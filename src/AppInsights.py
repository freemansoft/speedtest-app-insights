#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2022 Joe Freeman joe@freemansoft.com
#
# SPDX-License-Identifier: MIT
#
#
# Build metrics from the data reported by speedtest and passed in.
# Can also enable a logger to export logs to Application Insights
#
#
# This code is a useful example but is
# hardcoded to specific fields when called as a function library
import configparser
import json

# OpenCensus Log capture and Application Insights via logger
import logging
import os
from datetime import datetime

# Import the `configure_azure_monitor()` function from the
# `azure.monitor.opentelemetry` package.
from azure.monitor.opentelemetry import configure_azure_monitor

# Import the tracing api from the `opentelemetry` package.
from opentelemetry import environment_variables, metrics, trace
from opentelemetry.metrics import Meter

# https://opentelemetry-python.readthedocs.io/en/latest/sdk/metrics.view.html
from opentelemetry.sdk.metrics.view import View as SdkView
from opentelemetry.trace import Tracer

# log_prefix = os.path.basename(__file__) + ":"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# The azure library logging is at INFO which would then send it to Azure
# if log capture is enabled
logging.getLogger("azure").setLevel(level=logging.WARNING)
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(
    level=logging.WARNING
)

# keys in the key map must also be in the view dimensions/columns to be
# exposed as customDimensions
tag_key_isp = "client_isp"
tag_key_server_host = "server_host"


def load_insights_key() -> str:
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
def register_azure_monitor(
    azure_connection_string: str,
    cloud_role_name: str,
    capture_logs: bool = False,
) -> None:
    # From <https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-configuration?tabs=python> # noqa: E501
    # Cloud Role Name
    #    uses service.namespace and service.name attributes,
    #    it falls back to service.name if service.namespace isn't set.
    #    Note: is ${service.namespace}.${service.name} if both exist
    # Cloud Role Instance
    #   uses the service.instance.id attribute value.
    os.environ["OTEL_RESOURCE_ATTRIBUTES"] = f"service.name={cloud_role_name}"
    # In case you wanted to be even more confused, you can instead use
    # OTEL_SERVICE_NAME instead of OTEL_RESOURCE_ATTRIBUTES: service.name
    #
    # Disable exporters by setting these variables to "none"
    #
    # Netchecks
    # 7 items logged with or without integrations enabled
    if not capture_logs:
        os.environ[environment_variables.OTEL_LOGS_EXPORTER] = "none"
    # NetChecks
    # 4 traces logged , 6 if integrations are enabled
    # os.environ[environment_variables.OTEL_TRACES_EXPORTER] = "none"
    # NetChecks
    # 3 metrics logged, 5 if integrations are enabled
    # os.environ[environment_variables.OTEL_METRICS_EXPORTER] = "none"
    #
    # Traces can be sampled, We want all our traces.
    # os.environ["OTEL_TRACES_SAMPLER_ARG"]=1.0

    # Upload and download operations involve multiple HTTP packets which
    # are all captured as metrics, traces and logs if we leave
    # the urllib integration enabled
    os.environ["OTEL_PYTHON_DISABLED_INSTRUMENTATIONS"] = (
        "azure_sdk,django,fastapi,flask,psycopg2,urllib,urllib3"
    )

    # not sure what value to put here
    # os.environ[environment_variables.LOGGER_NAME_ARG] = "__name__"

    # we accept the default aggregator which is last value for gauges
    # instrument_name are all lower case in OT - mixed case is toLowerCase()
    # name are the view name which can be mixed case with spaces
    _st_servers_time_view = SdkView(
        instrument_name="st_servers_time",
        name="ST Servers Time",
        description="get servers",
    )
    _st_best_servers_time_view = SdkView(
        instrument_name="st_best_servers_time",
        name="ST Best Servers Time",
        description="get best servers",
    )
    _st_ping_time_view = SdkView(
        instrument_name="st_ping_time",
        name="ST Ping Time",
        description="last ping",
    )
    _upload_view = SdkView(
        instrument_name="st_upload_rate",
        name="ST Upload Rate",
        description="last upload",
    )
    _download_view = SdkView(
        instrument_name="st_download_rate",
        name="ST Download Rate",
        description="last download",
    )

    _st_dns_min_view = SdkView(
        instrument_name="st_dns_min",
        name="ST DNS Min",
        description="DNS ping min time",
    )
    _st_dns_avg_view = SdkView(
        instrument_name="st_dns_avg",
        name="ST DNS Avg",
        description="DNS ping average time",
    )
    _st_dns_max_view = SdkView(
        instrument_name="st_dns_max",
        name="ST DNS Max",
        description="DNS ping max time",
    )
    _st_dns_stddev_view = SdkView(
        instrument_name="st_dns_stdavg",
        name="ST DNS StdDev",
        description="DNS ping standard deviation",
    )

    configure_azure_monitor(
        connection_string=azure_connection_string,
        disable_offline_storage=True,
        views=[
            _st_servers_time_view,
            _st_best_servers_time_view,
            _st_ping_time_view,
            _upload_view,
            _download_view,
            _st_dns_min_view,
            _st_dns_avg_view,
            _st_dns_max_view,
            _st_dns_stddev_view,
        ],
    )


# Returns a meter that gauges can be connected to
def create_ot_meter(meter_name: str, azure_connection_string: str) -> Meter:
    meter = metrics.get_meter_provider().get_meter(name=meter_name)
    return meter


