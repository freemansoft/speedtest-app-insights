# quick demo that we can query for metrics

source ./instance_config.sh
source ./api_config.ini

# these strings were encoded by pasting into the chrome browser address bar.
customMetricsTop10="customMetrics%20|%20top%2010%20by%20timestamp%20desc"
customMetricsSTPingTime='customMetrics+%7C+where+name+%3D%3D+"ST+Ping+Time"+%7C+top+10+by+timestamp+desc'

# https://learn.microsoft.com/en-us/rest/api/application-insights/query/get?tabs=HTTP
curlString="https://api.applicationinsights.io/v1/apps/$appId/query?query=$customMetricsTop10&api_key=$apiKey"
curlString="https://api.applicationinsights.io/v1/apps/$appId/query?query=$customMetricsSTPingTime&api_key=$apiKey"

#echo $curlString
# run without the progress bar
metricsResults=$(curl -s $curlString)
echo "$metricsResults"

# other queries
# customMetrics | where name == "ST Ping Time" |  top 10 by timestamp desc
# customMetrics | where name == "ST Download Rate" or name == "ST Upload Rate" | order by timestamp desc
# customMetrics | summarize totalTime=sum(value) by name, bin(timestamp, 30m) | render timechart
#
# dependencies | where name == "main" |  top 10 by timestamp desc
# dependencies | summarize totalCount=sum(itemCount) by bin(timestamp, 30m) | render timechart
# dependencies | summarize totalCount=sum(itemCount) by name, bin(timestamp, 30m) | render timechart
