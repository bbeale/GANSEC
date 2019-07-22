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


def gene_to_str(gene, genes):
    indiv = ""
    for gene_num in genes:
        indiv += str(gene.loc[gene_num].values[0])
        indiv = indiv.replace("%s", " ").replace("&quot;", """) \
            .replace("%comma", ",").replace("&apos;", """)
    return indiv


def test_payload_with_selenium(web_driver, html_path):
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


class Gene:
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
        self.genomes = genomes

    def set_selection_status(self, status):
        self.selection_status = status


# The Genetic Algorithm
class GeneSequencer:
    def __init__(self, html_template, wd):
        
        self.template = html_template
        self.web_driver = wd

        full_path = os.path.dirname(os.path.abspath(__file__))

        self.wait = 0.0
        self.html_dir = "html"
        self.html_template_path = os.path.realpath(os.path.join(self.html_dir, "eval_template.html"))
        self.html_file = "ga_eval_html_*.html"
        self.result_dir = os.path.realpath(os.path.join(full_path, "result"))

        self.genome_length = 5
        self.max_genomes = 10
        self.select_genome = 10
        self.mutation_rate = 0.3
        self.genome_mutation_rate = 0.7
        self.max_generation = 1000
        self.max_fitness = 1
        self.gene_dir = os.path.realpath(os.path.join(full_path, "gene"))
        self.genes_path = os.path.realpath(os.path.join(self.gene_dir, "gene_list.csv"))
        self.html_checked_path = os.path.realpath(os.path.join(self.html_dir, "html_checked_result.txt"))
        self.bingo_score = 3.0
        self.warning_score = -0.1
        self.error_score = -0.5
        self.result_file = "ga_result_*.csv"
        self.result_list = []

    def create_genome(self, gene):
        genes = []
        for _ in range(self.genome_length):
            genes.append(random.randint(0, len(gene.index) - 1))
        return Gene(genes, 0)

    def natural_selection(self, generation, gene, eval_place, individual_idx):
        indiv = gene_to_str(gene, generation.genomes)
        html = self.template.render({eval_place: indiv})
        eval_html_path = os.path.realpath(os.path.join(self.html_dir, self.html_file.replace("*", str(individual_idx))))

        with open(eval_html_path, "w", encoding="utf-8") as _html:
            _html.write(html)

        payload, errors = tidy_fragment(html)

        warnings = len(re.findall(r"(Warning)\W", errors))
        errors = len(re.findall(r"(Error)\W", errors))

        if warnings > 0:
            warnings = float(warnings) * -0.2  # -0.1
        if errors > 0:
            errors = float(errors) * -1.1  # -1.0
        else:
            return None, 1

        int_score = warnings + errors
        result = test_payload_with_selenium(self.web_driver, str("file://" + eval_html_path))
        selenium_score = result["score"]
        if result["error"]:
            return None, 1

        if selenium_score > 0:
            print("[*] Found running script: \"{}\" in {}.".format(indiv, eval_place))
            int_score += self.bingo_score
            self.result_list.append([eval_place, generation.genomes, indiv])

        return int_score, 0

    def get_elites(self, generation):
        sort_result = sorted(generation, reverse=True, key=lambda u: u.selection_status)

        return [sort_result.pop(0) for _ in range(self.select_genome)]

    def crossover(self, first_sequence, second_sequence):
        genomes = []
        cross_first = random.randint(0, self.genome_length)
        cross_second = random.randint(cross_first, self.genome_length)
        one = first_sequence.get_genome()
        second = second_sequence.get_genome()
        progeny_one = one[:cross_first] + second[cross_first:cross_second] + one[cross_second:]
        progeny_second = second[:cross_first] + one[cross_first:cross_second] + second[cross_second:]
        genomes.append(Gene(progeny_one, 0))
        genomes.append(Gene(progeny_second, 0))
        return genomes

    def propogate_next(self, genes, elite_genes, ga_progeny):
        next_generation_geno = sorted(genes, reverse=False, key=lambda u: u.selection_status)
        for _ in range(0, len(elite_genes) + len(ga_progeny)):
            if len(next_generation_geno) > 0:
                next_generation_geno.pop()

        next_generation_geno.extend(elite_genes)
        next_generation_geno.extend(ga_progeny)
        return next_generation_geno

    def mutate(self, components, gene_pool):

        mutation = []
        for component in components:
            if self.mutation_rate > (random.randint(0, 100) / Decimal(100)):
                genes = []
                for _component in component.get_genome():
                    if self.genome_mutation_rate > (random.randint(0, 100) / Decimal(100)):
                        genes.append(random.randint(0, len(gene_pool.index) - 1))
                    else:
                        genes.append(_component)
                component.set_genome(genes)
                mutation.append(component)
            else:
                mutation.append(component)
        return mutation

    def genetic_algorithm(self):
        gene_pool = pd.read_csv(self.genes_path, encoding="utf-8").fillna("")

        save_path = os.path.realpath(os.path.join(self.result_dir, self.result_file.replace("*", self.web_driver.name)))
        if os.path.exists(save_path) is False:
            pd.DataFrame([], columns=["eval_place", "sig_vector", "sig_string"]).to_csv(
                save_path, mode="w", header=True, index=False)

        eval_place = "body_tag"
        current_generation = []
        for _ in range(self.max_genomes):
            current_generation.append(self.create_genome(gene_pool))
            
        elite_genes = []
        for int_count in range(1, self.max_generation + 1):
            for indiv, idx in enumerate(range(self.max_genomes)):

                selection_result, status = self.natural_selection(
                    current_generation[indiv], gene_pool, eval_place, idx
                )

                idx += 1
                if status == 1:
                    indiv -= 1
                    continue

                current_generation[indiv].set_selection_status(selection_result)
                time.sleep(self.wait)

            elite_genes = self.get_elites(current_generation)

            progeny_gene = []
            for i in range(0, self.select_genome):
                progeny_gene.extend(self.crossover(elite_genes[i - 1], elite_genes[i]))

            next_generation_individual_group = self.propogate_next(
                current_generation, elite_genes, progeny_gene)

            next_generation_individual_group = self.mutate(next_generation_individual_group, gene_pool)
            selection_statuses = [_.get_selection_status() for _ in current_generation]
            flt_avg = sum(selection_statuses) / float(len(selection_statuses))
            if flt_avg > self.max_fitness:
                break

            current_generation = next_generation_individual_group

        pd.DataFrame(self.result_list).to_csv(save_path, mode="a", header=True, index=False)

        contender = ""
        for gene_num in elite_genes[0].get_genome():
            contender += str(gene_pool.loc[gene_num].values[0])
        contender = contender.replace("%s", " ").replace("&quot;", '"').replace("%comma", ",")
        print("[+] Best individual : \"{}\"".format(contender))

        return self.result_list
