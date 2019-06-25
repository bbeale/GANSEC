#!/usr/bin/env python
import requests
import urlparse
import re
from BeautifulSoup import BeautifulSoup

from payload_generator import PayloadGenerator


class Scanner:
    def __init__(self, data):

        self.url            = data["url"]

        self.cookies        = None
        self.header         = None
        self.host           = None
        self.referer        = None
        self.username       = None
        self.passwd         = None
        self.ignore_links   = None

        if "cookie" in data.keys():
            self.cookies = self.parse_cookies(cookie_list=data["cookie"].split(";"))

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
            self.ignore_links = data["ignore"]

        self.session = requests.Session()

        for cookie in self.cookies:
            self.session.cookies.set(cookie[0], cookie[1])
            print(".")


        for cookie in self.cookies:
            self.session.cookies.set(cookie[0], cookie[1])

        self.links = []

        _headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Language": "en-US,en;q=0.5",
            "Upgrade-Insecure-Requests": "1",
            "Connection": "keep-alive",
            "DNT": "1",
        }

        if self.header is not None:
            nh = self.header.split(": ")
            _headers[nh[0]] = nh[1]

        self.session.headers.update(_headers)

        self.crawl(self.url)
        self.scan(self.url)

    def _parse_cookie(self, cookie_string):
        if cookie_string is None:
            raise Exception("Must pass in a cookie string")
        _cookie = cookie_string.split("=")
        return _cookie[0].strip(), _cookie[1].strip(),

    def parse_cookies(self, cookie_string=None, cookie_list=None):
        if cookie_string is not None and cookie_list is not None:
            raise Exception("One or the other: either a list of cookies or a cookie string")

        result = []

        if cookie_string is not None:
            result.append(self._parse_cookie(cookie_string))

        elif cookie_list is not None:

            for cookie in cookie_list:
                result.append(self._parse_cookie(cookie))

        return result

    def extract_links(self, url):
        response = self.session.get(url)
        rex = """(?:^href|src=['"])(.*[""'])"""
        links = re.findall(rex, response.content.decode("utf-8"))
        return [link.strip('"') for link in links]

    def extract_forms(self, url):
        response = self.session.get(url)
        html = BeautifulSoup(response.content)
        return html.findAll("form")

    def submit(self, form, value, url):
        action = form.get("action")
        p_url = urlparse.urljoin(url, action)
        method = form.get("method")

        inputs = form.findAll("input")
        p_data = dict()

        for i in inputs:
            i_name = i.get("name")
            i_type = i.get("type")
            i_value = i.get("value")
            if i_type == "text":
                i_value = value

            p_data[i_name] = i_value

        if method == "post":
            response = self.session.post(p_url, data=p_data)
        else:
            response = self.session.get(p_url, params=p_data)
        return response

    def login(self, uname, pword, login_url=None):

        l_data = dict(
            username=uname,
            password=pword,
            login="LOGIN"
        )

        self.session.auth = (uname, pword)
        return self.session.post(urlparse.urljoin(self.url, login_url), data=l_data)

    def crawl(self, url=None):
        if url is None:
            url = self.url

        links = self.extract_links(url)
        for link in links:
            link = urlparse.urljoin(url, str(link))

            if "#" in link:
                link = link.split("#")[0]

            if link not in self.links:
                self.links.append(link)
                self.crawl(link)

    def scan(self, url=None):
        if url is None:
            url = self.url

        for link in self.links:
            forms = self.extract_forms(link)
            for form in forms:
                print("[+] Testing forms in {}".format(link))
                if self.form_xss_test(form, url):
                    print("\n\n[***] XSS found in {} in form {}".format(link, form))

            if "=" in link:
                print("[+] Testing link: {}".format(link))
                if self.link_xss_test(url):
                    print("\n\n[***] XSS found in {}".format(link))

    def link_xss_test(self, url=None, payload=None):
        if url is None:
            url = self.url
        if payload is None:
            payload = "<script>alert(\"boo\")</script>"
        url = url.replace("=", "={}".format(payload))
        response = self.session.get(url)
        return payload in response.content

    def form_xss_test(self, form, url, payload=None):
        if url is None:
            url = self.url

        if payload is None:
            payload = "<script>alert(\"boo\")</script>"
        response = self.submit(form, payload, url)
        return payload in response.content

    def print_results(self):
        print("Not yet implemented")
