#!/usr/bin/env python
from learner import Learner


class PayloadGenerator:

    def __init__(self):
        self.attack_payloads = []

    def assemble_payload(self, data):

        payload_data = data
        payload = ""

        self.attack_payloads.append(payload)
