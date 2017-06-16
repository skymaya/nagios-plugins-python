#!/usr/bin/python

"""Nagios plugin to check ping (packet loss and transit time). IPv4 only"""

# Author: Sky Maya
# https://github.com/skymaya
# Version 1.0.0, 2017
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
    """
    Return a list of results from a ping command

    :param packets: number of packets to transmit
    :param host: hostname or IP of host
    :param timeout: timeout to wait for results
    """
    ping = subprocess.Popen(['ping', '-q', '-W', timeout, '-c', packets, host],
                            stdout=subprocess.PIPE)
    output = str(ping.communicate()[0])
    ping.stdout.close()
    output = [i for i in output.split('\n') if i.strip()]
    return output


def get_packetloss(output):
    """
    Return ping packet loss percentage

    :param output: list of ping results obtained from do_ping()
    """
    packetloss = [i for i in output if 'packet loss' in i]
    packetloss = '{0}'.format(packetloss[0])
    packetloss = re.search(r'(\d)%', packetloss).group().replace('%', '')
    return float(packetloss)


def get_rtt(output):
    """
    Return the average transit time in milliseconds

    :param output: list of ping results obtained from do_ping()
    """
    rtt = [i for i in output if 'rtt' in i and 'avg' in i]
    rtt = '{0}'.format(rtt[0])
    rtt = re.search(r'\/(\d.*?)\/', rtt).group().replace('/', '')
    return float(rtt)


def do_argparser():
    """Parse and return command line arguments"""
    host_help = 'Host to check, i.e. 127.0.0.1'
    warn_help = 'Comma-separated values for packet loss, transit time to trigger a warning'
    critical_help = '''Comma-separated values for packet loss, transit time to
    trigger a critical alert'''
    timeout_help = 'Optional: specify a timeout to wait for ping response, defaults to 5 seconds'
    packets_help = 'Optional: specify the number of packets to transmit, defaults to 5'
    version_help = 'check_ping.py, Version 1.0.0, 2017'

    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host', help=host_help, required=True)
    parser.add_argument('-w', '--warn', help=warn_help, required=True)
    parser.add_argument('-c', '--critical', help=critical_help, required=True)
    parser.add_argument('-t', '--timeout', help=timeout_help, required=False)
    parser.add_argument('-p', '--packets', help=packets_help, required=False)
    parser.add_argument('-v', '--version',
                        help=version_help, required=False)
    return parser.parse_args()


def main():
    """Main function"""
    args = do_argparser()

    if args.timeout:
        timeout = args.timeout
    else:
        timeout = '5'

    if args.packets:
        packets = args.packets
    else:
        packets = '5'

    ping = do_ping(packets, args.host, timeout)
    pktloss = get_packetloss(ping)
    rtt = get_rtt(ping)

    warn_pl = float(args.warn.split(',')[0])
    critical_pl = float(args.critical.split(',')[0])
    warn_rtt = float(args.warn.split(',')[1])
    critical_rtt = float(args.critical.split(',')[1])

    if pktloss >= critical_pl or rtt >= critical_rtt:
        print('CRITICAL: packet loss {0}%, rtt avg {1} ms'.format(pktloss, rtt))
        sys.exit(2)

    if pktloss >= warn_pl or rtt >= warn_rtt:
        print('WARNING: packet loss {0}%, rtt avg {1} ms'.format(pktloss, rtt))
        sys.exit(1)

    if pktloss < warn_pl and rtt < warn_rtt:
        print('OK: packet loss {0}%, rtt avg {1} ms'.format(pktloss, rtt))
        sys.exit(0)

if __name__ == "__main__":
    main()
