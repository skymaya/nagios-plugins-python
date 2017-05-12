#!/usr/bin/python

"""Nagios plugin to check a tcp connection for a hostname and port"""

# Author: Sky Maya
# https://github.com/skymaya

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
