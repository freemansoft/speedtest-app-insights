#!/usr/bin/env python3
import argparse
import speedtest
import json
import os
import time
#---------------------------
# TODO add DNS lookup timing
#---------------------------

# https://github.com/sivel/speedtest-cli
#
# do not name local python file same as import file - do not name speedtest.py
log_prefix = os.path.basename(__file__) + ":"
#--------------------------------------------------
# determine options
# sharing may require upload and download
#--------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("-d","--download", default=False, help="include download metrics",action="store_true")
parser.add_argument("-u","--upload", default=False, help="include upload metrics",action="store_true")
parser.add_argument("-o","--outfile", type=argparse.FileType('wt'), help="write output to file as json")
parser.add_argument("-s","--share", default=False, help="register results with speedtest", action="store_true" )
parser.add_argument("-v","--verbose", default=False, help="spend speedteset results json to console", action="store_true")
args = parser.parse_args()
if (args.upload):
    print(log_prefix,"upload enabled")
if (args.download):
    print(log_prefix,"download enabled")
if (args.share):
    print(log_prefix,"result sharing enabled")

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
    print(log_prefix,"getting servers")
    tic = time.perf_counter()
    s.get_servers(servers)
    tac = time.perf_counter()
    s.get_best_server()
    toc = time.perf_counter()
    
    if (args.download) : 
        print(log_prefix,"running download test")
        s.download(threads=threads)
    else :
        print(log_prefix,"skipping download test")

    if (args.upload) :
        print(log_prefix,"running upload test")
        s.upload(threads=threads)
    else :
        print(log_prefix,"skipping upload test")

    if (args.share) :
        print(log_prefix,"sharing results")
        print(log_prefix,"results sharing may be broken 03/03/2021")
        s.results.share()
    
    # convert seconds based times to msec
    setup_time_dict = {'get_servers':(tac-tic)*1000.0,'get_best_servers':(toc-tac)*1000.0}
    return s.results, setup_time_dict

#---------------------------------------------------
#
#---------------------------------------------------
# filetype really is the worst. 
# It can't tell you if the file already existed so we write header every time 
def write_csv(results,outfile):
    if (outfile):
        print(log_prefix,"writing to file")
        outfile.write(results.csv_header())
        outfile.write("\n")
        outfile.write(results.csv())
        outfile.write("\n")
        outfile.close()
    else:
        print(log_prefix,"no file output requested")

# This has the advantage of not requiring a header row and is self describing
def write_json(results,outfile):
    if (outfile):
        print(log_prefix,"writing to file")
        # formatting works on dict, not a string
        results_json = json.dumps(results.dict(), sort_keys=True)
        outfile.write(results_json)
        outfile.write("\n")
        outfile.close()
        return results_json
    else:
        print(log_prefix,"no file output requested")
        return "{}"

# python 3.9 adds a | operator
def Merge(dict1, dict2):
    res = {**dict1, **dict2}
    return res

#---------------------------------------------------
# Run the test
#---------------------------------------------------
results_speed, results_setup = run_test(args.upload, args.download)
write_json(results_speed,args.outfile)

# use the functions inside AppInsightsDemo.py
# augment the results with the setup times
from AppInsights import *
results_combined = Merge(results_speed.dict(),results_setup)
#print(log_prefix, results_combined)
push_speedtest_metrics(results_combined)

#---------------------------------------------------
# for testing
#---------------------------------------------------
if (args.verbose) :
    print(log_prefix,"\nas json string")
    print(log_prefix,json.dumps(results_speed.json()))
    print(log_prefix, json.dumps(results_speed.dict(), indent=2, sort_keys=True))
    #print(log_prefix,"\nas dictionary")
    #print(log_prefix,results_speed.dict())
    # print(log_prefix,"\nas csv")
    # print(log_prefix,results_speed.csv_header())
    # print(log_prefix,results_speed.csv())
