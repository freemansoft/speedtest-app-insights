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
logger = logging.getLogger(__name__)

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
    logger.info("as json string")
    logger.info("%s",json.dumps(results_speed.json()))
    logger.info("%s", json.dumps(results_speed.dict(), indent=2, sort_keys=True))
    logger.debug("\nas dictionary")
    logger.debug("%s",results_speed.dict())
    logger.debug("\nas csv")
    logger.debug("%s", results_speed.csv_header())
    logger.debug("%s",results_speed.csv())
