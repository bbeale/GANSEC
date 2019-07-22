#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from selenium import webdriver
from jinja2 import Environment, FileSystemLoader
from src.gene_sequencer import GeneSequencer
from src.payload_discriminator import PayloadDiscriminator
from selenium.webdriver.firefox.options import Options


def main():
    print("Starting payload generation now... Please be patient.")

    html_dir = "html"
    html_template = "eval_template.html"

    max_try_num = 10
    window_width = 780
    window_height = 480
    position_width = 520
    position_height = 1

    env = Environment(loader=FileSystemLoader(html_dir))
    template = env.get_template(html_template)

    executable_path = os.path.realpath(os.path.join("geckodriver"))
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(executable_path=executable_path, options=options)
    driver.set_window_size(window_width, window_height)
    driver.set_window_position(position_width, position_height)

    for idx in range(max_try_num):
        sequencer = GeneSequencer(template, driver)
        individual_list = sequencer.genetic_algorithm()

    discriminator = PayloadDiscriminator(template, driver)
    res = discriminator.gan()

    with open(os.path.join("results", "gan_res.csv"), "w+") as results:
        results.writelines(res)

    driver.close()
    return res


if __name__ == "__main__":
    main()
