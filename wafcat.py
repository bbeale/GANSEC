#!/usr/bin/env python
from src.scanner import Scanner
from requests.exceptions import ConnectionError
import sys


def main():
    try:
        vulnscanner = Scanner("", None)
    except ConnectionError as e:
        print(e.message)
        sys.exit(-1)
    vulnscanner.print_results()
    print(".")


if __name__ == "__main__":
    main()
