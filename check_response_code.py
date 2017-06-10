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

# related third party imports
import requests


def get_response_code(url):
    """Given a url, return the status code (i.e. 200, 404, 500, etc.)"""
    req = requests.get(url)
    return req.status_code


def do_argparser():
    """Parse and return command line arguments"""
    url_help = 'URL to check, i.e. http://www.example.com'
    rcode_help = 'Expected response code returned by given URL'

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url',
                        help=url_help, required=True)
    parser.add_argument('-r', '--responsecode',
                        help=rcode_help, type=str, required=True)
    return parser.parse_args()


def main():
    """Main function"""
    args = do_argparser()

    actual = str(get_response_code(args.url))
    expected = args.responsecode

    if actual == expected:
        print('OK: expected {0}, got {1}'.format(expected, actual))
        sys.exit(0)
    else:
        print('CRITICAL: expected {0}, got {1}'.format(expected, actual))
        sys.exit(2)


if __name__ == "__main__":
    main()
