#!/usr/bin/env python
import requests
import urlparse
import re
from BeautifulSoup import BeautifulSoup

from payload_generator import PayloadGenerator


class Scanner:
    def __init__(self, url, links_to_ignore=None, cookies=None, username=None, passwd=None):
        self.session = requests.Session()
        self.url = url
        self.links = []
        self.links_to_ignore = links_to_ignore

        self.session.headers.update({
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0"
        })

        self.session.cookies(self.session.cookies.cookiejar_from_dict(cookies, cookiejar=None, overwrite=True))
        self.login(username, passwd)

        # todo: parse a file with a reqest in it aka captured from zaproxy to set headers and cookies

        self.crawl(self.url)
        self.scan(self.url)

    def extract_links(self, url):
        response = self.session.get(url)
        rex = """(?:^href|src=['"])(.*['"])"""
        return re.findall(rex, response.content)

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
        # todo: make this more generic

        l_data = dict(
            username=uname,
            password=pword,
            login="LOGIN"
        )

        self.session.auth = (uname, pword)
        return self.session.post(urlparse.urljoin(self.url, login_url), data=l_data)

    def crawl(self, url=None):
        if url is None:
            n_url = self.url
        else:
            n_url = url

        links = self.extract_links(n_url)
        for link in links:
            link = urlparse.urljoin(url, link)

            if "#" in link:
                link = link.split("#")[0]

            if url in link and link not in self.links:
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
