#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import random
import re
import time
import pandas as pd
from decimal import Decimal
from selenium.common.exceptions import UnexpectedAlertPresentException, WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from tidylib import tidy_fragment


class Gene:
    """
    An individual component in a genome to get passed around during mutation / replicative processes. Much like how genes work in living organisms.
    """
    genomes = None
    selection_status = None

    def __init__(self, genomes, selection_status):
        self.genomes = genomes
        self.selection_status = selection_status

    def get_genom(self):
        return self.genomes

    def get_selection_status(self):
        return self.selection_status

    def set_genom(self, genomes):
        """
        :param genomes:
        :return:
        """
        if not genomes or genomes is None:
            raise GeneValidationException("[!] Genomes are required")

        self.genomes = genomes

    def set_selection_status(self, status):
        """
        :param status:
        :return:
        """
        if not status or status is None:
            raise GeneValidationException("[!] Genomes are required")
        self.selection_status = status
