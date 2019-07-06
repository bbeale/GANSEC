#!/usr/bin/env python
import requests
import urllib.parse as urlparse
from bs4 import BeautifulSoup
import mechanize

from src.payload_generator import PayloadGenerator


def parse_cookie(cookie_string):
    if cookie_string is None:
        raise Exception("Must pass in a cookie string")
    _cookie = cookie_string.split("=")
    return _cookie[0].strip(), _cookie[1].strip(),


def parse_cookies(cookie_string=None, cookie_list=None):
    if cookie_string is not None and cookie_list is not None:
        raise Exception("One or the other: either a list of cookies or a cookie string")

    result = []
    if cookie_string is not None:
        result.append(parse_cookie(cookie_string))

    elif cookie_list is not None:
        for cookie in cookie_list:
            result.append(parse_cookie(cookie))
    return result


class Scanner:
    def __init__(self, data):

        self.target_url     = data["url"]
        self._test_payload  = """<img style="width:100px; height:100px" src="" onmouseover="javascript:alert(document.cookie.toString())" />"""
        # self._test_payload  = '" onmouseover="javascript:alert(1)" "'

        self.cookies        = None
        self.header         = None
        self.host           = None
        self.referer        = None
        self.username       = None
        self.passwd         = None
        self.ignore_link    = None

        if "cookie" in data.keys():
            self.cookies = parse_cookies(cookie_list=data["cookie"].split(";"))

        if "header" in data.keys():
            self.header = data["header"]

        if "host" in data.keys():
            self.host = data["host"]

        if "referer" in data.keys():
            self.referer = data["referer"]

        if "username" in data.keys() and "password" in data.keys():
            self.username = data["username"]
            self.password = data["password"]

        if "ignore" in data.keys():
            self.ignore_link = data["ignore"]

        # self.session = requests.Session()
        #
        # if self.cookies:
        #     for cookie in self.cookies:
        #         self.session.cookies.set(cookie[0], cookie[1])
        #
        # self.target_links = []
        #
        # _headers = {
        #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0",
        #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        #     "Content-Type": "application/x-www-form-urlencoded",
        #     "Accept-Language": "en-US,en;q=0.5",
        #     "Upgrade-Insecure-Requests": "1",
        #     "Connection": "keep-alive",
        # }
        #
        # if self.header is not None:
        #     nh = self.header.split(": ")
        #     _headers[nh[0]] = nh[1]
        #
        # self.session.headers.update(_headers)
        # self.crawl(self.target_url)
        #
        # # I think I want to generate payloads before the actual scan but after getting the Urls...
        # # I will need to pass in or reference the payloads,
        # # which I will generate once I have a picture of the attack surface
        # self.pg = PayloadGenerator()
        # self.scan_results = []
        # self.scan()

        browser = mechanize.Browser()
        resp = browser.open(self.target_url)
        print(resp.read())