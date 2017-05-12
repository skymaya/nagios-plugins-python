#!/usr/bin/python

"""Nagios plugin to check SSL certificate details for a hostname and port"""

# Author: Sky Maya
# https://github.com/skymaya

from __future__ import print_function

#  standard library imports
import ssl
import socket
import argparse
import sys
from datetime import datetime


def convert_cert_date(date):
    """Given a string date from SSL output, return a formatted date object"""
    new_date = date.replace('GMT', '').rstrip()
    new_date = datetime.strptime(new_date, '%b %d %H:%M:%S %Y')
    return new_date


def convert_today_date():
    """Return a formatted date object from today's date that matches the string
    date from SSL output"""
    today = datetime.utcnow()
    today = datetime.strftime(today, '%Y-%m-%d %H:%M:%S')
    today = datetime.strptime(today, '%Y-%m-%d %H:%M:%S')
    return today


PARSER = argparse.ArgumentParser(usage='check_ssl.py -H host -p port -w warn -c critical -i issuer')
PARSER.add_argument('-H', '--host',
                    help='Host to check, i.e. 127.0.0.1',
                    required=True)
PARSER.add_argument('-p', '--port',
                    help='port to check, i.e. 443',
                    required=True)
PARSER.add_argument('-w', '--warn',
                    help='Number of days until certificate expiration to trigger a warning',
                    required=True)
PARSER.add_argument('-c', '--critical',
                    help='Number of days until certificate expiration to trigger a critical alert',
                    required=True)
PARSER.add_argument('-i', '--issuer',
                    help='Optional: this text must appear in the issuer string, i.e COMODO',
                    required=False)
ARGS = PARSER.parse_args()

HOSTNAME = ARGS.host
PORT = int(ARGS.port)
WARN = int(ARGS.warn)
CRITICAL = int(ARGS.critical)
EXPECT_ISSUER = ARGS.issuer
TODAY = convert_today_date()
TIMEOUT = 5

try:
    CONTEXT = ssl.create_default_context()
    SSL_SOCK = CONTEXT.wrap_socket(socket.socket(), server_hostname=HOSTNAME)
    SSL_SOCK.settimeout(TIMEOUT)
    SSL_SOCK.connect((HOSTNAME, PORT))
    CERT = SSL_SOCK.getpeercert()
except socket.error as err:
    print('CRITICAL: {0}'.format(err))
    sys.exit(2)
finally:
    SSL_SOCK.close()

ISSUER = dict(i[0] for i in CERT['issuer'])
SUBJECT = dict(i[0] for i in CERT['subject'])
NOT_AFTER = convert_cert_date(CERT['notAfter'])
DIFFERENCE = int((NOT_AFTER - TODAY).days)

if not SUBJECT['commonName'].endswith(HOSTNAME):
    print("CRITICAL: Hostname doesn't match certificate")
    sys.exit(2)

if EXPECT_ISSUER and EXPECT_ISSUER not in ISSUER['commonName']:
    print("CRITICAL: {0} not found in issuer string".format(EXPECT_ISSUER))
    sys.exit(2)

if DIFFERENCE <= CRITICAL and DIFFERENCE > 0:
    print('CRITICAL: certificate expires in {0} days'.format(DIFFERENCE))
    sys.exit(2)

if DIFFERENCE == 0:
    print('CRITICAL: certificate expired today')
    sys.exit(2)

if DIFFERENCE < 0:
    print('CRITICAL: certificate expired {0} days ago'.format(abs(DIFFERENCE)))
    sys.exit(2)

if DIFFERENCE <= WARN and DIFFERENCE < CRITICAL:
    print('WARNING: certificate expires in {0} days'.format(DIFFERENCE))
    sys.exit(1)

if DIFFERENCE > WARN:
    print('OK: certificate expires in {0} days'.format(DIFFERENCE))
    sys.exit(0)
