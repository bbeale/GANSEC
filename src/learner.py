#!/usr/bin/env python
# coding=utf-8
import tensorflow as tf


class Learner:

    def __init__(self):

        # Don't know what these numbers actually mean ¯\_(ツ)_/¯ just grabbed them from a tutuorial to start with
        self.learning_rate = 0.001
        self.n_input = 784
        self.n_hidden_1 = 256
        self.n_hidden_2 = 256
        self.n_classes = 10

        self.weights = {
            "h1": tf.Variable(tf.random_normal([self.n_input, self.n_hidden_1])),
            "h2": tf.Variable(tf.random_normal([self.n_hidden_1, self.n_hidden_2])),
            "out": tf.Variable(tf.random_normal([self.n_hidden_2, self.n_classes]))
        }

        self.biases = {
            "b1": tf.Variable(tf.random_normal([self.n_hidden_1])),
            "b2": tf.Variable(tf.random_normal([self.n_hidden_2])),
            "out": tf.Variable(tf.random_normal([self.n_classes]))
        }

        x = tf.placeholder("float", [None, self.n_input])
        y = tf.placeholder("float", [None, self.n_classes])

        self.prediction = self.multilayer_perceptron(x, self.weights, self.biases)

        self.cost = tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(self.prediction, y))
        self.optimizer = tf.train.AdamOptimizer(learning_rate=self.learning_rate).minimize(self.cost)

    def multilayer_perceptron(self, x, weights, biases):

        layer_1 = tf.add(tf.matmul(x, weights["h1"]), biases["b1"])
        layer_1 = tf.nn.relu(layer_1)

        layer_2 = tf.add(tf.matmul(layer_1, weights["h2"]), biases["b2"])
        layer_2 = tf.nn.relu(layer_2)

        out_layer = tf.matmul(layer_2, weights["out"] + biases["out"])
        return out_layer
