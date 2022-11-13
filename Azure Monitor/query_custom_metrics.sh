# quick demo that we can query for metrics

if [ ! -f api_config.ini ]; then
    echo "run generate_config.sh to create API keys"
    exit -1
fi
source ./api_config.ini

# other queries
# customMetrics | where name == "ST Ping Time" |  top 10 by timestamp desc
# customMetrics | where name == "ST Download Rate" or name == "ST Upload Rate" | order by timestamp desc
# customMetrics | summarize totalTime=sum(value) by name, bin(timestamp, 30m) | render timechart
# customMetrics | where name == "ST Ping Time" | where timestamp > ago(4d) | summarize min(value), avg(value), max(value) by cloud_RoleInstance
# dependencies | where name == "main" |  top 10 by timestamp desc
# dependencies | summarize totalCount=sum(itemCount) by bin(timestamp, 30m) | render timechart
# dependencies | summarize totalCount=sum(itemCount) by name, bin(timestamp, 30m) | render timechart

# these strings were encoded by pasting into the chrome browser address bar.
customMetricsTop10="customMetrics%20|%20top%2010%20by%20timestamp%20desc"
customMetricsPing='customMetrics+%7C+where+name+%3D%3D+"ST+Ping+Time"+%7C+top+10+by+timestamp+desc'
customMetricsPingByInstance='customMetrics+%7C+where+name+%3D%3D+"ST+Ping+Time"+%7C+where+timestamp+>+ago(4d)+%7C+summarize+min(value)%2C+avg(value)%2C+max(value)+by+cloud_RoleInstance'

curlString="https://api.applicationinsights.io/v1/apps/$appId/query?query=$customMetricsTop10&api_key=$apiKey"
curlString="https://api.applicationinsights.io/v1/apps/$appId/query?query=$customMetricsSTPing&api_key=$apiKey"
curlString="https://api.applicationinsights.io/v1/apps/$appId/query?query=$customMetricsPingByInstance&api_key=$apiKey"
# this has sensitive data in it so don't print this when making a video
#echo $curlString

# run without the progress bar
echo "========================"
echo "results"
metricsResults=$(curl -s $curlString)
echo $metricsResults
# results have multiple tables
# each table has an array of columns and rows
# {"tables":[{"name":"PrimaryResult","columns":[{"name":"cloud_RoleInstance","type":"string"},{"name":"min_value","type":"real"},{"name":"avg_value","type":"real"},{"name":"max_value","type":"real"}],"rows":[["pi-153a3987b",4.731,8.125820792647904,31.199],["Powerspec-g708",4.839,7.902727272727273,13.107],["fsi-7490-jf",6.339,7.389666666666667,9.19],["Joes-MBP.fios-router.home",9.677,9.9835,10.29]]}]}

echo "========================"
echo "columns names"
column_names=$(jq -c '.tables[0].columns[].name' <<< "$metricsResults")
echo "$column_names"

echo "========================"
echo "cloud instance stats"
cloud_instance_stats=$(jq -c '.tables[0].rows[]' <<< "$metricsResults")
echo "$cloud_instance_stats"

echo "========================"
echo "cloud instance names"
cloud_instance_names=$(jq '.[0]' <<< "$cloud_instance_stats")
echo $cloud_instance_names

