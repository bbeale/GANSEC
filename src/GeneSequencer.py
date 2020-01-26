#!/usr/bin/env python
# -*- coding: utf-8 -*-
from selenium.common.exceptions import UnexpectedAlertPresentException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from tidylib import tidy_fragment
from decimal import Decimal
from src.SeleniumValidator import SeleniumValidator
from src.Gene import Gene
import pandas as pd
import random
import time
import os
import re


def gene_to_str(gene, genes):
    """Convert a gene object to a string.

    :param gene:
    :param genes:
    :return:
    """
    if not gene or gene is None:
        raise GeneValidationException("[!] Invalid gene")

    if not genes or genes is None:
        raise GeneValidationException("[!] Invalid genes")

    indiv = ""
    for gene_num in genes:
        indiv += str(gene.loc[gene_num].values[0])
        indiv = indiv.replace("%s", " ").replace("&quot;", """) \
            .replace("%comma", ",").replace("&apos;", """)
    return indiv


class GeneSequencer:
    """
    This class does the work of running the genetic mutation and selection processes to determine the payloads that meet the fitness criteria.
    """
    def __init__(self, html_template, wd):

        if not html_template or html_template is None:
            raise SequencerValidationException("[!] Argument html_template not valid")

        if not wd or wd is None:
            raise SequencerValidationException("[!] WebDriver instance required.")
        
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
        """Return a gene object to represent an individual part of a genome.

        :param gene:
        :return:
        """
        if not gene or gene is None:
            raise SequencerValidationException("[!] gene is required.")

        genes = []
        for _ in range(self.genome_length):
            genes.append(random.randint(0, len(gene.index) - 1))
        return Gene(genes, 0)

    def natural_selection(self, generation, gene, eval_place, individual_i):
        """I don't have to be the be the fittest and fastest to survive -- I just have to be fitter and faster than YOU!

        :param generation:
        :param gene:
        :param eval_place:
        :param individual_i:
        :return:
        """
        if not generation or generation is None:
            raise SequencerValidationException("[!] generation is required.")

        if not gene or gene is None:
            raise SequencerValidationException("[!] gene is required.")

        if not eval_place or eval_place is None:
            raise SequencerValidationException("[!] eval_place is required.")

        if not individual_i or individual_i is None:
            raise SequencerValidationException("[!] individual_i is required.")

        sv = SeleniumValidator()
        indiv = gene_to_str(gene, generation.genomes)
        html = self.template.render({eval_place: indiv})
        eval_html_path = os.path.realpath(os.path.join(self.html_dir, self.html_file.replace("*", str(individual_i))))

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
        # result = test_payload_with_selenium(self.web_driver, str("file://" + eval_html_path))
        result = sv.validate_payload((self.web_driver, str("file://" + eval_html_path)))
        selenium_score = result["score"]
        if result["error"]:
            return None, 1

        if selenium_score > 0:
            print("[*] Found running script: \"{}\" in {}.".format(indiv, eval_place))
            int_score += self.bingo_score
            self.result_list.append([eval_place, generation.genomes, indiv])

        return int_score, 0

    def get_elites(self, generation):
        """Select the winners of the genetic selection process.

        :param generation:
        :return:
        """
        if not generation or generation is None:
            raise SequencerValidationException("[!] generation is required")

        sort_result = sorted(generation, reverse=True, key=lambda u: u.selection_status)

        return [sort_result.pop(0) for _ in range(self.select_genome)]

    def crossover(self, first_sequence, second_sequence):
        """Cross random genes between two sequences.

        :param first_sequence:
        :param second_sequence:
        :return:
        """
        if not first_sequence or first_sequence is None:
            raise SequencerValidationException("[!] first_sequence is required for genetic mutation")

        if not second_sequence or second_sequence is None:
            raise SequencerValidationException("[!] second_sequence is required for genetic mutation")

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

    def propogate(self, genes, elite_genes, offspring_genes):
        if not genes or genes is None:
            raise SequencerValidationException("[!] genes required.")

        if not elite_genes or elite_genes is None:
            raise SequencerValidationException("[!] elite_genes required.")

        if not offspring_genes or offspring_genes is None:
            raise SequencerValidationException("[!] offspring_genes required.")

        next_gen = sorted(genes, reverse=False, key=lambda u: u.selection_status)
        for _ in range(0, len(elite_genes) + len(offspring_genes)):
            if len(next_gen) > 0:
                next_gen.pop()

        next_gen.extend(elite_genes)
        next_gen.extend(offspring_genes)
        return next_gen

    def mutate(self, components, gene_pool):
        if not components or components is None:
            raise SequencerValidationException("[!] components require for mutationd")

        if not gene_pool or gene_pool is None:
            raise SequencerValidationException('[!] gene_pool required for mutation')

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
        """Run the genetic algorithm to populate the payloads.

        :return:
        """
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
            for indiv, i in enumerate(range(self.max_genomes)):

                selection_result, status = self.natural_selection(
                    current_generation[indiv], gene_pool, eval_place, i
                )

                i += 1
                if status == 1:
                    indiv -= 1
                    continue

                current_generation[indiv].set_selection_status(selection_result)
                time.sleep(self.wait)

            elite_genes = self.get_elites(current_generation)

            progeny_gene = []
            for i in range(0, self.select_genome):
                progeny_gene.extend(self.crossover(elite_genes[i - 1], elite_genes[i]))

            next_generation_individual_group = self.propogate(
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


class GeneException(Exception):
    pass


class GeneValidationException(GeneException):
    pass


class SequencerException(Exception):
    pass


class SequencerValidationException(SequencerException):
    pass
