#!/usr/bin/env python3
import argparse
import speedtest
import json
import os
import time
from AppInsights import *
#---------------------------
# TODO add DNS lookup timing
#---------------------------

# https://github.com/sivel/speedtest-cli
#
# do not name local python file same as import file - do not name speedtest.py
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


#---------------------------------------------------
# Actual speed test
#---------------------------------------------------
def run_test(should_download, should_upload, should_share, tracer):
    with tracer.span(name="main") as span:
        servers = []
        # If you want to test against a specific server
        # servers = [1234]

        threads = None
        # If you want to use a single threaded test
        #threads = 1

        # getting the servers does a ping
        s = speedtest.Speedtest() 
        logger.info("getting servers")
        tic = time.perf_counter()
        with tracer.span(name="get_servers") as span:
            s.get_servers(servers)
        tac = time.perf_counter()
        with tracer.span(name="get_best_servers") as span:
            s.get_best_server()
        toc = time.perf_counter()    

        if (should_download) : 
            with tracer.span(name="measure_download") as span:
                logger.info("running download test")
                s.download(threads=threads)
        else :
            logger.info("skipping download test")

        if (should_upload) :
            with tracer.span(name="measure_upload") as span:
                logger.info("running upload test")
                s.upload(threads=threads)
        else :
            logger.info("skipping upload test")

        if (should_share) :
            with tracer.span(name="sharing_is_caring") as span:
                logger.info("sharing results - results sharing may be broken 03/03/2021")
                s.results.share()
        
        # calculate and return the setup time which is not reported by speedtest
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
        logger.info("writing to file")
        outfile.write(results.csv_header())
        outfile.write("\n")
        outfile.write(results.csv())
        outfile.write("\n")
        outfile.close()
    else:
        logger.info("no file output requested")

# This has the advantage of not requiring a header row and is self describing
def write_json(results,outfile):
    if (outfile):
        logger.info("writing to file")
        # formatting works on dict, not a string
        results_json = json.dumps(results.dict(), sort_keys=True)
        outfile.write(results_json)
        outfile.write("\n")
        outfile.close()
        return results_json
    else:
        logger.info("no file output requested")
        return "{}"

# Merge two dictionaries
# python 3.9 adds a | operator
def Merge(dict1, dict2):
    res = {**dict1, **dict2}
    return res

