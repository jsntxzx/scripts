#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sqlite3
import argparse
import ipaddress

def valid_ip(address):
    parts = address.split(".")
    try:
        if len(parts) != 4:
            raise ValueError
        for item in parts:
            if not 0 <= int(item) <= 255:
                raise ValueError
        ret = get_location(address)
        print("The location of {0} is {1}".format(address, ret))
    except ValueError:
        msg = "Not a valid ip address: '{0}'.".format(address)
        raise argparse.ArgumentTypeError(msg)


def get_location(address):
    conn = sqlite3.connect("./misc/ipv4.db")
    with conn:
        c = conn.cursor()
        raw_address = int(ipaddress.IPv4Address(address))
        c.execute('select * from info where "raw_from" <= {0} and "raw_to" >= {0}'.format(raw_address))
        result = c.fetchone()
        if result:
            return result[2]
        else:
            return "UNKNOWN"




if __name__ == "__main__":
    description = "IP Location Query Tool"
    version = "1.0"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-v", "--version", action="version", version=version)
    parser.add_argument("-s", "--search", help="ip address string (i.e. 202.45.67.12)", metavar="ipv4_address", type=valid_ip, required=True)
    args = parser.parse_args()
