# -*- coding=utf-8 -*-

#Implmentation of anmm model based on bin sum input of QA matrix

from __future__ import print_function
from __future__ import absolute_import
import keras
import keras.backend as K
from keras.models import Sequential, Model
from keras.layers import *
from keras.activations import softmax
from model import BasicModel
from utils.utility import *
from keras import backend as K
import tensorflow as tf
import numpy as np

class ANMM_linear(BasicModel):
    def __init__(self, config):
        super(ANMM_linear, self).__init__(config)
        self._name = 'ANMM_linear'
        self.check_list = [ 'text1_maxlen', 'bin_num',
                'embed', 'embed_size', 'vocab_size',
                'num_layers', 'hidden_sizes']
        self.setup(config)
        self.initializer_fc = keras.initializers.RandomUniform(minval=-0.1, maxval=0.1, seed=11)
        self.initializer_gate = keras.initializers.RandomUniform(minval=-0.01, maxval=0.01, seed=11)
        self.initializer_linear = keras.initializers.Constant(value=0.33333)
        if not self.check():
            raise TypeError('[ANMM] parameter check wrong')
        print('[ANMM] init done', end='\n')

    def setup(self, config):
        if not isinstance(config, dict):
            raise TypeError('parameter config should be dict:', config)

        self.set_default('text1_maxlen', 10)
        self.set_default('hist_size', 60)
        self.set_default('dropout_rate', 0.)
        self.config.update(config)

    def get_docz(self, doc):
        
        #show_layer_info(fieldname, doc)
        z = doc
        #z = Dropout(rate=self.config['dropout_rate'])(z)
        #show_layer_info('Dropout', z)
        for i in range(self.config['num_layers']-1):
            dense_layer = Dense(self.config['hidden_sizes'][i], kernel_initializer=self.initializer_fc)
            z = dense_layer(z)
            z = Activation('tanh')(z)
            #show_layer_info('Dense', z)
        dense_layer2 = Dense(self.config['hidden_sizes'][self.config['num_layers']-1], kernel_initializer=self.initializer_fc, activation="tanh")
        z = dense_layer2(z)
        #show_layer_info('Dense', z)
        z = Permute((2, 1))(z)
        #show_layer_info('Permute', z)
        z = Reshape((self.config['text1_maxlen'],))(z)
        #show_layer_info('z shape', z)
	return z

    def get_attention(self, query): 
        embedding = Embedding(self.config['vocab_size'], self.config['embed_size'], weights=[self.config['embed']], trainable = False)

        q_embed = embedding(query)
        #show_layer_info('Embedding', q_embed)
        q_w = Dense(1, kernel_initializer=self.initializer_gate, use_bias=False)(q_embed)
        #show_layer_info('Dense', q_w)
        q_w = Lambda(lambda x: softmax(x, axis=1), output_shape=(self.config['text1_maxlen'], ))(q_w)
        #show_layer_info('Lambda-softmax', q_w)
        q_w = Reshape((self.config['text1_maxlen'],))(q_w)
        #show_layer_info('q_w shape', q_w)
	return q_w

    def build(self):
        def tensor_product(x):
            a = x[0]
            b = x[1]
            y = K.batch_dot(a, b, axis=1)
            y = K.einsum('ijk, ikl->ijl', a, b)
            return y
        query = Input(name="query", shape=(self.config['text1_maxlen'],))
        title = Input(name="title", shape=(self.config['text1_maxlen'], self.config['bin_num']))
    	question = Input(name="question", shape=(self.config['text1_maxlen'], self.config['bin_num']))
        answer = Input(name="answer", shape=(self.config['text1_maxlen'], self.config['bin_num']))
        title_z = self.get_docz(title)
    	question_z = self.get_docz(question)
    	answer_z = self.get_docz(answer)
    	q_w = self.get_attention(query)
        out_title = Dot(axes= [1, 1])([title_z, q_w])
        out_question = Dot(axes = [1, 1])([question_z, q_w])
        out_answer = Dot(axes = [1, 1])([answer_z, q_w])
        K_param = K.constant(value=[[0.5, 0.3, 0.2]], dtype="float32")
        out_ = Concatenate()([out_title, out_question, out_answer])
        out_ = Lambda(lambda x: K.dot(x, K.transpose(K_param)), output_shape=(1,))(out_)
        model = Model(inputs=[query, title, question, answer], outputs=[out_])
        return model
