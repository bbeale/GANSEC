#!/usr/bin/env python
from src.PayloadGenerator import generate
import urllib.parse as urlparse
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import time
import os


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


def load_payloads_from_file(filepath):
    payloads = []
    try:
        with open(filepath, "r") as pf:
            payloads = [p for p in pf.readlines() if p not in payloads]
    except FileExistsError or FileNotFoundError as e:
        print(e)

    return payloads


class Scanner:
    def __init__(self, data):

        if data is None:
            raise ScannerValidationException("[!] data argument required")

        self.target_url         = data["url"]
        # self._test_payload3      = """<img style="width:100px; height:100px" src="" onmouseover="javascript:alert(document.cookie.toString())" />"""
        # self._test_payload2     = '" onmouseover="javascript:alert(1)" "'
        self._test_payload1      = "<script>alert(1);</script>"

        executable_path         = os.path.realpath(os.path.join("geckodriver"))
        self.driver             = webdriver.Firefox(executable_path=executable_path)
        self.session            = requests.Session()

        self.cookies            = None
        self.header             = None
        self.host               = None
        self.referer            = None
        self.username           = None
        self.passwd             = None
        self.ignore_link        = None
        self.sleeptime          = None

        self.target_links       = []
        self.fuzz_payloads      = []
        self.scan_results       = []
        self.fuzz_results       = []
        self.smart_payloads     = []

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

        if "Payloads" in data.keys():
            self.fuzz_payloads = load_payloads_from_file(data["Payloads"])

        if "sleep" in data.keys():
            self.sleeptime = data["sleep"]

        if self.cookies:
            for cookie in self.cookies:
                self.session.cookies.set(cookie[0], cookie[1])

        _headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Language": "en-US,en;q=0.5",
            "Upgrade-Insecure-Requests": "1",
            "Connection": "keep-alive",
        }

        if self.header is not None:
            nh = self.header.split(": ")
            _headers[nh[0]] = nh[1]

        self.session.headers.update(_headers)

    def generate_smart_payloads(self):
        # I will probably have better luck if I train the model on a proper data science machine with a GPU if I want to run the generator right here in the future
        self.smart_payloads = generate()

    def extract_links(self, url):
        if not url or url is None:
            raise ScannerValidationException("[!] a url is required")

        response = self.session.get(url)
        _links = []
        html = BeautifulSoup(response.text, features="html.parser")

        elements = html.findAll(lambda tag: len(tag.attrs) > 0 and "href" in tag.attrs)
        sources = html.findAll(lambda tag: len(tag.attrs) > 0 and "src" in tag.attrs)

        for element in elements:
            if self.ignore_link is None:
                if element.attrs["href"] not in _links:
                    _links.append(element.attrs["href"])
                    continue
            else:
                if self.ignore_link not in element.attrs["href"]:
                    if element.attrs["href"] not in _links:
                        _links.append(element.attrs["href"])
                        continue

                    if "http" not in element.attrs["href"]:
                        link = urlparse.urljoin(self.target_url, element.attrs["href"])
                        if link not in _links:
                            _links.append(link)
                            continue

        for source in sources:
            if self.ignore_link is None:
                if source.attrs["src"] not in _links:
                    _links.append(source.attrs["src"])
                    continue
            else:
                if self.ignore_link not in source.attrs["src"]:
                    if source.attrs["src"] not in _links:
                        _links.append(source.attrs["src"])
                        continue

                if "http" not in source.attrs["src"]:
                    link = urlparse.urljoin(self.target_url, source.attrs["src"])
                    if link not in _links:
                        _links.append(link)
                        continue

        links = []
        unables = []
        for link in _links:
            if url in link:
                links.append(link)
            else:
                if link and link[0] == "/":
                    n_url = urlparse.urljoin(url, link)
                    links.append(n_url)
                    continue
                elif link and link[0] != "/":
                    n_url = urlparse.urljoin(url, link)
                    links.append(n_url)
                    continue
                else:
                    unables.append(link)

        return links

    def extract_forms(self, url):
        if not url or url is None:
            raise ScannerValidationException("[!] a url is required")

        response = self.session.get(url)
        html = BeautifulSoup(response.text, features="html.parser")
        return html.findAll("form")

    def submit(self, form, value, url):
        if not form or form is None:
            raise ScannerValidationException("[!] a form is required")

        if value is None:
            raise ScannerValidationException("[!] a value is required")

        if not url or url is None:
            raise ScannerValidationException("[!] a url is required")

        action = form.get("action")
        p_url = urlparse.urljoin(url, action)
        method = form.get("method")

        inputs = form.findAll("input")
        p_data = dict()

        for i in inputs:
            i_name = i.get("name")
            i_type = i.get("type")
            i_value = i.get("value")
            if i_type == "text" or i_type == "hidden":
                p_data[i_name] = value

        if method == "post":
            response = self.session.post(p_url, data=p_data)

            # TODO
            if response.status_code == 302:
                print("Request was redirected")

        else:
            response = self.session.get(p_url, params=p_data)

            # TODO
            if response.status_code == 302:
                print("Request was redirected")

        return response

    def login(self, uname, pword, login_url=None):

        if not uname or uname is None:
            raise ScannerValidationException("[!] uname is required")

        if not pword or pword is None:
            raise ScannerValidationException("[!] pword is required")

        if not login_url or login_url is None:
            raise ScannerValidationException("[!] login_url is required")

        l_data = dict(
            username=uname,
            password=pword,
            login="LOGIN"
        )

        self.session.auth = (uname, pword)
        return self.session.post(urlparse.urljoin(self.target_url, login_url), data=l_data)

    def crawl(self, url=None):
        if url is None:
            url = self.target_url

        href_links = self.extract_links(url)
        for link in href_links:
            link = urlparse.urljoin(url, link)

            if "#" in link:
                link = link.split("#")[0]

            if self.target_url in link and link not in self.target_links and self.ignore_link not in link:
                self.target_links.append(link)
                print("Crawling link {}".format(link))
                self.crawl(link)

    def scan(self, url=None):
        if len(self.target_links) is 0 and url is not None:
            self.target_links.append(url)

        for link in self.target_links:
            forms = self.extract_forms(link)
            for form in forms:
                print("[+] Testing forms in {}".format(link))
                resp = self.form_xss_test(form, link)

                if resp["reflected"]:
                    res = "\n\n[***] XSS found in {} in form {}".format(link, form.name)
                    print(res)
                    self.scan_results.append(resp)

            if "=" in link:
                print("[+] Testing link: {}".format(link))
                resp = self.link_xss_test(link)

                if resp["reflected"]:
                    res = "\n\n[***] XSS found in {}".format(link)
                    self.scan_results.append(res)
                    print(res)
                    self.fuzz_results.append(resp)

                    if self.sleeptime is not None:
                        time.sleep(self.sleeptime)

    def link_xss_test(self, url, payload):
        if not url or url is None:
            raise ScannerValidationException("[!] a url is required to scan")

        if not payload or payload is None:
            raise ScannerValidationException("[!] a payload is required for the scanner to scan")

        url = url.replace("=", "={}".format(payload))
        reflected = False
        response = self.session.get(url)
        if payload in response.text:
            reflected = True
        return dict(
            response_text=response.text,
            reflected=reflected,
            status=response.status_code
        )

    def form_xss_test(self, form, url, payload):
        if not form or form is None:
            raise ScannerValidationException("[!] a form is required")

        if not url or url is None:
            raise ScannerValidationException("[!] a url is required to scan")

        if not payload or payload is None:
            raise ScannerValidationException("[!] a payload is required for the scanner to scan")


        reflected = False
        response = self.submit(form, payload, url)
        if payload in response.text:
            reflected = True
        return dict(
            response_text=response.text,
            reflected=reflected,
            status=response.status_code
        )

    def print_results(self):
        if len(self.scan_results) is 0 and len(self.fuzz_results) is 0:
            print("No XSS vulnerabilities found")
        elif len(self.scan_results) > 0:
            print("Scan results:\n\n")
            for res in self.scan_results:
                print(res)
            print("\tdone!")
        elif len(self.fuzz_results) > 0:
            print("Fuzz results:\n\n")
            for res in self.fuzz_results:
                print(res)
        print("\tdone")


class ScannerException(Exception):
    pass


class ScannerValidationException(ScannerException):
    pass
