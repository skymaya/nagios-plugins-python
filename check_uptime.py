#!/usr/bin/python

"""Nagios plugin to check server uptime"""

# Author: Sky Maya
# https://github.com/skymaya
# Version 1.0.0, 2017
# Attempts to get uptime data from a host via snmp. The data is returned as
# timeticks and converted to seconds. An operator argument is accepted to
# determine when to produce ok, warning, or critical statuses. The operator can be
# less than (lt) or greater than (gt). A time type is also accepted as sec, min,
# hr, or day. For example, if the provided arguments are:
# -w 5 -c 1 -o -lt -t days
# the plugin will warn when the uptime is less than 5 days, alert critical if
# the uptime is less than 1 day, or show an ok status if the uptime is greater
# than 5 days.
#
# Example Nagios command for commands.cfg (or where your command templates are stored):
#
# define command {
#     command_name check_uptime
#     command_line $USER1$/check_uptime.py -H $HOSTADDRESS$ -C $ARG1$ -w $ARG2$ -c $ARG3$ -o $ARG4$ -t $ARG5$
# }
#
# Example Nagios service for the host file:
#
# define service {
#     name check_uptime
#     check_command check_uptime!secretpass!5!1!lt!day
# }
#

from __future__ import print_function

#  standard library imports
import argparse
import sys
from datetime import timedelta

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


class UptimeData(SNMPData):
    """
    Return the formatted results of an snmpget for system uptime data

    :param community: SNMP community password for host
    :param host: hostname or IP of host
    """
    def __init__(self, community, host):
        self.oids = ['1.3.6.1.2.1.25.1.1.0']
        self.data = self.do_snmpget(community, host, self.oids)
        super(UptimeData, self).__init__(community, host)

    def uptime(self):
        """Return uptime in seconds"""
        # snmp data is in timeticks so go ahead and convert to seconds
        ticks = int(self.data[0][1])
        seconds = ticks / 100
        return seconds


def to_seconds(val, timetype):
    """
    Convert and return a value in seconds from seconds (sec), minutes (min),
    hours (hr), or days(day)

    :param val: initial value for the time type
    :param timetype: time type as sec, min, hr, or day
    """
    if timetype == "sec":
        return val
    elif timetype == "min":
        return val * 60.0
    elif timetype == "hr":
        return val * 3600.0
    elif timetype == "day":
        return val * 86400.0


def do_argparser():
    """Parse and return command line arguments"""
    host_help = 'Host to check, i.e. 127.0.0.1'
    comm_help = 'SNMP community password'
    warn_help = 'Length of uptime to generate a warning'
    critical_help = 'Length of uptime to generate a critical alert'
    op_help = '''Operator to use with critical and warning values; greater than
    (gt) or less than (lt)'''
    tt_help = 'Measure uptime in seconds (sec), minutes (min), hours (hr), or days (day)'
    version_help = 'check_uptime.py, Version 1.0.0, 2017'

    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host',
                        help=host_help, required=True)
    parser.add_argument('-C', '--community',
                        help=comm_help, required=True)
    parser.add_argument('-w', '--warn',
                        help=warn_help, type=float, required=True)
    parser.add_argument('-c', '--critical',
                        help=critical_help, type=float, required=True)
    parser.add_argument('-o', '--operator',
                        help=op_help, required=True)
    parser.add_argument('-t', '--timetype',
                        help=tt_help, required=True)
    parser.add_argument('-v', '--version',
                        help=version_help, required=False)
    return parser.parse_args()


def main():
    """Main function"""
    args = do_argparser()

    uptime_seconds = UptimeData(args.community, args.host).uptime()
    pretty_uptime = timedelta(seconds=uptime_seconds)
    user_warn = to_seconds(args.warn, args.timetype)
    user_critical = to_seconds(args.critical, args.timetype)

    if args.operator == 'lt':
        if uptime_seconds <= user_critical:
            print('CRITICAL: server uptime is {0}'.format(pretty_uptime))
            sys.exit(2)
        elif uptime_seconds <= user_warn:
            print('WARNING: server uptime is {0}'.format(pretty_uptime))
            sys.exit(1)
        elif uptime_seconds > user_warn:
            print('OK: server uptime is {0}'.format(pretty_uptime))
            sys.exit(0)

    if args.operator == 'gt':
        if uptime_seconds >= user_critical:
            print('CRITICAL: server uptime is {0}'.format(pretty_uptime))
            sys.exit(2)
        elif uptime_seconds >= user_warn:
            print('WARNING: server uptime is {0}'.format(pretty_uptime))
            sys.exit(1)
        elif uptime_seconds < user_warn:
            print('OK: server uptime is {0}'.format(pretty_uptime))
            sys.exit(0)


if __name__ == "__main__":
    main()
