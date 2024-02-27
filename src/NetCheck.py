#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2022 Joe Freeman joe@freemansoft.com
#
# SPDX-License-Identifier: MIT
#
import argparse
import json
import logging

from opentelemetry.trace import Tracer

from AppInsights import (
    create_ot_tracer,
    load_insights_key,
    push_azure_speedtest_metrics,
    register_azure_monitor,
)
from SpeedTest import Merge, run_test, write_json

# ---------------------------
# TODO add DNS lookup timing
# ---------------------------

# https://github.com/sivel/speedtest-cli
#
# do not name local python file same as import file - do not name speedtest.py
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NetCheck")

# --------------------------------------------------
# determine options
# sharing may require upload and download
# --------------------------------------------------
parser = argparse.ArgumentParser(
    prog="NetCheck",
    description="A Python Driver for SpeedTest.net latency and throughput.",
    epilog="Start your engines!",
)
parser.add_argument(
    "-d",
    "--download",
    default=False,
    help="include download metrics",
    action="store_true",
)
parser.add_argument(
    "-u",
    "--upload",
    default=False,
    help="include upload metrics",
    action="store_true",
)
parser.add_argument(
    "-o",
    "--outfile",
    type=argparse.FileType("wt"),
    help="write output to file as json",
)
parser.add_argument(
    "-s",
    "--share",
    default=False,
    help="register results with speedtest",
    action="store_true",
)
parser.add_argument(
    "-v",
    "--verbose",
    default=False,
    help="log speedtest results as json to console and Azure",
    action="store_true",
)
args = parser.parse_args()
if args.upload:
    logger.info("upload enabled")
if args.download:
    logger.info("download enabled")
if args.share:
    logger.info("result sharing enabled")

azure_instrumentation_key = load_insights_key()
# Enable tracing
register_azure_monitor(
    azure_connection_string=azure_instrumentation_key,
    cloud_role_name="NetCheck.py",
    capture_logs=args.verbose,
)
# Need the actual tracer to do spans
tracer: Tracer = create_ot_tracer()
# ---------------------------------------------------
# Run the test
# ---------------------------------------------------
results_speed, results_setup = run_test(
    should_download=args.download,
    should_upload=args.upload,
    should_share=args.share,
    tracer=tracer,
)
# write out just the standard speedtest results
write_json(results_speed, args.outfile)
# augment the results with the setup times
results_combined = Merge(results_speed.dict(), results_setup)
logger.debug("results combined: %s", results_combined)
# use the functions inside AppInsights.py
push_azure_speedtest_metrics(results_combined, azure_instrumentation_key)

# ---------------------------------------------------
# We route the verbose log output to the ApplicationInsights logs.
# ---------------------------------------------------
if args.verbose:
    # Program exits after one execution
    # so only these log statements end up in Application insights.
    logger.info(
        '{ "combined_data": %s }', json.dumps(results_combined, sort_keys=True)
    )
    logger.debug(
        "as json: %s",
        json.dumps(results_speed.dict(), indent=2, sort_keys=True),
    )
    logger.debug(
        "as encoded string: %s", json.dumps(results_speed.json())
    )  # logs the entire object a singl json string
    logger.debug("as dictionary: %s", results_speed.dict())
    logger.debug(
        "as csv: %s\n%s", results_speed.csv_header(), results_speed.csv()
    )
