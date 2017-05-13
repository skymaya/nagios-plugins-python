#!/usr/bin/python

"""Nagios plugin to check server load"""

# Author: Sky Maya
# https://github.com/skymaya
# Uses snmpget to return the 1 minute, 5 minute, and 15 minute load levels of
# a host. Accepts warning and critical values as comma-separated floats or integers
# and compares them to current load levels.
#
# REQUIRES: netsnmp (apt-get install libsnmp-python)
#
# Example Nagios command for commands.cfg (or where your command templates are stored):
#
# define command {
#     command_name check_load
#     command_line $USER1$/check_load.py -H $HOSTADDRESS$ -C $ARG1$ -w $ARG2$ -c $ARG3$
# }
#
# Example Nagios service for the host file:
#
# define service {
#     name check_load
#     check_command check_load!secretpass!1,3,5!5,7,9
# }
#

from __future__ import print_function

#  standard library imports
import argparse
import sys

# related third party imports
import netsnmp


def do_snmpget(oid, community, host):
    """Given an oid, community password, and host, return the result of an
    snmpget"""
    var = netsnmp.Varbind(oid)
    res = netsnmp.snmpget(var, Version=2, DestHost=host, Community=community)
    return res


PARSER = argparse.ArgumentParser(usage='check_load.py -H host -C community -w [1,5,15] -c [1,5,15]')
PARSER.add_argument('-H', '--host',
                    help='Host to check, i.e. 127.0.0.1',
                    required=True)
PARSER.add_argument('-C', '--community',
                    help='SNMP community password',
                    required=True)
PARSER.add_argument('-w', '--warn',
                    help='Comma-separated values for 1, 5, 15 min load to trigger a warning',
                    required=True)
PARSER.add_argument('-c', '--critical',
                    help='Comma-separated values for 1, 5, 15 min load to trigger a critical alert',
                    required=True)
ARGS = PARSER.parse_args()

COMMUNITY = ARGS.community
HOST = ARGS.host
WARN = [float(i) for i in ARGS.warn.split(',')]
CRITICAL = [float(i) for i in ARGS.critical.split(',')]

M1_OID = '.1.3.6.1.4.1.2021.10.1.3.1'
M5_OID = '.1.3.6.1.4.1.2021.10.1.3.2'
M15_OID = '.1.3.6.1.4.1.2021.10.1.3.3'

M1_LOAD = do_snmpget(M1_OID, COMMUNITY, HOST)[0]
M5_LOAD = do_snmpget(M5_OID, COMMUNITY, HOST)[0]
M15_LOAD = do_snmpget(M15_OID, COMMUNITY, HOST)[0]

LOAD = [float(M1_LOAD), float(M5_LOAD), float(M15_LOAD)]
CHECK_WARN = [l for l, w in zip(LOAD, WARN) if l >= w]
CHECK_CRITICAL = [l for l, c in zip(LOAD, CRITICAL) if l >= c]

if CHECK_CRITICAL:
    print('CRITICAL: load is {0}, {1}, {2}'.format(M1_LOAD, M5_LOAD, M15_LOAD))
    sys.exit(2)

if CHECK_WARN:
    print('WARNING: load is {0}, {1}, {2}'.format(M1_LOAD, M5_LOAD, M15_LOAD))
    sys.exit(1)

if not CHECK_WARN and not CHECK_CRITICAL:
    print('OK: load is {0}, {1}, {2}'.format(M1_LOAD, M5_LOAD, M15_LOAD))
    sys.exit(0)
