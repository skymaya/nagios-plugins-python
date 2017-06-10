#!/usr/bin/python

"""Nagios plugin to check a tcp connection for a hostname and port"""

# Author: Sky Maya
# https://github.com/skymaya
# Attempts to connect to a given port for the given host. A custom timeout value
# may be provided but the default is 5 seconds. This plugin can be used to check
# any tcp port connection; 80, 443, 22, 21, 25, etc. It's just a very generic
# port check plugin. Alerts critical if a connection can't be made or ok if it
# connects.
#
# Example Nagios command for commands.cfg (or where your command templates are stored):
#
# define command {
#     command_name check_tcp_port
#     command_line $USER1$/check_tcp_port.py -H $HOSTADDRESS$ -p $ARG1$
# }
#
# Example Nagios service for the host file:
#
# define service {
#     name check_tcp_port
#     check_command check_tcp_port!80!-t 3
# }
#


from __future__ import print_function

#  standard library imports
import socket
import argparse
import sys


def do_argparser():
    """Parse and return command line arguments"""
    host_help = 'Host to check, i.e. 127.0.0.1'
    port_help = 'port to check, i.e. 80'
    timeout_help = 'optional timeout, default is 5 seconds'

    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host',
                        help=host_help, required=True)
    parser.add_argument('-p', '--port',
                        help=port_help, type=int, required=True)
    parser.add_argument('-t', '--timeout',
                        help=timeout_help, type=float, required=False)
    return parser.parse_args()


def socket_connect(host, port, timeout):
    """Given a host, port, and timeout values, attempt to connect to the port
    and throw an exception with CRITICAL message if it fails or print OK status
    if successful"""
    try:
        sock = socket.socket()
        sock.settimeout(timeout)
        sock.connect((host, port))
    except socket.timeout as err:
        print('CRITICAL: Connection to port {0} failed: {1}'.format(port, err))
        sys.exit(2)
    else:
        print('OK: Connection to port {0} successful'.format(port))
        sys.exit(0)
    finally:
        sock.close()


def main():
    """Main function"""
    args = do_argparser()
    host = args.host
    port = args.port
    if args.timeout:
        timeout = args.timeout
    else:
        timeout = 5.0
    socket_connect(host, port, timeout)


if __name__ == "__main__":
    main()
