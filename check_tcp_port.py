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

PARSER = argparse.ArgumentParser(usage='check_tcp_port.py -H host -p port -t timeout')
PARSER.add_argument('-H', '--host',
                    help='Host to check, i.e. 127.0.0.1',
                    required=True)
PARSER.add_argument('-p', '--port',
                    help='port to check, i.e. 80',
                    required=True)
PARSER.add_argument('-t', '--timeout',
                    help='optional timeout, default is 5 seconds',
                    required=False)
ARGS = PARSER.parse_args()

HOST = ARGS.host
PORT = int(ARGS.port)

if ARGS.timeout:
    TIMEOUT = ARGS.timeout
else:
    TIMEOUT = 5

try:
    SOCK = socket.socket()
    SOCK.settimeout(TIMEOUT)
    SOCK.connect((HOST, PORT))
except socket.timeout as err:
    print('CRITICAL: Connection to port {0} failed: {1}'.format(PORT, err))
    sys.exit(2)
else:
    print('OK: Connection to port {0} successful'.format(PORT))
    sys.exit(0)
finally:
    SOCK.close()
