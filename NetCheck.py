#!/usr/bin/env python3
import argparse
import speedtest
import json
# https://github.com/sivel/speedtest-cli
#
# do not name local python file same as import file - do not name speedtest.py

#--------------------------------------------------
# determine options
#--------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("-d","--download", default=False, help="include download metrics",action="store_true")
parser.add_argument("-u","--upload", default=False, help="include upload metrics",action="store_true")
parser.add_argument("-o","--outfile", type=argparse.FileType('wt'), help="write output to file as json")
parser.add_argument("-s","--share", default=False, help="register results with speedtest", action="store_true" )
parser.add_argument("-v","--verbose", default=False, help="spend speedteset results json to console", action="store_true")
args = parser.parse_args()
if (args.upload):
    print("NetCheck:","upload enabled")
if (args.download):
    print("NetCheck:","download enabled")

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
    print("NetCheck:","getting servers")
    s.get_servers(servers)
    s.get_best_server()

    if (args.download) : 
        print("NetCheck:","running download test")
        s.download(threads=threads)
    else :
        print("NetCheck:","skipping download test")

    if (args.upload) :
        print("NetCheck:","running upload test")
        s.upload(threads=threads)
    else :
        print("NetCheck:","skipping upload test")
    if (args.share) :
        print("NetCheck:","sharing results")
        s.results.share()
    return s.results

#---------------------------------------------------
#
#---------------------------------------------------
# filetype really is the worst. 
# It can't tell you if the file already existed so we write header every time 
def write_csv(results,outfile):
    if (outfile):
        print("NetCheck:","writing to file")
        outfile.write(results.csv_header())
        outfile.write("\n")
        outfile.write(results.csv())
        outfile.write("\n")
        outfile.close()
    else:
        print("NetCheck:","no file output requested")

# This has the advantage of not requiring a header row and is self describing
def write_json(results,outfile):
    if (outfile):
        print("NetCheck:","writing to file")
        # formatting works on dict, not a string
        results_json = json.dumps(results.dict(), sort_keys=True)
        outfile.write(results_json)
        outfile.write("\n")
        outfile.close()
        return results_json
    else:
        print("NetCheck:","no file output requested")
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
    #print("NetCheck:","\nas dictionary")
    #print("NetCheck:",results.dict())
    print("NetCheck:","\nas json string")
    print("NetCheck:",json.dumps(results.json()))
    print("NetCheck:", json.dumps(results.dict(), indent=2, sort_keys=True))
    # print("NetCheck:","\nas csv")
    # print("NetCheck:",results.csv_header())
    # print("NetCheck:",results.csv())
