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
    host_help = 'Host to check, i.e. 127.0.0.1'
    port_help = 'port to check, i.e. 443'
    warn_help = 'Number of days until cert expiration to trigger a warning'
    critical_help = 'Number of days until cert expiration to trigger an alert'
    issuer_help = 'Optional: name of issuer, i.e COMODO'

    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host', help=host_help, required=True)
    parser.add_argument('-p', '--port', help=port_help, type=int, required=True)
    parser.add_argument('-w', '--warn', help=warn_help, type=int, required=True)
    parser.add_argument('-c', '--critical', help=critical_help, type=int,
                        required=True)
    parser.add_argument('-i', '--issuer', help=issuer_help, required=False)
    return parser.parse_args()


def socket_connect(host, port, timeout):
    """Given a host, SSL port, and a timeout value, create a connection
    socket and return the certificate details"""
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
    """Main function"""
    args = do_argparser()
    today = convert_today_date()
    timeout = 5
    cert = socket_connect(args.host, args.port, timeout)
    issuer = dict(i[0] for i in cert['issuer'])
    not_after = convert_cert_date(cert['notAfter'])
    difference = int((not_after - today).days)

    if args.issuer and args.issuer not in issuer['commonName']:
        print("CRITICAL: {0} not found in issuer string".format(args.issuer))
        sys.exit(2)

    if difference > args.warn:
        print('OK: cert expires in {0} days'.format(difference))
        sys.exit(0)

    if difference <= 0:
        print('CRITICAL: cert expired {0} days ago'.format(abs(difference)))
        sys.exit(2)

    if difference <= args.critical:
        print('CRITICAL: cert expires in {0} days'.format(difference))
        sys.exit(2)

    if difference <= args.warn:
        print('WARNING: cert expires in {0} days'.format(difference))
        sys.exit(1)


if __name__ == "__main__":
    main()
