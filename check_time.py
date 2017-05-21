#!/usr/bin/python

"""Nagios plugin to check server time drift"""

# Author: Sky Maya
# https://github.com/skymaya
# Uses SNMP to get the host's timestamp as returned by HOST-RESOURCES-MIB::hrSystemDate
# and formats it into a UTC timestamp. Accepts a values for warning and critical
# statuses representing time drift in minutes. An ok status is returned when the
# drift is less than the warning value, a warning status is returned when the
# drift is equal to or greater than the warning value but is less than the
# critical value, and finally a critical status is returned if the drift is
# equal to or greater than the critical value. Setting a warning value of no
# less than 1 minute is recommended.
#
# REQUIRES: pysnmp
#
# Example Nagios command for commands.cfg (or where your command templates are stored):
#
# define command {
#     command_name check_time
#     command_line $USER1$/check_time.py -H $HOSTADDRESS$ -C $ARG1$ -w $ARG2$ -c $ARG3$
# }
#
# Example Nagios service for the host file:
#
# define service {
#     name check_time
#     check_command check_time!secretpass!1!5
# }
#

from __future__ import print_function

#  standard library imports
import argparse
import sys
from datetime import datetime, timedelta

# related third party imports
from pysnmp.entity.rfc3413.oneliner import cmdgen


class SNMPData(object): # pylint: disable=too-few-public-methods
    """Functions to make an SNMP connection to retrieve data"""
    def __init__(self, community, host):
        self.community = community
        self.host = host

    @staticmethod
    def do_snmpget(community, host, oid):
        """Given an list of one or more oids, community password, and host,
        return the result of an snmpget"""
        cmd_gen = cmdgen.CommandGenerator()
        err_found, err_status, err_index, var_binds = cmd_gen.getCmd(
            cmdgen.CommunityData(community),
            cmdgen.UdpTransportTarget((host, 161)), *oid)
        if err_found:
            print('UNKNOWN: {0} {1} {2}'.format(err_found, err_status, err_index))
            sys.exit(3)
        return var_binds


class TimeData(SNMPData):
    """Functions to make an SNMP connection to retrieve system uptime data"""
    def __init__(self, community, host):
        self.oids = [(('HOST-RESOURCES-MIB', 'hrSystemDate'), 0)]
        self.data = self.do_snmpget(community, host, self.oids)
        self.host_ts = self.data[0][1].prettyPrint().split(',')
        super(TimeData, self).__init__(community, host)

    @staticmethod
    def convert_to_utc(dto, offset):
        """Given a datetime object in the format yyyy-mm-dd 24:mm:ss.ms and
        utc offset list in the format [hrs, mins], convert to utc and return
        converted datetime"""
        # Possibly a silly way to convert to UTC but avoiding importing
        # additional 3rd party libraries for now
        if offset[0] >= 0:
            dt_utc = dto - timedelta(hours=offset[0], minutes=offset[1])
        elif offset[0] < 0:
            dt_utc = dto + timedelta(hours=abs(offset[0]), minutes=offset[1])
        return dt_utc

    def host_time_utc(self):
        """Return host time as a datetime object converted to UTC"""
        host_day = self.host_ts[0]
        host_time = self.host_ts[1]
        host_offset = [int(i) for i in self.host_ts[2].split(':')]
        host_dt = datetime.strptime(host_day+' '+host_time, '%Y-%m-%d %H:%M:%S.%f')
        host_dt_utc = self.convert_to_utc(host_dt, host_offset)
        return host_dt_utc


def do_argparser():
    """Parse and return command line arguments"""
    usage_help = 'check_uptime.py -H host -C community -w val -c val'
    host_help = 'Host to check, i.e. 127.0.0.1'
    comm_help = 'SNMP community password'
    warn_help = 'Drift in minutes to generate a warning'
    critical_help = 'Drift in minutes to generate a critical alert'

    parser = argparse.ArgumentParser(usage=usage_help)
    parser.add_argument('-H', '--host',
                        help=host_help, required=True)
    parser.add_argument('-C', '--community',
                        help=comm_help, required=True)
    parser.add_argument('-w', '--warn',
                        help=warn_help, type=float, required=True)
    parser.add_argument('-c', '--critical',
                        help=critical_help, type=float, required=True)
    return parser.parse_args()


def main():
    """Main function"""
    args = do_argparser()

    host_now = TimeData(args.community, args.host).host_time_utc()
    now = datetime.utcnow()
    diff = round(abs(now - host_now).seconds / 60.0, 3)

    if diff >= args.critical:
        print('CRITICAL: drift is {0}, time is {1} UTC'.format(diff, host_now))
        sys.exit(2)

    if diff >= args.warn:
        print('WARNING: drift is {0}, time is {1} UTC'.format(diff, host_now))
        sys.exit(1)

    if diff < args.warn:
        print('OK: drift is {0}, time is {1} UTC'.format(diff, host_now))
        sys.exit(0)


if __name__ == "__main__":
    main()
