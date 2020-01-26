#!/usr/bin/env python
# -*- coding: utf-8 -*-
from requests.exceptions import ConnectionError
from argparse import ArgumentParser
from src.Scanner import Scanner
import sys
import os


usage = """
    python gansec.py --url <url> (--fuzz | --crawl | --scan) [args]
"""


def main(args):

    parser = ArgumentParser()

    parser.add_argument("--url", help="A URL for scan entry point")
    parser.add_argument("--crawl", help="A URL for scan entry point")
    parser.add_argument("--scan", help="A URL for scan entry point")
    parser.add_argument("--fuzz", help="A URL for scan entry point")
    parser.add_argument("--gan", help="Generate payloads using a GAN")

    parser.add_argument("--Urls", help="A text file with a list of URLs to scan")
    parser.add_argument("--cookie", help="A cookie or semicolon delimited list of cookies to the session for an authenticated scan")
    parser.add_argument("--Cookies", help="A text file with a list of cookies to add")
    parser.add_argument("--header", help="A request header to add to the session")
    parser.add_argument("--Headers", help="A file with a list of request headers to add to the session")
    parser.add_argument("--host", help="Host header")
    parser.add_argument("--referer", help="Referer header")
    parser.add_argument("--username", help="A username")
    parser.add_argument("--password", help="A password")
    parser.add_argument("--ignore", help="A URL or semicolon delimited list of URLs to ignore")
    parser.add_argument("--Ignores", help="A file with a list of URLs to ignore")
    parser.add_argument("--payload", help="A custom payload; If not provided, will use the default")
    parser.add_argument("--Payloads", help="A text file with a list of custom payloads")

    scan_data = dict()

    if len(args) is 0:
        print(usage)
        sys.exit(-1)
    else:
        if args[0] != "--url":
            print(usage)
            sys.exit(-1)

        scan_data["url"] = args[args.index("--url") + 1]

        if "--Urls" in args:

            U_index = args.index("--Urls")
            if os.path.exists(os.path.realpath(args[U_index + 1])):
                _filepath = os.path.realpath(args[U_index + 1])
                scan_data["Urls"] = _filepath

        if "--cookie" in args:

            c_index = args.index("--cookie")
            scan_data["cookie"] = args[c_index + 1]

        if "--Cookies" in args:

            C_index = args.index("--Cookies")
            if os.path.exists(os.path.realpath(args[C_index + 1])):
                _filepath = os.path.realpath(args[C_index + 1])
                scan_data["Cookies"] = _filepath

        if "--header" in args:

            h_index = args.index("--header")
            scan_data["header"] = args[h_index + 1]

        if "--Headers" in args:

            H_index = args.index("--Headers")
            if os.path.exists(os.path.realpath(args[H_index + 1])):
                _filepath = os.path.realpath(args[H_index + 1])
                scan_data["Headers"] = _filepath

        if "--host" in args:

            ho_index = args.index("--host")
            scan_data["host"] = args[ho_index + 1]

        if "--referer" in args:

            r_index = args.index("--referer")
            scan_data["referer"] = args[r_index + 1]

        if "--username" in args:
            if "--password" not in args:
                print(usage)
                sys.exit(-1)

            u_index = args.index("--username")
            p_index = args.index("--password")

            scan_data["username"] = args[u_index + 1]
            scan_data["password"] = args[p_index + 1]

        if "--ignore" in args:

            i_index = args.index("--ignore")
            scan_data["ignore"] = args[i_index + 1]

        if "--Ignores" in args:

            I_index = args.index("--Ignores")
            if os.path.exists(os.path.realpath(args[I_index + 1])):
                _filepath = os.path.realpath(args[I_index + 1])
                scan_data["Ignores"] = _filepath

        if "--payload" in args:

            pl_index = args.index("--payload")
            scan_data["payload"] = args[pl_index + 1]

        if "--Payloads" in args:

            Pl_index = args.index("--Payloads")
            if os.path.exists(os.path.realpath(args[Pl_index + 1])):
                _filepath = os.path.realpath(args[Pl_index + 1])
                scan_data["Payloads"] = _filepath

        if "--sleep" in args:

            s_index = args.index("--sleep")
            scan_data["sleep"] = float(args[s_index + 1])

    try:
        vulnscanner = Scanner(scan_data)

        # if "--fuzz" in args and "--Payloads" in args:     # Forgot I took this out for now
        #     vulnscanner.fuzz(vulnscanner.fuzz_payloads)

        if "--gan" in args:
            vulnscanner.generate_smart_payloads()
        if "--crawl" in args and "--scan" not in args:
            vulnscanner.crawl(vulnscanner.target_url)
        elif "--scan" in args:
            vulnscanner.crawl(vulnscanner.target_url)
            vulnscanner.scan(vulnscanner.target_url)
        else:
            print("Invalid option\n", usage)
            sys.exit(-1)
    except ConnectionError as e:
        print(e)
        sys.exit(-1)
    vulnscanner.print_results()


if __name__ == "__main__":
    main(sys.argv[1:])
    print("[-] Done")