# Returns an OpenTelemetry Tracer that is bound to Azure Application Insights
def create_ot_tracer() -> Tracer:
    # Get a tracer for the current module.
    tracer = trace.get_tracer(__name__)
    return tracer


# Create dictionary that can be tied to ot metrics
def _create_ot_attributes(metrics_info):  # -> dict[str, Any]:
    attributes = {
        tag_key_isp: metrics_info["client"]["isp"],
        tag_key_server_host: metrics_info["server"]["host"],
    }
    return attributes


# return: measurement map - primarily for testing
def push_azure_speedtest_metrics(json_data, azure_connection_string):

    meter = create_ot_meter(
        meter_name="SpeedTest", azure_connection_string=load_insights_key()
    )

    # perf data gathered while running the test
    get_servers_gauge = meter.create_gauge(
        name="ST_Servers_Time",
        unit="ms",
        description="Amount of time it took to get_servers()",
    )
    get_best_servers_gauge = meter.create_gauge(
        name="ST_Best_Servers_Time",
        unit="ms",
        description="Amount of time it toook to get_best_servers()",
    )
    # metrics always returned from the test
    ping_gauge = meter.create_gauge(
        name="ST_Ping_Time",
        unit="ms",
        description="The latency in milliseconds per ping check",
    )
    upload_gauge = meter.create_gauge(
        name="ST_Upload_Rate",
        unit="Mbps",
        description="Upload speed in megabits per second",
    )
    download_gauge = meter.create_gauge(
        name="ST_Download_Rate",
        unit="Mbps",
        description="Download speed in megabits per second",
    )

    run_attributes = _create_ot_attributes(json_data)

    get_servers_gauge.set(
        amount=round(number=float(json_data["get_servers"]), ndigits=3),
        attributes=run_attributes,
    )
    get_best_servers_gauge.set(
        amount=round(number=float(json_data["get_best_servers"]), ndigits=3),
        attributes=run_attributes,
    )
    ping_gauge.set(
        amount=round(number=float(json_data["ping"]), ndigits=3),
        attributes=run_attributes,
    )
    if json_data["upload"] != 0:
        upload_gauge.set(
            amount=round(number=float(json_data["upload"]), ndigits=3),
            attributes=run_attributes,
        )
    else:
        logger.info("no upload stats to report")
    if json_data["download"] != 0:
        download_gauge.set(
            amount=round(number=float(json_data["download"]), ndigits=3),
            attributes=run_attributes,
        )
    else:
        logger.info("no download stats to report")


def push_azure_dns_metrics(
    ping_min: float, ping_average: float, ping_max: float, ping_stddev: float
):
    meter = create_ot_meter(
        meter_name="DNSTest", azure_connection_string=load_insights_key()
    )

    # perf data gathered while running the test
    ping_min_measure = meter.create_gauge(
        name="ST_DNS_Min",
        unit="ms",
        description="Minimum DNS Time",
    )
    ping_max_measure = meter.create_gauge(
        name="ST_DNS_Max",
        unit="ms",
        description="Maximum DNS Time",
    )
    ping_avg_measure = meter.create_gauge(
        name="ST_DNS_Avg",
        unit="ms",
        description="Average DNS Time",
    )
    ping_stddev_measure = meter.create_gauge(
        name="ST_DNS_StdDev",
        unit="ms",
        description="Standard Deviation DNS Time",
    )

    # could create attributes here
    ping_min_measure.set(amount=round(number=ping_min, ndigits=3))
    ping_avg_measure.set(amount=round(number=ping_average, ndigits=3))
    ping_max_measure.set(amount=round(number=ping_max, ndigits=3))
    ping_stddev_measure.set(amount=round(number=ping_stddev, ndigits=3))


# Used for testing this class - verify by lookin gin App Insights
# Only consumes sample data.  Do not use in REAL app
def AppInsightsMain():
    # sample speedtest.net output json as a string
    sample_string = (
        '{"download": 93579659.45913646, '
        '"upload": 94187295.64264823, "ping": 40.125, '
        '"server": '
        '{"url": "http://speedtest.red5g.com:8080/speedtest/upload.php", '
        '"lat": "38.9047", "lon": "-77.0164", '
        '"name": "Washington, DC", "country": "United States", "cc": "US", '
        '"sponsor": "red5g.com", "id": "30471", '
        '"host": "speedtest.red5g.com:8080", "d": 23.71681279068988, '
        '"latency": 9.125}, "timestamp": "2021-03-01T13:18:16.460145Z", '
        '"bytes_sent": 117825536, "bytes_received": 117376482, "share": null, '
        '"client": {"ip": "108.48.69.33", "lat": "39.0828", "lon": "-77.1674",'
        '"isp": "Verizon Fios", "isprating": "3.7", "rating": "0",'
        ' "ispdlavg": "0", "ispulavg": "0", "loggedin": "0", "country": "US"}}'
    )

    sample_dict = json.loads(sample_string)
    mmap = push_azure_speedtest_metrics(sample_dict)

    # manual visual verification - should be only if verbose
    metrics = list(mmap.measure_to_view_map.get_metrics(datetime.utcnow()))
    logger.info("first metric %s", metrics[0].time_series[0].points[0])


if __name__ == "__main__":
    AppInsightsMain()
