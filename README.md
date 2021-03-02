This document will eventually describe how to use your Pi an internet health monitor.

## Intention
The intention is to 
1. Capture the current internet health with the `speedtest` CLI.
1. Publish the results to an Azure Application Insights dashboard

## Usage - NetCheck and Azure App Insights
1. Copy config.ini.template to config.ini
1. Register in Application Insights to get a key
1. Replace the dummy key in config.ini with yoru new key
1. Run `NetCheck.py`
  1. Run with only a ping check `python3 NetCheck.py `
  1. Run with ping, upload and download `python3 NetCheck.py --download --upload`
  1. Get help with `NetCheck.py --help`

## Example speedtest.net cli output
Raspberry Pi3 on 1GB port on 1GB FIOS internet service. A Raspberry Pi3 seems to have a max ethernet speed of 100Mbit/s

### speedtest installed as part of apt package
Installed in /usr/bin
```
pi@pi-52863f1:~/Documents/speedtest-app-insights $  /usr/bin/speedtest

   Speedtest by Ookla

     Server: Windstream - Ashburn, VA (id = 17383)
        ISP: Verizon Fios
    Latency:     4.04 ms   (0.04 ms jitter)
   Download:    94.19 Mbps (data used: 42.4 MB)                               
     Upload:    93.90 Mbps (data used: 42.3 MB)                               
Packet Loss:     0.0%
 Result URL: https://www.speedtest.net/result/c/dee19d27-1f5a-4cff-aa42-d8084a145b8f
```

### speedtest installed as part of speedtest-cli gitpull
Installed in ~/.local/bin
```
$ speedtest
Retrieving speedtest.net configuration...
Testing from Verizon Fios (108.48.69.33)...
Retrieving speedtest.net server list...
Selecting best server based on ping...
Hosted by PBW Communications, LLC (Herndon, VA) [22.70 km]: 8.306 ms
Testing download speed................................................................................
Download: 91.92 Mbit/s
Testing upload speed......................................................................................................
Upload: 93.90 Mbit/s
```

## References
* https://github.com/sivel/speedtest-cli
* https://docs.microsoft.com/en-us/azure/azure-monitor/app/opencensus-python
* https://docs.microsoft.com/en-us/azure/azure-monitor/app/create-new-resource
* https://github.com/census-instrumentation/opencensus-python/tree/master/contrib/opencensus-ext-azure

## Scripts
| Script | Purpose |
| - | - |
| setup.sh | downloads the Speedtest.net CLI, configures Python |
| NetCheck.py | Program that runs the speedtest-cli and records metrics |
| AppInsights.py | OpenCensus library wrapper used to send metrics to Azure Application Insights | 
