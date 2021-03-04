#!/usr/bin/env python3

from datetime import datetime
import json
import configparser
import os
from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import measure as measure_module
from opencensus.stats import stats as stats_module
from opencensus.stats import view as view_module
from opencensus.tags import tag_key as tag_key
from opencensus.tags import tag_map as tag_map
from opencensus.tags import tag_value as tag_value
from opencensus.ext.azure import metrics_exporter

log_prefix = os.path.basename(__file__) + ":"

# sample speedtest.net output json as a string
sample_string = "{\"download\": 93579659.45913646, \"upload\": 94187295.64264823, \"ping\": 40.125, \"server\": {\"url\": \"http://speedtest.red5g.com:8080/speedtest/upload.php\", \"lat\": \"38.9047\", \"lon\": \"-77.0164\", \"name\": \"Washington, DC\", \"country\": \"United States\", \"cc\": \"US\", \"sponsor\": \"red5g.com\", \"id\": \"30471\", \"host\": \"speedtest.red5g.com:8080\", \"d\": 23.71681279068988, \"latency\": 9.125}, \"timestamp\": \"2021-03-01T13:18:16.460145Z\", \"bytes_sent\": 117825536, \"bytes_received\": 117376482, \"share\": null, \"client\": {\"ip\": \"108.48.69.33\", \"lat\": \"39.0828\", \"lon\": \"-77.1674\", \"isp\": \"Verizon Fios\", \"isprating\": \"3.7\", \"rating\": \"0\", \"ispdlavg\": \"0\", \"ispulavg\": \"0\", \"loggedin\": \"0\", \"country\": \"US\"}}"

# keys in the key map must also be in the view dimensions/columns to be exposed as customDimensions
tag_key_isp = tag_key.TagKey("client_isp")
tag_key_server_host = tag_key.TagKey("server_host")

def load_insights_key():
    # Add support for a config.ini file
    config = configparser.ConfigParser()
    config.read('config.ini')
    config['azure']
    #print(log_prefix, config['azure']['azure_instrumentation_key'])
    return config['azure']['azure_instrumentation_key']

def register_azure_metrics(view_manager, azure_connection_string):
    # enable the Azure metrics exporter which talks to Azure
    exporter = metrics_exporter.new_metrics_exporter(
        enable_standard_metrics=False,
        connection_string=azure_connection_string)
    view_manager.register_exporter(exporter)

def make_measure_float( metric_name, metric_description, metric_unit):
    # The description of our metric
    measure = measure_module.MeasureFloat(metric_name, metric_description, metric_unit)
    return measure
    
def record_metric_float(mmap,value,measure):
    # data from the speed test
    mmap.measure_float_put(measure,value)
    # the measure becomes the key to the measurement map
    print(log_prefix,"metrics: ",measure.name, "measure:", measure, "measurement map:",mmap.measurement_map)

def make_view_float(view_manager, name, description, measure):
    # view must be registered prior to record
    ping_view = view_module.View(name=name,
                               description= description,
                               columns=[tag_key_isp,tag_key_server_host],
                               measure=measure,
                               aggregation=aggregation_module.LastValueAggregation())
    view_manager.register_view(ping_view)

def record_speedtest(json_data):
    azure_instrumentation_key = load_insights_key()
    # standard opencensus and azure exporter setup    
    stats = stats_module.stats
    view_manager = stats.view_manager
    stats_recorder = stats.stats_recorder
    mmap = stats_recorder.new_measurement_map()
    
    # we measure 3 different things so lets describe them
    ping_measure = make_measure_float("ping_time", "The latency in milliseconds per ping check", "ms")
    upload_measure = make_measure_float("upload_speed", "Upload speed in megabits per second", "Mbps")
    download_measure = make_measure_float("download_speed", "Download speed in megabits per second", "Mbps")

    # we always monitor ping and optionally capture upload or download
    # the name is what you see in the Azure App Insights drop lists 
    # https://github.com/census-instrumentation/opencensus-python/issues/1015
    make_view_float(view_manager=view_manager, name="ST Ping Time", description="last ping", measure=ping_measure)
    if (json_data['upload'] != 0):
        make_view_float(view_manager=view_manager, name="ST Upload Rate", description="last upload", measure=upload_measure)
    if (json_data['download']!=0):
        make_view_float(view_manager=view_manager, name="ST Download Rate", description="last download", measure=download_measure)

    # lets add the exporter and register our azure key with the exporter
    register_azure_metrics(view_manager,azure_instrumentation_key)

    # We always capture ping and sometimes upload or download
    record_metric_float(mmap, json_data['ping'], ping_measure)
    if (json_data['upload'] != 0):
        record_metric_float(mmap, json_data['upload'], upload_measure)
    else:
        print(log_prefix,"no upload stats to report")
    if (json_data['download']!=0):
        record_metric_float(mmap, json_data['download'], download_measure)
    else:
        print(log_prefix,"no download stats to report")

    # create our tags for these metrics - record the metrics - the exporter runs on a schedule
    # this will throw a 400 if the instrumentation key isn't set
    tag_and_record(mmap,json_data)
    return mmap

# Record a single metric. Apply same tags to all metrics.
def tag_and_record(mmap, metrics_info):
    # apply same tags to every metric in batch
    tag_value_isp= tag_value.TagValue(metrics_info['client']['isp'])
    tag_value_server_host= tag_value.TagValue(metrics_info['server']['host'])
    tagmap = tag_map.TagMap()
    tagmap.insert(tag_key_isp,tag_value_isp)
    tagmap.insert(tag_key_server_host, tag_value_server_host)
    print(log_prefix,"tagmap", tagmap)
    mmap.record(tagmap)

# Only consumes sample data.  Do not use in REAL app
def main():
    sample_dict = json.loads(sample_string)
    mmap = record_speedtest(sample_dict)

    # manual visual verification - should be only if verbose
    metrics = list(mmap.measure_to_view_map.get_metrics(datetime.utcnow()))
    print(log_prefix,"first metric", metrics[0].time_series[0].points[0])

if __name__ == "__main__":
    main()