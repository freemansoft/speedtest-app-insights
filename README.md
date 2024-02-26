# Capturing speedtest.net data in Azure App Insights

The labels for the open telemtry version are those than from the privous version.  They are **lower case** and have **spaces repalced with underscores**

## Purpose

This project captures internet connection statistics and sends them to an Azure dashboard.

![Script Flow](./images/NetCheck-AppInsights.png)

1. Capture the current ping time and optionally upload/doownload statistics of the internet connection for the machine this machine runs on as measured by the `speedtest.net` python API
1. Publish the results to an Azure Application Insights dashboard

![Application Insights Dashboard](./images/App-Insights-Dashboard.png)

## Prerequisites

1. Python3
1. An internet connection
1. An account in Azure that can run the free tier of _Azure Application Insights_.  See references below for instructions.
    1. You can comment out the `AppInsights.py` call at the bottom of `NetCheck.py` if you don't wish to create a dashboard in _Azure Application Insights_

## TODO

1. Create IaC script that instantiates Application Insights so you don't have to use [Azure Portal](https://portal.azure.com)
1. Create a script for the Mac that runs `Install Certificates.command`

## Issues

1. speedtest.net initialization can vary by platorm. Some machines require https and some don't work with it
    1. Some Windows WSL environments require `s = speedtest.Speedtest(secure=1)`
    1. The Mac with python 3.10 gets a cert error.  `CERTIFICATE_VERIFYFAILED`  Two options
        * Fix the certificate by running the `Install Certificates.command`  Double click on `/Applications/<python version>/Install Certificates.command`
        * Disable `secure` with this code change `s = speedtest.Speedtest(secure=0)`

## Scripts in this repository

| Script                        | Purpose                                                                        |
| ----------------------------- | ------------------------------------------------------------------------------ |
| Linux/Pi Setup / Installation |                                                                                |
| 1-setup-host.sh               | downloads the Speedtest.net CLI, configures Python                             |
| 2-install-crontab.sh          | Installs a crontab entry that runs NetCheck.py on a regular basis              |
| 11-remove-crontab.sh          | removes this user's NetCheck.py crontab entries                                |
| Network testing binaries      |                                                                                |
| NetCheck.py                   | The main program. Program that invokes the test code in SpeedTest.py           |
| SpeedTest.py                  | SpeedTest.net adapter. Runs the speedtest-cli and records metrics              |
| AppInsights.py                | OpenCensus library wrapper used to send metrics to Azure Application Insights  |
| Windows Python Setup          |                                                                                |
| setup.ps1                     | Windows Python setup program. Will prompt to install python3 via Windows store |

## Usage - NetCheck and Azure App Insights

1. Run `1-setup-host.sh` to install dependencies on a raspberry pi
    1. Alternative for like a windows machine `pip3 install -r requirements.txt` or `python3 -m pip install -r requirements.txt`
