#!/usr/bin/python

"""Nagios plugin to check ping (packet loss and transit time). IPv4 only"""

# Author: Sky Maya
# https://github.com/skymaya
# Pings a host and warns or alerts critical if actual packet loss or transit
# time exceeds given values.
#
# Example Nagios command for commands.cfg (or where your command templates are stored):
#
# define command {
#     command_name check_ping
#     command_line $USER1$/check_ping.py -H $HOSTADDRESS$ -w $ARG1$ -c $ARG2$
# }
#
# Example Nagios service for the host file:
#
# define service {
#     name check_ping
#     check_command check_ping!10,100!20,200
# }
#

from __future__ import print_function

#  standard library imports
import subprocess
import re
import argparse
import sys


def do_ping(packets, host, timeout):
    """Given the number of packets to transmit, host IP, and timeout value,
    ping the host and return a list containing the results"""
    ping = subprocess.Popen(['ping', '-q', '-W', timeout, '-c', packets, host],
                            stdout=subprocess.PIPE)
    output = ping.communicate()[0]
    ping.stdout.close()
    output = [i for i in output.split('\n') if i.strip()]
    return output


def get_packetloss(output):
    """Given the list output of ping results using do_ping(), return the packet
    loss percentage as a float"""
    packetloss = [i for i in output if 'packet loss' in i]
    packetloss = '{0}'.format(packetloss[0])
    packetloss = re.search(r'(\d)%', packetloss).group().replace('%', '')
    return float(packetloss)


def get_rtt(output):
    """Given the list output of ping results using do_ping(), return the average
    transit time in milliseconds as a float"""
    rtt = [i for i in output if 'rtt' in i and 'avg' in i]
    rtt = '{0}'.format(rtt[0])
    rtt = re.search(r'\/(\d.*?)\/', rtt).group().replace('/', '')
    return float(rtt)


PARSER = argparse.ArgumentParser(usage='check_ping.py -H host -w [pl,rtt] -c [pl,rtt]')
PARSER.add_argument('-H', '--host',
                    help='Host to check, i.e. 127.0.0.1',
                    required=True)
PARSER.add_argument('-w', '--warn',
                    help='''Comma-separated values for packet loss, transit time
                    to trigger a warning''',
                    required=True)
PARSER.add_argument('-c', '--critical',
                    help='''Comma-separated values for packet loss, transit time
                    to trigger a critical alert''',
                    required=True)
PARSER.add_argument('-t', '--timeout',
                    help='''Optional: specify a timeout to wait for ping
                    response, defaults to 5 seconds''',
                    required=False)
PARSER.add_argument('-p', '--packets',
                    help='''Optional: specify the number of packets to transmit,
                    defaults to 5''',
                    required=False)
ARGS = PARSER.parse_args()

if ARGS.timeout:
    TIMEOUT = ARGS.timeout
else:
    TIMEOUT = '5'

if ARGS.packets:
    PACKETS = ARGS.packets
else:
    PACKETS = '5'

HOST = ARGS.host

PING = do_ping(PACKETS, HOST, TIMEOUT)

PL = get_packetloss(PING)
RTT = get_rtt(PING)

WARN_PL = float(ARGS.warn.split(',')[0])
CRITICAL_PL = float(ARGS.critical.split(',')[0])
WARN_RTT = float(ARGS.warn.split(',')[1])
CRITICAL_RTT = float(ARGS.critical.split(',')[1])

if PL >= CRITICAL_PL or RTT >= CRITICAL_RTT:
    print('CRITICAL: packet loss {0}%, rtt avg {1} ms'.format(PL, RTT))
    sys.exit(2)

if PL >= WARN_PL or RTT >= WARN_RTT:
    print('WARNING: packet loss {0}%, rtt avg {1} ms'.format(PL, RTT))
    sys.exit(1)

if PL < WARN_PL and RTT < WARN_RTT:
    print('OK: packet loss {0}%, rtt avg {1} ms'.format(PL, RTT))
    sys.exit(0)
