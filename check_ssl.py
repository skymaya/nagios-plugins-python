#!/usr/bin/python

"""Nagios plugin to check SSL certificate details for a hostname and port"""

# Author: Sky Maya
# https://github.com/skymaya
# Connects to the SSL port of a hostname and attempts to retrieve certificate details.
# Warning and critical values must be given as integers. Optionally, provide the
# name of the certificate issuer (i.e COMODO). By default, the plugin will alert
# critial if the provided hostname doesn't match what's in the certificate.
#
# Example Nagios command for commands.cfg (or where your command templates are stored):
#
# define command {
#     command_name check_ssl
#     command_line $USER1$/check_ssl.py -H $HOSTADDRESS$ -p $ARG1$ -w $ARG2$ -c $ARG3$
# }
#
# Example Nagios service for the host file:
#
# define service {
#     name check_ssl
#     check_command check_ssl!443!30!10!-i Symantec
# }
#

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


def do_argparser():
    """Parse and return command line arguments"""
    parser = argparse.ArgumentParser(usage='''check_ssl.py -H host -p port -w
                                    warn -c critical -i issuer''')
    parser.add_argument('-H', '--host',
                        help='Host to check, i.e. 127.0.0.1',
                        required=True)
    parser.add_argument('-p', '--port',
                        help='port to check, i.e. 443',
                        required=True)
    parser.add_argument('-w', '--warn',
                        help='''Number of days until certificate expiration to
                        trigger a warning''',
                        required=True)
    parser.add_argument('-c', '--critical',
                        help='''Number of days until certificate expiration to
                        trigger a critical alert''',
                        required=True)
    parser.add_argument('-i', '--issuer',
                        help='''Optional: this text must appear in the issuer
                        string, i.e COMODO''',
                        required=False)
    return parser.parse_args()


def socket_connect(host, port, timeout):
    try:
        context = ssl.create_default_context()
        ssl_sock = context.wrap_socket(socket.socket(), server_hostname=host)
        ssl_sock.settimeout(timeout)
        ssl_sock.connect((host, port))
        cert_info = ssl_sock.getpeercert()
        ssl.match_hostname(cert_info, host)
    except socket.error as err:
        print('CRITICAL: {0}'.format(err))
        sys.exit(2)
    except ssl.CertificateError as err:
        print('CRITICAL: {0}'.format(err))
        sys.exit(2)
    finally:
        ssl_sock.close()
    return cert_info


def main():
    args = do_argparser()

    hostname = args.host
    port = int(args.port)
    warn = int(args.warn)
    critical = int(args.critical)
    expect_issuer = args.issuer
    today = convert_today_date()
    timeout = 5

    cert = socket_connect(hostname, port, timeout)

    issuer = dict(i[0] for i in cert['issuer'])
    not_after = convert_cert_date(cert['notAfter'])
    difference = int((not_after - today).days)

    if expect_issuer and expect_issuer not in issuer['commonName']:
        print("CRITICAL: {0} not found in issuer string".format(expect_issuer))
        sys.exit(2)

    if difference <= critical and difference > 0:
        print('CRITICAL: certificate expires in {0} days'.format(difference))
        sys.exit(2)

    if difference == 0:
        print('CRITICAL: certificate expired today')
        sys.exit(2)

    if difference < 0:
        print('CRITICAL: certificate expired {0} days ago'.format(abs(difference)))
        sys.exit(2)

    if difference <= warn and difference < critical:
        print('warnING: certificate expires in {0} days'.format(difference))
        sys.exit(1)

    if difference > warn:
        print('OK: certificate expires in {0} days'.format(difference))
        sys.exit(0)


if __name__ == "__main__":
    main()