1. Create Application Inights and get key
    1. Get an Azure account
    1. Log into [Azure Portal Insights blade](https://portal.azure.com/#blade/HubsExtension/BrowseResource/resourceType/microsoft.insights%2Fcomponents)
    1. Register in [Application Insights](https://portal.azure.com/#create/Microsoft.AppInsights)
        1. Select your subscription
        1. Create a resource group or use an existing one
        1. Select an instance name.
        1. Select a Region.
        1. Select _Resource Mode_ as a _Workspace-based.
        1. Select the Log Analytics Workspace. There is a DefaultWorkspace in each region. You can use that.
    1. Get an Application Insights _Instrumentation Key_ from the Portal.  It is on the Application Insights home page in the upper right corner.
        1. Open the [Application Insights blade](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/microsoft.insights%2Fcomponents)
        1. Copy the `Connection String` in the upper right corder
    1. Copy config.ini.template to config.ini
    1. Replace the dummy key in config.ini with your new key that you copied from the portal above.  It should look something like

    ```json
    azure_instrumentation_key=InstrumentationKey=0000000-0000-0000-0000-00000000000;IngestionEndpoint=https://westus2-1.in.applicationinsights.azure.com/
    ```

1. Run main program `NetCheck.py` There are several options
    1. Run with only a ping check `python3 NetCheck.py`
    1. Run with ping, upload and download `python3 NetCheck.py --download --upload`
    1. Get help with `NetCheck.py --help`

### Optional

1. Manage data retention  [the data retention period](https://docs.microsoft.com/en-us/azure/azure-monitor/app/pricing#change-the-data-retention-period). Learn [how long data is kept](https://docs.microsoft.com/en-us/azure/azure-monitor/app/data-retention-privacy).

### Installing in crontab to run repeately

1. cd into this directory
1. Verify the cycle times you wish in `2-install-crontab.sh`.  The file is in crontab format.
1. run `2-install-crontab.sh`

## Example speedtest.net cli output

Raspberry Pi3 on 1GB port on 1GB FIOS internet service.

### speedtest installed as part of apt package

Installed in /usr/bin

```bash
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

### speedtest installed as part of speedtest-cli github pull

Installed in ~/.local/bin

```bash
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

## Application Insights

See [Application Insights Readme](READ-APP-INSIGHTS.md)

## Raspberry Pi Networking

Some Raspberry Pi models are speed limited on their ethernet. magpi posted [ethernet test results](https://magpi.raspberrypi.org/articles/raspberry-pi-4-specs-benchmarks)

* In my testing, the Raspberry Pi 3 hardwire Ethernet seems to max out about 94 Mbit/s. The Raspberry Pi speed should be sigficantly higher because its eithernet interface is part of the SoC instead of being USB attached like previous boards.
* My results align with numbers in this blog article <https://www.jeffgeerling.com/blogs/jeff-geerling/getting-gigabit-networking> . The same article says you can get slightly over 200 Mbit/s with a USB 3.0 Gigabit adapter.
* This site shows Raspberry Pi 3 and Pi 4 speeds. Note that the Pi3 speeds on this page are higher than other reference sites [Hackaday Raspberry Pi Benchmarks](https://hackaday.com/2019/07/10/raspberry-pi-4-benchmarks-processor-and-network-performance-makes-it-a-real-desktop-contender/)

## References

* Speedtest Python library
  * <https://github.com/sivel/speedtest-cli>
* Azure App Insights docs
  * <https://docs.microsoft.com/en-us/azure/azure-monitor/app/create-workspace-resource>
  * <https://docs.microsoft.com/en-us/azure/azure-monitor/app/opencensus-python>
  * <https://docs.microsoft.com/en-us/azure/azure-monitor/app/create-new-resource>
* App Insights Open Census Python exporter
  * <https://github.com/census-instrumentation/opencensus-python/tree/master/contrib/opencensus-ext-azure>
  * <https://github.com/census-instrumentation/opencensus-python/blob/master/contrib/opencensus-ext-azure/opencensus/ext/azure/common/utils.py>
* Azure Dashboard
  * <https://portal.azure.com/#blade/HubsExtension/BrowseResource/resourceType/microsoft.insights%2Fcomponents>

## Experimental Features

### DnsCheck.py

This module uses dnspython to do a dns check. I found that my network experience was heavily driven by my DNS times.

It should install fine but you can see in 1-setup-host.sh that there is a bit of overhead to get this working
because it depends on a library that is best installed from git.

## Release Notes

The speed test team changes something in their API in April 2021.
This changed some format that broke speedtest.py.  You need the 2.1.3 version, or later, of the speedtest.  Grab it with pip3 or if not available then the following assuming you run pip not as root

```bash
wget https://raw.githubusercontent.com/sivel/speedtest-cli/v2.1.3/speedtest.py -O ~/.local/lib/python3.<version>/site-packages/speedtest.py
```

Ex:

```bash
wget https://raw.githubusercontent.com/sivel/speedtest-cli/v2.1.3/speedtest.py -O ~/.local/lib/python3.7/site-packages/speedtest.py
```
