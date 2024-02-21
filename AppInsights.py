#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2022 Joe Freeman joe@freemansoft.com
#
# SPDX-License-Identifier: MIT
#
#
# Build metrics from the data reported by speedtest and passed in.
# Can also register a logger to export logs to Application Insights
#
#
# This code is a useful example but is
# hardcoded to specific fields when called as a function library
import configparser
import json

# OpenCensus Log capture and Application Insights via logger
import logging
from datetime import datetime

from opencensus.ext.azure import metrics_exporter
from opencensus.ext.azure.log_exporter import AzureLogHandler

# OpenCensus TraceCapture and Application Insights via Tracer
from opencensus.ext.azure.trace_exporter import AzureExporter

# OpenCensus Metrics and Azure Application Insights
from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import measure as measure_module
from opencensus.stats import stats as stats_module
from opencensus.stats import view as view_module
from opencensus.tags import tag_key as tag_key
from opencensus.tags import tag_map as tag_map
from opencensus.tags import tag_value as tag_value
from opencensus.trace.samplers import AlwaysOnSampler
from opencensus.trace.tracer import Tracer

# log_prefix = os.path.basename(__file__) + ":"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# keys in the key map must also be in the view dimensions/columns to be
# exposed as customDimensions
tag_key_isp = tag_key.TagKey("client_isp")
tag_key_server_host = tag_key.TagKey("server_host")


def load_insights_key():
    # Add support for a config.ini file
    config = configparser.ConfigParser()
    config.read("config.ini")
    config["azure"]
    logger.debug(
        "Instrumentation key: %s", config["azure"]["azure_instrumentation_key"]
    )
    return config["azure"]["azure_instrumentation_key"]


# call this if you want to send logs to Azure App Insight
# after this,
# every log(warn) will end up in azure as a log event "trace" !"tracing"
def register_azure_handler_with_logger(logger, azure_connection_string):
    logger.addHandler(
        AzureLogHandler(connection_string=azure_connection_string)
    )


# Call to get an OpenCensus Tracer that is bound to Azure Application Insights
def register_azure_exporter_with_tracer(azure_connection_string):
    tracer = Tracer(
        exporter=AzureExporter(connection_string=azure_connection_string),
        sampler=AlwaysOnSampler(),
    )
    return tracer


def _create_metric_measure(metric_name, metric_description, metric_unit):
    # The description of our metric
    measure = measure_module.MeasureFloat(
        metric_name, metric_description, metric_unit
    )
    return measure


def _record_metric_float(mmap, value, measure):
    # data from the speed test
    mmap.measure_float_put(measure, value)
    # the measure becomes the key to the measurement map
    logger.info(
        "metrics: %s value: %s number of measurements: %s ",
        measure.name,
        value,
        len(mmap.measurement_map),
    )


def _create_metric_view(view_manager, name, description, measure):
    # view must be registered prior to record
    ping_view = view_module.View(
        name=name,
        description=description,
        columns=[tag_key_isp, tag_key_server_host],
        measure=measure,
        aggregation=aggregation_module.LastValueAggregation(),
    )
    view_manager.register_view(ping_view)


# after this, everything sent to this view will end up in azure as a metric
def _register_azure_exporter_with_view_manager(
    view_manager, azure_connection_string
):
    # enable the Azure metrics exporter which talks to Azure
    # standard metrics are CPU, memory, storage, etc.
    exporter = metrics_exporter.new_metrics_exporter(
        enable_standard_metrics=False,
        connection_string=azure_connection_string,
    )
    view_manager.register_exporter(exporter)


# Record a single metric. Apply same tags to all metrics.
def _tag_and_record(mmap, metrics_info):
    # apply same tags to every metric in batch
    tag_value_isp = tag_value.TagValue(metrics_info["client"]["isp"])
    tag_value_server_host = tag_value.TagValue(metrics_info["server"]["host"])
    tagmap = tag_map.TagMap()
    tagmap.insert(tag_key_isp, tag_value_isp)
    tagmap.insert(tag_key_server_host, tag_value_server_host)
    logger.debug("tagmap: %s", tagmap.map)
    mmap.record(tagmap)


