#!/usr/bin/python

"""Nagios plugin to check SSH connection using telnet"""

# Author: Sky Maya
# https://github.com/skymaya
# Version 1.0.0, 2017
# Uses telnet to connect to a given SSH port on a host. Alerts critical if
# something is wrong with the connection, warning if the response is unexpected,
# or ok if the response contains SSH.
#
# Example Nagios command for commands.cfg (or where your command templates are stored):
#
# define command {
#     command_name check_ssh
#     command_line $USER1$/check_ssh.py -H $HOSTADDRESS$ -p $ARG1$
# }
#
# Example Nagios service for the host file:
#
# define service {
#     name check_ssh
#     check_command check_ssh!127.0.0.1!!22!-t 5
# }
#

from __future__ import print_function

#  standard library imports
import telnetlib
import sys
import socket
import argparse


def telnet_connect(host, port, timeout):
    """
    Return data response from a telnet connection

    :param host: hostname or IP for the telnet connection
    :param port: host port to check
    :param timeout: timeout to wait for connection
    """
    try:
        tlnt = telnetlib.Telnet()
        tlnt.open(host, port, timeout)
    except socket.timeout as err:
        print('CRITICAL: {0}'.format(err))
        sys.exit(2)
    else:
        data = tlnt.read_some().strip()
    finally:
        tlnt.close()
    return data


def do_argparser():
    """Parse and return command line arguments"""
    host_help = 'URL to check, i.e. http://www.example.com'
    port_help = 'Expected response code returned by given URL'
    timeout_help = 'Optional: specify a timeout to wait for telnet response, defaults to 5 seconds'
    version_help = 'check_ssh.py, Version 1.0.0, 2017'

    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host',
                        help=host_help, required=True)
    parser.add_argument('-p', '--port',
                        help=port_help, required=True)
    parser.add_argument('-t', '--timeout',
                        help=timeout_help, type=float, required=False)
    parser.add_argument('-v', '--version',
                        help=version_help, required=False)
    return parser.parse_args()


def main():
    """Main function"""
    args = do_argparser()

    if args.timeout:
        timeout = args.timeout
    else:
        timeout = 5

    ssh_data = str(telnet_connect(args.host, args.port, timeout))

    if 'SSH' in ssh_data:
        print('OK: {0}'.format(ssh_data))
        sys.exit(0)
    else:
        print('WARNING: unexpected data {0}'.format(ssh_data))
        sys.exit(1)


if __name__ == "__main__":
    main()
