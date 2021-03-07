#!/usr/bin/env python3
#
# This code is a useful example but is hardcoded to specific fields when called as a function library
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

def create_metric_measure( metric_name, metric_description, metric_unit):
    # The description of our metric
    measure = measure_module.MeasureFloat(metric_name, metric_description, metric_unit)
    return measure
    
def record_metric_float(mmap,value,measure):
    # data from the speed test
    mmap.measure_float_put(measure,value)
    # the measure becomes the key to the measurement map
    print(log_prefix,"metrics: ",measure.name, "value:", value, "number of measurements:",len(mmap.measurement_map))

def create_metric_view(view_manager, name, description, measure):
    # view must be registered prior to record
    ping_view = view_module.View(name=name,
                               description= description,
                               columns=[tag_key_isp,tag_key_server_host],
                               measure=measure,
                               aggregation=aggregation_module.LastValueAggregation())
    view_manager.register_view(ping_view)

def push_speedtest_metrics(json_data):
    azure_instrumentation_key = load_insights_key()
    # standard opencensus and azure exporter setup    
    stats = stats_module.stats
    view_manager = stats.view_manager
    stats_recorder = stats.stats_recorder
    mmap = stats_recorder.new_measurement_map()
    
    # perf data gathered while running tests
    get_servers_measure = create_metric_measure("get_servers_time", "Amount of time it took to get_servers()", "ms")
    get_best_servers_measure = create_metric_measure("get_best_servers_time", "Amount of time it took to get_best_servers()", "ms")
    # we measure 3 different things so lets describe them
    ping_measure = create_metric_measure("ping_time", "The latency in milliseconds per ping check", "ms")
    upload_measure = create_metric_measure("upload_speed", "Upload speed in megabits per second", "Mbps")
    download_measure = create_metric_measure("download_speed", "Download speed in megabits per second", "Mbps")

    # we always monitor ping and optionally capture upload or download
    # add setup metrics
    create_metric_view(view_manager=view_manager, name="ST Servers Time", description="get servers", measure=get_servers_measure)
    create_metric_view(view_manager=view_manager, name="ST Best Servers Time", description="get best servers", measure=get_best_servers_measure)
    # the name is what you see in the Azure App Insights drop lists 
    # https://github.com/census-instrumentation/opencensus-python/issues/1015
    create_metric_view(view_manager=view_manager, name="ST Ping Time", description="last ping", measure=ping_measure)
    if (json_data['upload'] != 0):
        create_metric_view(view_manager=view_manager, name="ST Upload Rate", description="last upload", measure=upload_measure)
    if (json_data['download']!=0):
        create_metric_view(view_manager=view_manager, name="ST Download Rate", description="last download", measure=download_measure)

    # lets add the exporter and register our azure key with the exporter
    register_azure_metrics(view_manager,azure_instrumentation_key)

    # views(measure, view)  events(measure,metric)
    # setup times
    record_metric_float(mmap, json_data['get_servers'], get_servers_measure)
    record_metric_float(mmap, json_data['get_best_servers'], get_best_servers_measure)
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
    print(log_prefix,"tagmap:", tagmap.map)
    mmap.record(tagmap)

# Only consumes sample data.  Do not use in REAL app
def main():
    sample_dict = json.loads(sample_string)
    mmap = push_speedtest_metrics(sample_dict)

    # manual visual verification - should be only if verbose
    metrics = list(mmap.measure_to_view_map.get_metrics(datetime.utcnow()))
    print(log_prefix,"first metric", metrics[0].time_series[0].points[0])

if __name__ == "__main__":
    main()