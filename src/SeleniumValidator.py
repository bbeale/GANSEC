#!/usr/bin/env python
# -*- coding: utf-8 -*-
from selenium.common.exceptions import UnexpectedAlertPresentException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver


class SeleniumValidator(webdriver):

    def __init__(self):
        super(webdriver, self).__init__()

    def validate_payload(self, html_path):
        """Load the HTML in a Selenium browser to see if the script executes.

        :param html_path:
        :return:
        """
        # if not web_driver or web_driver is None:
        #     raise GeneValidationException("[!] WebDriver reference required")

        if not html_path or html_path is None or not os.path.exists(html_path):
            raise GeneValidationException("[!] HTML path invalid or does not exist")

        result = dict()
        result["score"] = 0
        result["error"] = False

        # Refresh browser for next run
        try:
            web_driver.get(html_path)
            WebDriverWait(web_driver, 5).until(EC.presence_of_element_located((By.NAME, "testview")))
        except UnexpectedAlertPresentException as e:
            print("Alert!\ne:", e)
            result["score"] += 1

        except WebDriverException as e:
            print("Error\ne:", e)
            result["error"] = True

        return result


class SeleniumValidatorException(UnexpectedAlertPresentException, WebDriverException, WebDriverException):
    pass
