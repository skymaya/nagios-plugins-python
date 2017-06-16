#!/usr/bin/python

"""Nagios plugin to check server load"""

# Author: Sky Maya
# https://github.com/skymaya
# Uses snmpget to return the 1 minute, 5 minute, and 15 minute load levels of
# a host. Accepts warning and critical values as comma-separated floats or integers
# and compares them to current load levels.
#
# REQUIRES: pysnmp
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
from pysnmp.entity.rfc3413.oneliner import cmdgen


class SNMPData(object): # pylint: disable=I0011,R0903
    """
    Make an SNMP connection and return the results with do_snmpget()

    :param community: SNMP community password for host
    :param host: hostname or IP of host
    """
    def __init__(self, community, host):
        self.community = community
        self.host = host

    @staticmethod
    def do_snmpget(community, host, oid):
        """
        Return the results of an snmpget

        :param community: SNMP community password for host
        :param host: hostname or IP of host
        :param oid: SNMP oid to retrieve data from the host
        """
        cmd_gen = cmdgen.CommandGenerator()
        err_found, err_status, err_index, var_binds = cmd_gen.getCmd(
            cmdgen.CommunityData(community),
            cmdgen.UdpTransportTarget((host, 161)), *oid)
        if err_found:
            print('UNKNOWN: {0} {1} {2}'.format(err_found, err_status, err_index))
            sys.exit(3)
        return var_binds


class LoadData(SNMPData):
    """
    Return the formatted results of an snmpget for system load

    :param community: SNMP community password for host
    :param host: hostname or IP of host
    """
    def __init__(self, community, host):
        self.oids = ['1.3.6.1.4.1.2021.10.1.3.1',
                     '1.3.6.1.4.1.2021.10.1.3.2',
                     '1.3.6.1.4.1.2021.10.1.3.3']
        self.data = self.do_snmpget(community, host, self.oids)
        super(LoadData, self).__init__(community, host)

    def one_minute(self):
        """Return the one minute load average"""
        return self.data[0][1]

    def five_minute(self):
        """Return the five minute load average"""
        return self.data[1][1]

    def fifteen_minute(self):
        """Return the fifteen minute load average"""
        return self.data[2][1]


def do_argparser():
    """Parse and return command line arguments"""
    host_help = 'Host to check, i.e. 127.0.0.1'
    comm_help = 'SNMP community password'
    warn_help = 'Comma-separated values for 1, 5, 15 min load to trigger a warning'
    critical_help = 'Comma-separated values for 1, 5, 15 min load to trigger a critical alert'

    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host', help=host_help, required=True)
    parser.add_argument('-C', '--community', help=comm_help, required=True)
    parser.add_argument('-w', '--warn', help=warn_help, required=True)
    parser.add_argument('-c', '--critical', help=critical_help, required=True)
    return parser.parse_args()


def main():
    """Main function"""
    args = do_argparser()

    warn = [float(i) for i in args.warn.split(',')]
    critical = [float(i) for i in args.critical.split(',')]

    all_load = LoadData(args.community, args.host)

    m1_load = all_load.one_minute()
    m5_load = all_load.five_minute()
    m15_load = all_load.fifteen_minute()

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