# return: measurement map - primarily for testing
def push_azure_speedtest_metrics(json_data, azure_connection_string):
    # standard opencensus and azure exporter setup
    stats = stats_module.stats
    view_manager = stats.view_manager
    stats_recorder = stats.stats_recorder
    mmap = stats_recorder.new_measurement_map()

    # perf data gathered while running tests
    get_servers_measure = _create_metric_measure(
        "get_servers_time", "Amount of time it took to get_servers()", "ms"
    )
    get_best_servers_measure = _create_metric_measure(
        "get_best_servers_time",
        "Amount of time it took to get_best_servers()",
        "ms",
    )
    # we measure 3 different things so lets describe them
    ping_measure = _create_metric_measure(
        "ping_time", "The latency in milliseconds per ping check", "ms"
    )
    upload_measure = _create_metric_measure(
        "upload_speed", "Upload speed in megabits per second", "Mbps"
    )
    download_measure = _create_metric_measure(
        "download_speed", "Download speed in megabits per second", "Mbps"
    )

    # we always monitor ping and optionally capture upload or download
    # add setup metrics
    _create_metric_view(
        view_manager=view_manager,
        name="ST Servers Time",
        description="get servers",
        measure=get_servers_measure,
    )
    _create_metric_view(
        view_manager=view_manager,
        name="ST Best Servers Time",
        description="get best servers",
        measure=get_best_servers_measure,
    )
    # the name is what you see in the Azure App Insights drop lists
    # https://github.com/census-instrumentation/opencensus-python/issues/1015
    _create_metric_view(
        view_manager=view_manager,
        name="ST Ping Time",
        description="last ping",
        measure=ping_measure,
    )
    if json_data["upload"] != 0:
        _create_metric_view(
            view_manager=view_manager,
            name="ST Upload Rate",
            description="last upload",
            measure=upload_measure,
        )
    if json_data["download"] != 0:
        _create_metric_view(
            view_manager=view_manager,
            name="ST Download Rate",
            description="last download",
            measure=download_measure,
        )

    # lets add the exporter and register our azure key with the exporter
    _register_azure_exporter_with_view_manager(
        view_manager, azure_connection_string
    )

    # views(measure, view)  events(measure,metric)
    # setup times
    _record_metric_float(mmap, json_data["get_servers"], get_servers_measure)
    _record_metric_float(
        mmap, json_data["get_best_servers"], get_best_servers_measure
    )
    # We always capture ping and sometimes upload or download
    _record_metric_float(mmap, json_data["ping"], ping_measure)
    if json_data["upload"] != 0:
        _record_metric_float(mmap, json_data["upload"], upload_measure)
    else:
        logger.info("no upload stats to report")
    if json_data["download"] != 0:
        _record_metric_float(mmap, json_data["download"], download_measure)
    else:
        logger.info("no download stats to report")

    # create our tags for these metrics -
    # record the metrics -
    # the exporter runs on a schedule
    # this will throw a 400 if the instrumentation key isn't set
    _tag_and_record(mmap, json_data)
    return mmap


def push_azure_dns_metrics(
    ping_min, ping_average, ping_max, ping_stddev, azure_connection_string
):
    # standard opencensus and azure exporter setup
    stats = stats_module.stats
    view_manager = stats.view_manager
    stats_recorder = stats.stats_recorder
    mmap = stats_recorder.new_measurement_map()

    # perf data gathered while running tests
    ping_min_measure = _create_metric_measure(
        "dns_min", "Minimum DNS time", "ms"
    )
    ping_avg_measure = _create_metric_measure(
        "dns_avg", "Average DNS time", "ms"
    )
    ping_max_measure = _create_metric_measure(
        "dns_max", "Maximum DNS time", "ms"
    )
    ping_stddev_measure = _create_metric_measure(
        "dns_stddev", "Standard Deviation DNS time", "ms"
    )

    # we always monitor ping and optionally capture upload or download
    # add setup metrics
    _create_metric_view(
        view_manager=view_manager,
        name="ST DNS Min",
        description="DNS ping min time",
        measure=ping_min_measure,
    )
    _create_metric_view(
        view_manager=view_manager,
        name="ST DNS Avg",
        description="DNS ping average time",
        measure=ping_avg_measure,
    )
    _create_metric_view(
        view_manager=view_manager,
        name="ST DNS Max",
        description="DNS ping max time",
        measure=ping_max_measure,
    )
    _create_metric_view(
        view_manager=view_manager,
        name="ST DNS StdDev",
        description="DNS ping standard deviation",
        measure=ping_stddev_measure,
    )

    # lets add the exporter and register our azure key with the exporter
    _register_azure_exporter_with_view_manager(
        view_manager, azure_connection_string
    )

    # views(measure, view)  events(measure,metric)
    _record_metric_float(mmap, ping_min, ping_min_measure)
    _record_metric_float(mmap, ping_average, ping_avg_measure)
    _record_metric_float(mmap, ping_max, ping_max_measure)
    _record_metric_float(mmap, ping_stddev, ping_stddev_measure)

    # could add tags here
    # this will throw a 400 if the instrumentation key isn't set
    mmap.record()
    return mmap


# Used for testing this class - verify by looking in App Insights
# Only consumes sample data.  Do not use in REAL app
def AppInsightsMain():
    # sample speedtest.net output json as a string
    sample_string = '{"download": 93579659.45913646, "upload": 94187295.64264823, "ping": 40.125, "server": {"url": "http://speedtest.red5g.com:8080/speedtest/upload.php", "lat": "38.9047", "lon": "-77.0164", "name": "Washington, DC", "country": "United States", "cc": "US", "sponsor": "red5g.com", "id": "30471", "host": "speedtest.red5g.com:8080", "d": 23.71681279068988, "latency": 9.125}, "timestamp": "2021-03-01T13:18:16.460145Z", "bytes_sent": 117825536, "bytes_received": 117376482, "share": null, "client": {"ip": "108.48.69.33", "lat": "39.0828", "lon": "-77.1674", "isp": "Verizon Fios", "isprating": "3.7", "rating": "0", "ispdlavg": "0", "ispulavg": "0", "loggedin": "0", "country": "US"}}'

    sample_dict = json.loads(sample_string)
    mmap = push_azure_speedtest_metrics(sample_dict)

    # manual visual verification - should be only if verbose
    metrics = list(mmap.measure_to_view_map.get_metrics(datetime.utcnow()))
    logger.info("first metric %s", metrics[0].time_series[0].points[0])


if __name__ == "__main__":
    AppInsightsMain()
