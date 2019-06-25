#!/usr/bin/env python
from src.scanner import Scanner
from requests.exceptions import ConnectionError
from argparse import ArgumentParser
import sys


usage = """
    python wafcat.py <url> [args]
"""


def main(args):

    parser = ArgumentParser()

    parser.add_argument("--url", help="A URL for scan entry point")
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

    scan_data = dict()

    if args is None:
        print(usage)
        sys.exit(-27)
    else:
        if args[0] != "--url":
            print(usage)
            sys.exit(-27)

        scan_data["url"] = args[args.index("--url") + 1]

        if "--cookie" in args:

            c_index = args.index("--cookie")
            scan_data["cookie"] = args[c_index + 1]

        if "--header" in args:

            h_index = args.index("--header")
            scan_data["header"] = args[h_index + 1]

        if "--host" in args:

            ho_index = args.index("--host")
            scan_data["host"] = args[ho_index + 1]

        if "--referer" in args:

            r_index = args.index("--referer")
            scan_data["referer"] = args[r_index + 1]

        if "--username" in args:
            if "--password" not in args:
                print(usage)
                sys.exit(-27)

            u_index = args.index("--username")
            p_index = args.index("--password")

            scan_data["username"] = args[u_index + 1]
            scan_data["password"] = args[p_index + 1]

        if "--ignore" in args:

            i_index = args.index("--ignore")
            scan_data["ignore"] = args[i_index + 1]

    try:
        vulnscanner = Scanner(scan_data)
    except ConnectionError as e:
        print(e.message)
        sys.exit(-1)
    vulnscanner.print_results()


if __name__ == "__main__":
    main(sys.argv[1:])
    print(".")

