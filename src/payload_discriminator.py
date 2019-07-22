#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import random
import numpy as np
import pandas as pd
from keras.optimizers import SGD
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.layers.advanced_activations import LeakyReLU
from keras.layers import Dropout
from keras import backend as K
from selenium.common.exceptions import UnexpectedAlertPresentException, WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


K.set_image_dim_ordering("th")


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

    try:
        web_driver.get(html_path)
        WebDriverWait(web_driver, 5).until(EC.presence_of_element_located((By.NAME, "testview")))
    except UnexpectedAlertPresentException as e:
        print("Alert!\ne:", e)
        result["score"] += 1

    except WebDriverException as e:
        print("Error!\ne:", e)
        result["error"] = True

    return result


class PayloadDiscriminator:
    def __init__(self, html_template, wd):
        
        self.template = html_template
        self.web_driver = wd

        full_path = os.path.dirname(os.path.abspath(__file__))

        self.result_dir = os.path.realpath(os.path.join(full_path, "result"))
        self.eval_html_path = os.path.realpath(os.path.join("html", "ga_eval_html_*.html"))
        self.gene_dir = os.path.realpath(os.path.join(full_path, "gene"))
        self.genes_path = os.path.realpath(os.path.join(self.gene_dir, "gene_list.csv"))
        self.ga_result_file = "ga_result_*.csv"
        self.genome_length = 5
        self.input_size = 200
        self.batch_size = 32
        self.num_epoch = 50
        self.max_sig_num = 10
        self.max_explore_codes_num = 1000  # 00
        self.max_synthetic_num = 1000
        self.weight_dir = os.path.realpath(os.path.join(full_path, "weight"))
        self.gen_weight_file = "generator_*.h5"
        self.dis_weight_file = "discriminator_*.h5"
        self.gan_result_file = "gan_result_*.csv"
        self.gan_vec_result_file = "gan_result_vec_*.csv"
        self.generator = None

        self.df_genes = pd.read_csv(self.genes_path, encoding="utf-8").fillna("")
        self.flt_size = len(self.df_genes) / 2.0

        self.weight_path = os.path.realpath(
            os.path.join(self.weight_dir, self.gen_weight_file.replace("*", str(self.num_epoch - 1))))

    def generator_model(self):
        model = Sequential()
        model.add(Dense(input_dim=self.input_size, output_dim=self.input_size * 10, init="glorot_uniform"))
        model.add(LeakyReLU(0.2))
        model.add(Dropout(0.5))
        model.add(Dense(self.input_size * 10, init="glorot_uniform"))
        model.add(LeakyReLU(0.2))
        model.add(Dropout(0.5))
        model.add(Dense(self.input_size * 5, init="glorot_uniform"))
        model.add(LeakyReLU(0.2))
        model.add(Dropout(0.5))
        model.add(Dense(output_dim=self.genome_length, init="glorot_uniform"))
        model.add(Activation("tanh"))
        return model

    def discriminator_model(self):
        model = Sequential()
        model.add(Dense(input_dim=self.genome_length, output_dim=self.genome_length * 10, init="glorot_uniform"))
        model.add(LeakyReLU(0.2))
        model.add(Dense(self.genome_length * 10, init="glorot_uniform"))
        model.add(LeakyReLU(0.2))
        model.add(Dense(1, init="glorot_uniform"))
        model.add(Activation("sigmoid"))
        return model

    def train(self, list_sigs):
        X_train = []
        X_train = np.array(list_sigs)
        X_train = (X_train.astype(np.float32) - self.flt_size) / self.flt_size

        discriminator = self.discriminator_model()
        d_opt = SGD(lr=0.1, momentum=0.1, decay=1e-5)
        discriminator.compile(loss="binary_crossentropy", optimizer=d_opt)

        discriminator.trainable = False
        self.generator = self.generator_model()
        dcgan = Sequential([self.generator, discriminator])
        g_opt = SGD(lr=0.1, momentum=0.3)
        dcgan.compile(loss="binary_crossentropy", optimizer=g_opt)

        num_batches = int(len(X_train) / self.batch_size)
        naughty_scripts = []
        for epoch in range(self.num_epoch):
            for batch in range(num_batches):

                noise = np.array([np.random.uniform(-1, 1, self.input_size) for _ in range(self.batch_size)])
                generated_codes = self.generator.predict(noise, verbose=0)

                image_batch = X_train[batch * self.batch_size:(batch + 1) * self.batch_size]
                X = image_batch
                y = [random.uniform(0.7, 1.2) for _ in range(self.batch_size)]
                d_loss = discriminator.train_on_batch(X, y)
                X = generated_codes
                y = [random.uniform(0.0, 0.3) for _ in range(self.batch_size)]
                d_loss = discriminator.train_on_batch(X, y)

                noise = np.array([np.random.uniform(-1, 1, self.input_size) for _ in range(self.batch_size)])
                g_loss = dcgan.train_on_batch(noise, [1] * self.batch_size)

                for generated_code in generated_codes:
                    genes = []
                    for gene_num in generated_code:
                        gene_num = (gene_num * self.flt_size) + self.flt_size
                        gene_num = int(np.round(gene_num))
                        if gene_num == len(self.df_genes):
                            gene_num -= 1
                        genes.append(int(gene_num))
                    str_html = gene_to_str(self.df_genes, genes)

                    eval_place = "body_tag"
                    html = self.template.render({eval_place: str_html})
                    with open(self.eval_html_path, "w", encoding="utf-8") as _html:
                        _html.write(html)

                    result = test_payload_with_selenium(self.web_driver, self.eval_html_path)

                    selenium_score = result["score"]
                    error_flag = result["error"]
                    if error_flag:
                        continue

                    if selenium_score > 0:
                        print("[!] Found running script: \"{}\" in {}.".format(str_html, eval_place))
                        naughty_scripts.append([eval_place, str_html])

            self.generator.save_weights(os.path.realpath(os.path.join(self.weight_dir, self.gen_weight_file.replace("*", str(epoch)))))
            discriminator.save_weights(os.path.realpath(os.path.join(self.weight_dir, self.dis_weight_file.replace("*", str(epoch)))))

        return naughty_scripts

    def code_to_gene(self, generated_code):
        genes = []
        for gene_num in generated_code:
            gene_num = (gene_num * self.flt_size) + self.flt_size
            gene_num = int(np.round(gene_num))
            if gene_num == len(self.df_genes):
                gene_num -= 1
            genes.append(int(gene_num))
        return genes

    def vector_mean(self, vector1, vector2):
        return (vector1 + vector2) / 2

    def gan(self):
        gan_save_path = os.path.realpath(os.path.join(self.result_dir, self.gan_result_file.replace("*", self.web_driver.name)))
        vec_save_path = os.path.realpath(os.path.join(self.result_dir, self.gan_vec_result_file.replace("*", self.web_driver.name)))

        if os.path.exists(self.weight_path):
            self.generator = self.generator_model()
            self.generator.load_weights("{}".format(self.weight_path))

            valid_code_list = []
            result_list = []
            for i in range(self.max_explore_codes_num):

                noise = np.array([np.random.uniform(-1, 1, self.input_size) for _ in range(1)])
                generated_codes = self.generator.predict(noise, verbose=0)
                str_html = gene_to_str(self.df_genes, self.code_to_gene(generated_codes[0]))

                eval_place = "body_tag"

                html = self.template.render({eval_place: str_html})
                with open(self.eval_html_path, "w", encoding="utf-8") as _html:
                    _html.write(html)

                result = test_payload_with_selenium(self.web_driver, self.eval_html_path)

                selenium_score = result["score"]
                error_flag = result["error"]

                if error_flag:
                    continue

                if selenium_score > 0:
                    print("[!] Found valid injection: \"{}\" in {}.".format(str_html, eval_place))
                    valid_code_list.append([str_html, noise])
                    result_list.append([eval_place, str_html])

            if os.path.exists(gan_save_path) is False:
                pd.DataFrame(result_list, columns=["eval_place", "injection_code"]).to_csv(
                    gan_save_path, mode="w", header=True, index=False)
            else:
                pd.DataFrame(result_list).to_csv(gan_save_path, mode="a", header=False, index=False)

            results = []
            for i in range(self.max_synthetic_num):
                noise_i1 = np.random.randint(0, len(valid_code_list))
                noise_i2 = np.random.randint(0, len(valid_code_list))

                noise = self.vector_mean(valid_code_list[noise_i1][1], valid_code_list[noise_i2][1])
                generated_codes = self.generator.predict(noise, verbose=0)
                str_html = gene_to_str(self.df_genes, self.code_to_gene(generated_codes[0]))

                eval_place = "body_tag"
                script_exec = False
                html = self.template.render({eval_place: str_html})
                with open(self.eval_html_path, "w", encoding="utf-8") as _html:
                    _html.write(html)

                result = test_payload_with_selenium(self.web_driver, self.eval_html_path)

                selenium_score = result["score"]
                error_flag = result["error"]

                if error_flag:
                    continue

                if selenium_score > 0:
                    print("[!] Found running script: \"{}\".".format(str_html))
                    script_exec = True

                results.append(
                    [eval_place, str_html, valid_code_list[noise_i1][0], valid_code_list[noise_i2][0],
                     script_exec])

            if os.path.exists(vec_save_path) is False:
                pd.DataFrame(results, columns=[
                    "eval_place",
                    "synthesized_code",
                    "origin_code1",
                    "origin_code2",
                    "bingo"]).to_csv(vec_save_path, mode="w", header=True, index=False)
            else:
                pd.DataFrame(results).to_csv(vec_save_path, mode="a", header=False, index=False)
        else:
            sig_path = os.path.realpath(
                os.path.join(self.result_dir, self.ga_result_file.replace("*", self.web_driver.name)))
            df_temp = pd.read_csv(sig_path, encoding="utf-8").fillna("")
            df_sigs = df_temp[~df_temp.duplicated()]

            list_sigs = []
            for i in range(len(df_sigs)):
                list_temp = df_sigs["sig_vector"].values[i].replace("[", "").replace("]", "").split(",")
                list_sigs.append([int(s) for s in list_temp])

            naughty_scripts = []
            target_sig_list = []
            for target_sig in list_sigs:
                target_sig_list.extend([target_sig for _ in range(self.max_sig_num)])
            naughty_scripts.extend(self.train(target_sig_list))

            if os.path.exists(gan_save_path) is False:
                pd.DataFrame(naughty_scripts, columns=["eval_place", "injection_code"]).to_csv(
                    gan_save_path, mode="w", header=True, index=False)
            else:
                pd.DataFrame(naughty_scripts).to_csv(gan_save_path, mode="a", header=False, index=False)


# %%
# html_dir = os.path.realpath("html")
# html_template = "eval_template.html"
# env = Environment(loader=FileSystemLoader(html_dir))
# template = env.get_template(html_template)
# %%0
# executable_path=os.path.realpath(os.path.join("geckodriver"))
# options = Options()
# options.headless = True
# driver = webdriver.Firefox(executable_path=executable_path, options=options)
# %%
# generator = GeneticAlgorithm(template, driver)
# %%
# generator.main()
# %%
