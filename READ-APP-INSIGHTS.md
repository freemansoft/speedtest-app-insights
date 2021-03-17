# Azure Appication Insights 
Python information can be sent to Azure Application Insights as Metrics, Traces or Logs.  
The data is actualy sent as events which means that it could appear in _Metrics_ as an _Aggregation_ and in _Logs_ as an individual event.

This program leverages the three types of telemetry supported for Python Applications.

| Telemetry sent with | Open Census Terms| Appears in Application Insights as |
| - | - | - | 
| Azure Monitor _trace exporter_  | trace and span | `dependencies` |
| Azure Monitor _metrics exporter_ | metrics | `customMetrics` |
| Azure Monitor _log exporter_ | Python logger | `traces` |

## Use Case
You can use the dash board to track your performance or compare the performance of different locations or providers

![Multi-Site](./images/speed-test-dual-site.png)

## Standard Dimensions sent to Application Insights via all exporters
_as of 3/2021_
The [azure exporter utils.py](https://github.com/census-instrumentation/opencensus-python/blob/master/contrib/opencensus-ext-azure/opencensus/ext/azure/common/utils.py) sends a fixed set of properties to Application Insights that can be used in charts for **filtering** or **splitting**
* Splitting is not supported on charts with multiple metrics. [See documentation](https://docs.microsoft.com/en-us/azure/azure-monitor/essentials/metrics-charts)

| Property Name | Populated With | Notes |
| - | - | - |
| Application Version | `undefined` | n/a |
| Authenticated User | `False` | n/a |
| Browser Version | `Python Requests n.n` | ? |
| City | location | ? | 
| Cloud Role Instance | **hostname** | platform.node() |
| Cloud Role Name | Python script name | sys.argv[0] |
| Country or Region | country | ? |
| Device Model | `other` | hard coded device.type |
| Device Type | `PC` | ? |
| Operating System | `#1333 SMP ...` | platform.version() part of `uname -a` |
| Operation Name | `undefined` | n/a |
| Real or synthetic traffic | `False` | ? |
| Source of synthetic traffic | `undefined` | n/a |
| State or Province | State | ? |

## Telemetry via metrics exporter 

### Structure in the OpenCensus API and Application Insights metrics exporter
This is _partially correct_ explanation of OpenCensus events and Azure bindings
1. The `measure` is a type definition that is used as a key to register both `metrics` and `views`
    1. The view list has `views` keyed by `measure`
    1. The events have `recordings` keyed by `measure`

### Metrics in AppInsight Dashboard
Metrics aggregations are visible as `metrics` in the Applicaton Insights under _Monitoring / Metrics _
1. `Home > Application Insights > _your resource_ ` 
1. Right side-bar `Monitoring` / `Metrics`

Individual _Metrics Events_ can also be seen under _Monitoring / Logs_
1. `Home > Application Insights > _your resource_ ` 
1. Right side-bar `Monitoring` / `Logs`

| Metric Namespace | SpeedTest Metric | Description |
| - | - | - |
| `Log Based Metrics` | `ST Ping Time` | ping time as reported by SpeedTest |
| `Log Based Metrics` | `ST Download Speed` | download speed as reported by SpeedTest |
| `Log Based Metrics` | `ST Upload Speed` | upload speed time as reported by SpeedTest |
| `Log Based Metrics` | `ST Servers Time` | initial SpeedTest setup call time |
| `Log Based metrics` | `ST Best Servers Time` | time it took to get 'best servers' from SpeedTest |


### Custom Dimensions
AppInsights.py adds a couple custom tags to the data. These show up as custom dimensions.  

* CustomDimensions can be seen on the query screen results pane as a combined json structure. 
* CustomDimensions must added explicitly to the results configuration
* CustomDimensions can be used to filter in gauges.

The speedtest program adds two `customDimension` properties

| Custom Dimension | Value |
| - | - |
| client_isp | client isp as reported by speedtest sdk |
| server_host | speedtest server host as reported by speedtest sdk | 

## Log output in Application Insight
The program can send a single line of output per run to the ApplicationInsights as `traces` in the Log export query screens

## Tracing and spans
The program sends trace exports via the OpenCensus `Trace and Span` APIs.

* You can find the custom nested span tracing in `dependencies` in the _Monitoring / Logs_
* You can use the _Performance_ dashboard to see span timing information. 
    * Drill down into an individual call chain by clicking on _Samples_ in the bottom right corner

**Sample Call Chain Queries**
Some derived from
*  https://social.msdn.microsoft.com/Forums/azure/en-US/7333f142-fe43-4efd-a6e4-e61f9078c145/azure-app-insights-join?forum=ApplicationInsights

All of the traces for some time window
```
dependencies
```

Length of time each test took including number of spans created in that test
```
// the number of buckets for each operation id and how long the outside span took
dependencies
| summarize max=max(duration) , NumSpans=count() by operation_Id
```
Performance statistics for running the entire test comparing the performance with upload/download vs not
```
// Metrics for when we do downloads and when we don't
// 1. for each span Id find the longest which is actually the outer span
// 2. for each pool 3/5 and role instance 
// this assumes that we run no up/down or both up/down  It is broken if sometimes up and sometimes down
dependencies
| summarize OuterSpanTime=max(duration) , NumSpans=count() by operation_Id, cloud_RoleInstance
| summarize average_OuterSpanTime = avg(OuterSpanTime), percentiles(OuterSpanTime, 0, 50,95,99) by cloud_RoleInstance, NumSpans
```

Query taken from dashboard that provides stats on each individual span type
```
// this query calculates dependency duration percentiles and count by target
let start=datetime("2021-03-15T01:18:00.000Z");
let end=datetime("2021-03-16T01:18:00.000Z");
let timeGrain=5m;
let dataset=dependencies
    // additional filters can be applied here
    | where timestamp > start and timestamp < end
    | where client_Type != "Browser"
;
dataset
// change 'target' on the below line to segment by a different property
| summarize count_=sum(itemCount), avg(duration), percentiles(duration, 50, 95, 99) by target
// calculate duration percentiles and count for all dependencies (overall)
| union(dataset
    | summarize count_=sum(itemCount), avg(duration), percentiles(duration, 50, 95, 99)
    | extend operation_Name="Overall")
| order by count_ desc
```
