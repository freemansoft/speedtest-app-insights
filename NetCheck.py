#!/usr/bin/env python3
import argparse
import speedtest
import json
# https://github.com/sivel/speedtest-cli
#
# do not name the file same as import - do not name speedtest.py

#--------------------------------------------------
# determine options
#--------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("-d","--download", default=False, help="include download metrics",action="store_true")
parser.add_argument("-u","--upload", default=False, help="include upload metrics",action="store_true")
parser.add_argument("-o","--outfile", type=argparse.FileType('wt'), help="write output to file as json")
parser.add_argument("-v","--verbose", default=False, help="spend speedteset results json to console", action="store_true")
args = parser.parse_args()
if (args.upload):
    print("upload enabled")
if (args.download):
    print("download enabled")

#---------------------------------------------------
# Actual speed test
#---------------------------------------------------
def run_test(should_download, should_upload):
    servers = []
    # If you want to test against a specific server
    # servers = [1234]

    threads = None
    # If you want to use a single threaded test
    #threads = 1

    # geeting the servers does a ping
    s = speedtest.Speedtest() 
    print("getting servers")
    s.get_servers(servers)
    s.get_best_server()

    if (args.download) : 
        print("running download test")
        s.download(threads=threads)
    else :
        print("skipping download test")

    if (args.upload) :
        print("running upload test")
        s.upload(threads=threads)
    else :
        print("skipping upload test")
    #s.results.share()
    return s.results

#---------------------------------------------------
#
#---------------------------------------------------
# filetype really is the worst. 
# It can't tell you if the file already existed so we write header every time 
def write_csv(results,outfile):
    if (outfile):
        print("writing to file")
        outfile.write(results.csv_header())
        outfile.write("\n")
        outfile.write(results.csv())
        outfile.write("\n")
        outfile.close()
    else:
        print("no file output requested")

# This has the advantage of not requiring a header row and is self describing
def write_json(results,outfile):
    if (outfile):
        print("writing to file")
        # formatting works on dict, not a string
        results_json = json.dumps(results.dict(), sort_keys=True)
        outfile.write(results_json)
        outfile.write("\n")
        outfile.close()
        return results_json
    else:
        print("no file output requested")
        return "{}"


#---------------------------------------------------
# Run the test
#---------------------------------------------------
results = run_test(args.upload, args.download)
write_json(results,args.outfile)

# use the functions inside AppInsightsDemo.py
from AppInsights import *
record_speedtest(results.dict())

#---------------------------------------------------
# for testing
#---------------------------------------------------
if (args.verbose) :
    #print("\nas dictionary")
    #print(results.dict())
    print("\nas json string")
    print(json.dumps(results.json()))
    print( json.dumps(results.dict(), indent=2, sort_keys=True))
    # print("\nas csv")
    # print(results.csv_header())
    # print(results.csv())
