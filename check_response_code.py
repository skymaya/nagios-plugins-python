#!/usr/bin/python

"""Nagios plugin to check the response code of a given url"""

# Author: Sky Maya
# https://github.com/skymaya
# Connects to a URL and attempts to retrieve the status code. If the code does
# not match a valid given expected code, the script will alert critical. If the
# given expected code is invalid, the script will warn. A status of OK is only
# produced when the codes are valid and match.
#
# REQUIRES: requests (pip install requests)
#
# Example Nagios command for commands.cfg (or where your command templates are stored):
#
# define command {
#     command_name check_response_code
#     command_line $USER1$/check_response_code.py -u $ARG1$ -r $ARG2$
# }
#
# Example Nagios service for the host file:
#
# define service {
#     name check_response_code
#     check_command check_response_code!http://www.example.com!200
# }
#

from __future__ import print_function

#  standard library imports
import argparse
import sys
import re

# related third party imports
import requests


def get_response_code(url):
    """Given a url, return the status code (i.e. 200, 404, 500, etc.)"""
    req = requests.get(url)
    return req.status_code


def check_code_format(code):
    """Given a response code, check if it's valid; contains only three
    positive integers"""
    code = str(code)
    check = re.compile(r'^[0-9]{3}$')
    if not check.match(code):
        raise ValueError


PARSER = argparse.ArgumentParser(usage='check_response_code.py -u url -r responsecode')
PARSER.add_argument('-u', '--url',
                    help='URL to check, i.e. http://www.example.com',
                    required=True)
PARSER.add_argument('-r', '--responsecode',
                    help='''Expected response code returned by given URL''',
                    required=True)
ARGS = PARSER.parse_args()

ACTUAL = str(get_response_code(ARGS.url))
EXPECTED = str(ARGS.responsecode)

try:
    check_code_format(ACTUAL)
    check_code_format(EXPECTED)
except ValueError as err:
    print('WARNING: invalid code: expected {0}, got {1}'.format(EXPECTED, ACTUAL))
    sys.exit(1)

if ACTUAL == EXPECTED:
    print('OK: expected {0}, got {1}'.format(EXPECTED, ACTUAL))
    sys.exit(0)
else:
    print('CRITICAL: expected {0}, got {1}'.format(EXPECTED, ACTUAL))
    sys.exit(2)
