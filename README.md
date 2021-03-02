This document will eventually describe how to use your Pi an internet health monitor.

## Intention
The intention is to 
1. Capture the current internet health with the `speedtest` CLI.
1. Publish the results to an Azure Application Insights dashboard

## Usage - NetCheck and Azure App Insights
1. Copy config.ini.template to config.ini
1. Register in Application Insights to get a key
1. Replace the dummy key in config.ini with yoru new key
1. Run with only a ping check `python3 NetCheck.py `
1. Run with ping, upload and download `python3 NetCheck.py --download --upload`

## Example speedtest.net cli output
Raspberry Pi3 on 1GB port on 1GB FIOS internet service. A Raspberry Pi3 seems to have a max ethernet speed of 100Mbit/s

```
pi@pi-52863f1:~/Documents/RaspberryPi $ speedtest NetCheck --download --upload

   Speedtest by Ookla

     Server: Windstream - Ashburn, VA (id = 17383)
        ISP: Verizon Fios
    Latency:     4.46 ms   (1.35 ms jitter)
   Download:    95.44 Mbps (data used: 61.2 MB)
     Upload:    93.90 Mbps (data used: 42.3 MB)
Packet Loss:     0.0%
 Result URL: https://www.speedtest.net/result/c/6e405b18-6135-4608-91a0-0da5e8e1cf58
```

## References
* https://github.com/sivel/speedtest-cli
* https://docs.microsoft.com/en-us/azure/azure-monitor/app/opencensus-python
* https://docs.microsoft.com/en-us/azure/azure-monitor/app/create-new-resource

## Scripts
| Script | Purpose |
| - | - |
| setup.sh | downloads the Speedtest.net CLI, configures Python |
| AppInsights | ?? | 