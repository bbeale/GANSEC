#!/usr/bin/env python
from src.learner import Learner


class PayloadGenerator:

    def __init__(self):
        # self.learner = Learner()
        self.attack_payloads = []

    def assemble_payload(self, data):

        payload_data = data
        payload = ""

        self.attack_payloads.append(payload)
