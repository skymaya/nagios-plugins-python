#!/usr/bin/python

"""Nagios plugin to check the number of logged in system users"""

# Author: Sky Maya
# https://github.com/skymaya
# Uses SNMP to check the number of logged in system (Unix) users. Returns an ok
# status if the number of users is less than the warning level, a warning status
# if the number of users is greater than or equal to the warning level but less
# than the critical level, or a critical status when the number of users is
# greater than or equal to the critical level.
#
# REQUIRES: pysnmp
#
# Example Nagios command for commands.cfg (or where your command templates are stored):
#
# define command {
#     command_name check_users
#     command_line $USER1$/check_users.py -H $HOSTADDRESS$ -C $ARG1$ -w $ARG2$ -c $ARG3$
# }
#
# Example Nagios service for the host file:
#
# define service {
#     name check_users
#     check_command check_users!secretpass!3!4
# }
#

from __future__ import print_function

#  standard library imports
import argparse
import sys

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


class UserData(SNMPData):
    """Functions to make an SNMP connection to retrieve system users"""
    def __init__(self, community, host):
        self.oids = ['1.3.6.1.2.1.25.1.5.0']
        self.data = self.do_snmpget(community, host, self.oids)
        super(UserData, self).__init__(community, host)

    def user_count(self):
        """Return the number of logged in system users"""
        return int(self.data[0][1])


def do_argparser():
    """Parse and return command line arguments"""
    usage_help = 'check_users.py -H host -C community -w val -c val'
    host_help = 'Host to check, i.e. 127.0.0.1'
    comm_help = 'SNMP community password'
    warn_help = 'Number of logged in users to generate a warning'
    critical_help = 'Number of logged in users to generate a critical alert'

    parser = argparse.ArgumentParser(usage=usage_help)
    parser.add_argument('-H', '--host',
                        help=host_help, required=True)
    parser.add_argument('-C', '--community',
                        help=comm_help, required=True)
    parser.add_argument('-w', '--warn',
                        help=warn_help, type=int, required=True)
    parser.add_argument('-c', '--critical',
                        help=critical_help, type=int, required=True)
    return parser.parse_args()


def main():
    """Main function"""
    args = do_argparser()

    users = UserData(args.community, args.host).user_count()

    if users >= args.critical:
        print('CRITICAL: {0} logged in users'.format(users))
        sys.exit(2)

    if users >= args.warn:
        print('WARNING: {0} logged in users'.format(users))
        sys.exit(1)

    if users < args.warn:
        print('OK: {0} logged in users'.format(users))
        sys.exit(0)


if __name__ == "__main__":
    main()
