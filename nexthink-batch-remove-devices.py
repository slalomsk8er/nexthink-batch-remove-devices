#! /usr/bin/env python3
# -*- coding: utf-8; py-indent-offset: 4 -*-
#
# Author:  Dominik Riva, Universitätsspital Basel/Switzerland
# Contact: dominik (dot) riva (at) usb (dot) ch
#          https://www.unispital-basel.ch/
# License: The Unlicense, see LICENSE file.

"""Have a look at the README for further details
"""

import os
import argparse # pylint: disable=C0413
import sys # pylint: disable=C0413
import urllib3 # pylint: disable=C0413
import json
from urllib.parse import quote
from getpass import getpass


__author__ = """Dominik Riva, Universitätsspital Basel/Switzerland"""
__version__ = '2022052001'


DESCRIPTION = """This script reads one device per line from a file and sets a Category to be later abel to batch remove the devices in the Nexthink Finder."""

DEFAULT_ENGINES = ["one.engine.nexthink.example.com", "two.engine.nexthink.example.com"]
DEFAULT_CATEGORY = "to be removed"
DEFAULT_KEYWORD = "remove"
DEFAULT_TIMEOUT = 5

def parse_args():
    """Parse command line agruments using argparse.
    """
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument(
        '-V', '--version',
        action='version',
        version='{0}: v{1} by v{2}'.format('%(prog)s', __version__, __author__)
    )

    parser.add_argument(
        '--engines',
        help='Nexthink Engines. Default: %(default)s',
        dest='engines',
        nargs='+',
        default=DEFAULT_ENGINES,
    )

    parser.add_argument(
        '--category',
        help='Category, Default: %(default)s',
        dest='category',
        default=DEFAULT_CATEGORY,
    )

    parser.add_argument(
        '--keyword',
        help='Keyword of Category. Default: %(default)s',
        dest='keyword',
        default=DEFAULT_KEYWORD,
    )

    parser.add_argument(
        '--timeout',
        help='Network timeout in seconds. Default: %(default)s (seconds)',
        dest='timeout',
        type=int,
        default=DEFAULT_TIMEOUT,
    )

    parser.add_argument(
        '--device-list',
        help='text file - one device per line',
        dest='device_list',
        required=True,
    )

    return parser.parse_args()

def main():
    args = parse_args()
    
    # https://stackoverflow.com/a/42403360
    if sys.stdin.isatty():
        print("Enter credentials")
        username = input("Username: ")
        password = getpass("Password: ")
    else:
        username = sys.stdin.readline().rstrip()
        password = sys.stdin.readline().rstrip()

    http = urllib3.PoolManager()
    auth = '{}:{}'.format(username, password)
    headers = urllib3.make_headers(basic_auth=auth)

    with open(args.device_list, 'r') as devices:
        for device in devices:
            for engine in args.engines:
                #(update (set #"to be removed" (enum remove))
                #   (from device
                #       (where device
                #           (eq name (string "HOSTNAME"))
                url = 'https://{}:1671/2/query?platform=windows&query=(update%20(set%20%23%22{}%22%20(enum%20{}))%20(from%20device%20(where%20device%20(eq%20name%20(string%20%22{}%22))&hr=true&format=json'.format(
                    engine,
                    quote(args.category),
                    quote(args.keyword),
                    quote(device.strip()))
                #print(url)
                #sys.exit()
                resp = http.request(
                    'GET',
                    url,
                    headers=headers,
                    timeout=args.timeout
                )
                print(device.strip(), engine, resp.status, json.loads(resp.data))

if __name__ == '__main__':
	main()
