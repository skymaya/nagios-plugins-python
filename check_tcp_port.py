#!/usr/bin/python

# Author: Sky Maya
# https://github.com/skymaya

#  standard library imports
import socket
import argparse
import sys

parser = argparse.ArgumentParser(usage='check_tcp_port.py -H host -p port -t timeout')
parser.add_argument('-H', '--host',
                    help='Host to check, i.e. 127.0.0.1',
                    required=True)
parser.add_argument('-p', '--port',
                    help='port to check, i.e. 80',
                    required=True)
parser.add_argument('-t', '--timeout',
                    help='optional timeout, default is 5 seconds',
                    required=False)
args = parser.parse_args()

host = args.host
port = int(args.port)

if args.timeout:
    timeout = args.timeout
else:
    timeout = 5

try:
    s = socket.socket()
    s.settimeout(timeout)
    s.connect((host, port))
except socket.timeout as e:
    print('CRITICAL: Connection to port {0} failed: {1}'.format(port, e))
    sys.exit(2)
else:
    print('OK: Connection to port {0} successful'.format(port))
    sys.exit(0)
finally:
    s.close()
