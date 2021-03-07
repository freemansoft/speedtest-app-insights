#!/usr/bin/env python3
import argparse
import speedtest
import json
import os
import time
from SpeedTest import *

#---------------------------
# TODO add DNS lookup timing
#---------------------------

# https://github.com/sivel/speedtest-cli
#
# do not name local python file same as import file - do not name speedtest.py
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NetCheck")

#--------------------------------------------------
# determine options
# sharing may require upload and download
#--------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("-d","--download", default=False, help="include download metrics",action="store_true")
parser.add_argument("-u","--upload", default=False, help="include upload metrics",action="store_true")
parser.add_argument("-o","--outfile", type=argparse.FileType('wt'), help="write output to file as json")
parser.add_argument("-s","--share", default=False, help="register results with speedtest", action="store_true" )
parser.add_argument("-v","--verbose", default=False, help="log speedtest results as json to console and Azure", action="store_true")
args = parser.parse_args()
if (args.upload):
    logger.info("upload enabled")
if (args.download):
    logger.info("download enabled")
if (args.share):
    logger.info("result sharing enabled")


#---------------------------------------------------
# Run the test
#---------------------------------------------------
results_speed, results_setup = run_test(args.upload, args.download, args.share)
write_json(results_speed,args.outfile)
# augment the results with the setup times
results_combined = Merge(results_speed.dict(),results_setup)
logger.debug("results combined: %s", results_combined)
# use the functions inside AppInsights.py
push_speedtest_metrics(results_combined)

#---------------------------------------------------
# for testing
#---------------------------------------------------
if (args.verbose) :
    register_azure_with_logger(logger, load_insights_key())
    logger.info("{ \"combined_data\": %s }", json.dumps(results_combined, sort_keys=True)) 
    logger.debug("as json: %s", json.dumps(results_speed.dict(), indent=2, sort_keys=True))
    logger.debug("as encoded string: %s",json.dumps(results_speed.json())) # logs the entire object a singl json string
    logger.debug("as dictionary: %s",results_speed.dict())
    logger.debug("as csv: %s\n%s", results_speed.csv_header(),results_speed.csv())

