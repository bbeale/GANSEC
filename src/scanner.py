#!/usr/bin/env python
import requests
import urllib.parse as urlparse
from bs4 import BeautifulSoup

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

        self.url            = data["url"]
        self._test_payload  = '<img style="width:100px; height:100px" src="" onmouseover="javascript:alert(document.cookie.toString())" />'
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

        self.session = requests.Session()

        if self.cookies:
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
        }

        if self.header is not None:
            nh = self.header.split(": ")
            _headers[nh[0]] = nh[1]

        self.session.headers.update(_headers)
        self.crawl(self.url)

        # I think I want to generate payloads before the actual scan but after getting the Urls...
        # I will need to pass in or reference the payloads,
        # which I will generate once I have a picture of the attack surface
        self.pg = PayloadGenerator()
        self.scan_results = []
        self.scan(self.url)

    def extract_links(self, url):
        response = self.session.get(url)
        _links = []
        html = BeautifulSoup(response.text, features="html.parser")

        elements = html.findAll(lambda tag: len(tag.attrs) > 0 and "href" in tag.attrs)

        for element in elements:
            if self.ignore_link is None:
                _links.append(element.attrs["href"])
                continue
            elif self.ignore_link is not None and self.ignore_link not in element.attrs["href"]:
                _links.append(element.attrs["href"])
                continue
            else:
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
        response = self.session.get(url)
        html = BeautifulSoup(response.text, features="html.parser")
        return html.findAll("form")

    # TODO: Perhaps this should take an input instead of a whole form
    def submit(self, form, value, url):
        action = form.get("action")
        p_url = urlparse.urljoin(url, action)
        method = form.get("method")

        inputs = form.findAll("input")
        p_data = dict()

        responses = []
        payload_set = False
        for i in inputs:
            i_name = i.get("name")
            i_type = i.get("type")
            i_value = i.get("value")

            p_data[i_name] = i_value

            if payload_set:
                continue

            if i_type == "text" or i_type == "hidden":
                p_data[i_name] = value
                payload_set = True

        if method == "post":
            response = self.session.post(p_url, data=p_data)





            # TODO

            if response.status_code == 302:
                print("Request was redirected")

            responses.append(response.text)
        else:
            response = self.session.get(p_url, params=p_data)
            if response.status_code == 302:
                print("Request was redirected")

            responses.append(response.text)
        return responses

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
            print("Crawling link {}".format(link))
            link = urlparse.urljoin(url, str(link))

            if "#" in link:
                link = link.split("#")[0]

            if link not in self.links:
                self.links.append(link)
                self.crawl(link)

    def scan(self, url=None):
        if url is None:
            url = self.url

        if url not in self.links:
            self.links.append(url)

        for link in self.links:
            forms = self.extract_forms(link)
            for form in forms:
                print("[+] Testing forms in {}".format(link))
                if self.form_xss_test(form, link):
                    res = "\n\n[***] XSS found in {} in form {}".format(link, form)
                    self.scan_results.append(res)
                    print(res)

            if "=" in link:
                print("[+] Testing link: {}".format(link))
                if self.link_xss_test(link):
                    res = "\n\n[***] XSS found in {}".format(link)
                    self.scan_results.append(res)
                    print(res)

    def link_xss_test(self, url=None, payload=None):
        if url is None:
            url = self.url
        if payload is None:
            payload = self._test_payload
        url = url.replace("=", "={}".format(payload))
        response = self.session.get(url)
        return payload in response.text

    def form_xss_test(self, form, url, payload=None):
        if url is None:
            url = self.url
        # todo: I think I am going to want to parse the form inputs here instead, so I can test them one at a time
        if payload is None:
            payload = self._test_payload
        responses = self.submit(form, payload, url)
        return True in [payload in response.text for response in responses]

    def print_results(self):
        print("--Not yet implemented --\n\nScan results: ", self.scan_results)
