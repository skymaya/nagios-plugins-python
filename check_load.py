#!/usr/bin/python

"""Nagios plugin to check server load"""

# Author: Sky Maya
# https://github.com/skymaya
# Uses snmpget to return the 1 minute, 5 minute, and 15 minute load levels of
# a host. Accepts warning and critical values as comma-separated floats or integers
# and compares them to current load levels.
#
# REQUIRES: netsnmp (apt-get install libsnmp-python, CentOS just install net-snmp stuff)
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


def do_argparser():
    """Parse and return command line arguments"""
    usage_help = 'check_load.py -H host -C community -w [1,5,15] -c [1,5,15]'
    host_help = 'Host to check, i.e. 127.0.0.1'
    comm_help = 'SNMP community password'
    warn_help = 'Comma-separated values for 1, 5, 15 min load to trigger a warning'
    critical_help = 'Comma-separated values for 1, 5, 15 min load to trigger a critical alert'

    parser = argparse.ArgumentParser(usage=usage_help)
    parser.add_argument('-H', '--host',
                        help=host_help, required=True)
    parser.add_argument('-C', '--community',
                        help=comm_help, required=True)
    parser.add_argument('-w', '--warn',
                        help=warn_help, required=True)
    parser.add_argument('-c', '--critical',
                        help=critical_help, required=True)
    return parser.parse_args()


def main():
    """Main function"""
    args = do_argparser()

    warn = [float(i) for i in args.warn.split(',')]
    critical = [float(i) for i in args.critical.split(',')]

    m1_oid = '.1.3.6.1.4.1.2021.10.1.3.1'
    m5_oid = '.1.3.6.1.4.1.2021.10.1.3.2'
    m15_oid = '.1.3.6.1.4.1.2021.10.1.3.3'

    m1_load = do_snmpget(m1_oid, args.community, args.host)[0]
    m5_load = do_snmpget(m5_oid, args.community, args.host)[0]
    m15_load = do_snmpget(m15_oid, args.community, args.host)[0]

    load = [float(m1_load), float(m5_load), float(m15_load)]
    check_warn = [l for l, w in zip(load, warn) if l >= w]
    check_critical = [l for l, c in zip(load, critical) if l >= c]

    if check_critical:
        print('CRITICAL: load is {0}, {1}, {2}'.format(m1_load, m5_load, m15_load))
        sys.exit(2)

    if check_warn:
        print('WARNING: load is {0}, {1}, {2}'.format(m1_load, m5_load, m15_load))
        sys.exit(1)

    if not check_warn and not check_critical:
        print('OK: load is {0}, {1}, {2}'.format(m1_load, m5_load, m15_load))
        sys.exit(0)


if __name__ == "__main__":
    main()
