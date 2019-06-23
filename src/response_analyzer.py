#!/usr/bin/env python
from src import learner


class ResponseAnalyzer:

    def __init__(self, response_object):
        self.response_object = response_object

    def analyze_response(self, response):
        return