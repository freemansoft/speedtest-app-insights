#!/usr/bin/env python3

import datetime
import getopt
import ipaddress
import json
import os
import socket
import sys

import dns.rcode
import dns.rdatatype
import dns.resolver

# these come from dnsdiag - we're making use of their internal modules
import util.dns
from util.dns import PROTO_UDP

from AppInsights import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DnsUtil")

# code based on https://github.com/farrokhi/dnsdiag/blob/master/dnseval.py

# NOTE: future work - send this to application insights
# TODO: This accepts a list of dns servers but returns after the first one
# does a dns lookup and returns the times
def ping_me(dns_server_list, query_host_name, should_force_miss):

    # defaults
    rdatatype = "A"
    proto = PROTO_UDP
    src_ip = None
    dst_port = 53  # default for UDP and TCP
    count = 10
    waittime = 2
    use_edns = True
    want_dnssec = False

    # dns_server_list = dns.resolver.get_default_resolver().nameservers
    # print(f)

    for server in dns_server_list:
        # check if we have a valid dns server address
        if server.lstrip() == "":  # deal with empty lines
            continue
        server = server.replace(" ", "")
        try:
            ipaddress.ip_address(server)
        except ValueError:  # so it is not a valid IPv4 or IPv6 address, so try to resolve host name
            try:
                resolver = socket.getaddrinfo(server, port=None)[1][4][0]
            except OSError:
                print("Error: cannot resolve hostname:", server)
                resolver = None
            except Exception:
                pass
        else:
            resolver = server

        if not resolver:
            continue

        try:
            retval = util.dns.ping(
                query_host_name,
                resolver,
                dst_port,
                rdatatype,
                waittime,
                count,
                proto,
                src_ip,
                use_edns=use_edns,
                force_miss=should_force_miss,
                want_dnssec=want_dnssec,
            )
            # TODO this is broken. It returns after the fist server is tested
            return (
                retval.rcode,
                retval.r_min,
                retval.r_avg,
                retval.r_max,
                retval.r_stddev,
            )

        except SystemExit:
            break
        except Exception as e:
            print("%s: %s" % (server, e))
            continue


if __name__ == "__main__":
    return_code, ping_min, ping_average, ping_max, ping_stddev = ping_me(
        ["8.8.4.4", "8.8.8.8"], "wikipedia.org", False
    )

    # sample times on FIOS DC and Medicom DE are 
    #     FIOS:     return_code:0     min=0.408       avg=0.500       max=0.730       std-dev=0.090
    #     MediaCom: return_code:0     min=35.032      avg=37.418      max=39.587      std-dev=1.654   
    #     MediaCom: return_code:0     min=35.013      avg=42.450      max=59.062      std-dev=7.504   
    print(
        "return_code:%d     min=%-8.3f    avg=%-8.3f    max=%-8.3f    std-dev=%-8.3f"
        % (return_code, ping_min, ping_average, ping_max, ping_stddev)
    )

    if return_code == 0: 
        # Enable opencensus tracing. Create a new tracer for every run / loop.
        tracer = register_azure_exporter_with_tracer(load_insights_key())
        # use the functions inside AppInsights.py
        push_dns_metrics(ping_min=round(ping_min,3), ping_average=round(ping_average,3), ping_max=round(ping_max,3), ping_stddev=round(ping_stddev,3))

