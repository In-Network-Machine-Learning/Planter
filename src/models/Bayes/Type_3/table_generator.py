# THIS FILE IS PART OF Planter PROJECT
# Planter.py - The core part of the Planter library
#
# THIS PROGRAM IS FREE SOFTWARE TOOL, WHICH MAPS MACHINE LEARNING ALGORITHMS TO DATA PLANE, IS LICENSED UNDER Apache-2.0
# YOU SHOULD HAVE RECEIVED A COPY OF WTFPL LICENSE, IF NOT, PLEASE CONTACT THE FOLLOWING E-MAIL ADDRESSES
#
# Copyright (c) 2020-2021 Changgang Zheng
# Copyright (c) Computing Infrastructure Lab, Department of Engineering Science, University of Oxford
# E-mail: changgang.zheng@eng.ox.ac.uk or changgangzheng@qq.com
#
# Functions: This file is responsible for training, algorithm mapping, and software testing of the ML model.
#            Please refer to ./Docs/Planter_User_Document.pdf or further information.

import numpy as np
import pandas as pd
import argparse
import time

from sklearn.cluster import KMeans
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn import svm
from sklearn.metrics import *
from sklearn.svm import SVC
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import GaussianNB
import pydotplus
import copy
import math

import os
import sys
# import grpc
import json
from src.functions.Range_to_TCAM_Top_Down import *
from src.functions.normalization import *
from src.functions.json_encoder import *

def ten_to_bin(num,count):
    num = int(num)
    num = bin(num).lstrip('0b')

    if len(num) != count:
        cont = count - len(num)
        num = cont * '0' + num
    return num


def calculate_prob(input,feature_No, class_No, model_parmeters):#i is class
    part_1 = 1 / np.sqrt(2 * np.pi * model_parmeters['c'+str(class_No)]['f'+str(feature_No)]['std'] ** 2)
    part_2_u =   (input - model_parmeters['c'+str(class_No)]['f'+str(feature_No)]['mean']) ** 2
    part_2_l =  2 * (model_parmeters['c'+str(class_No)]['f'+str(feature_No)]['std'] ** 2)
    return part_1*np.exp(-part_2_u/part_2_l)




def run_model(train_X, train_y, test_X, test_y, used_features):
    config_file = 'src/configs/Planter_config.json'

    Planter_config = json.load(open(config_file, 'r'))
    Planter_config['model config']['number of bits'] = np.int(input('- Number of bits for each action data? (default = 16) ') or '16')
    Planter_config['model config']['number of classes'] = np.int(np.max(train_y) + 1)

    num_bits = Planter_config['model config']['number of bits']
    num_features = Planter_config['data config']['number of features']
    num_classes = Planter_config['model config']['number of classes']

    feature_names = []
    for i, f in enumerate(used_features):
        train_X.rename(columns={f: "f" + str(i)}, inplace=True)
        test_X.rename(columns={f: "f" + str(i)}, inplace=True)
        feature_names += ["f" + str(i)]
    feature_max = []
    for i in feature_names:
        t_t = [test_X[[i]].max()[0], train_X[[i]].max()[0]]
        feature_max += [np.max(t_t)+1]

    # =================== train model timer ===================
    Planter_config['timer log']['train model'] = {}
    Planter_config['timer log']['train model']['start'] = time.time()
    # =================== train model timer ===================

    # fit
    clf = GaussianNB()
    clf.fit(train_X, train_y)
    sklearn_y_predict = clf.predict(test_X)
    result = classification_report(test_y, sklearn_y_predict, digits=4)
    print('\n', result)

    # =================== train model timer ===================
    Planter_config['timer log']['train model']['end'] = time.time()
    # =================== train model timer ===================

    # =================== convert model timer ===================
    Planter_config['timer log']['convert model'] = {}
    Planter_config['timer log']['convert model']['start'] = time.time()
    # =================== convert model timer ===================


    model_parmeters={}
    for c in range(num_classes):
        model_parmeters['c'+str(c)] = {}
        for f in range(num_features):
            model_parmeters['c' + str(c)]["f"+str(f)] = {}
            model_parmeters['c' + str(c)]["f"+str(f)]['std'] = np.sqrt(clf.sigma_[c,f])
            model_parmeters['c' + str(c)]["f"+str(f)]['mean'] = clf.theta_[c,f]

    value_info = {}
    value_info["max"] = 0
    value_info["min"] = 0
    for f in range(num_features):
        value_info["f" + str(f)] = {}
        value_info["f"+str(f)]["max"] =  0
        value_info["f"+str(f)]["min"] =  0

    Bayes_separate_table = {}
    for f in range(num_features):
        Bayes_separate_table['feature '+str(f)] = {}
        for inputs in range(0,feature_max[f]+1):
            Bayes_separate_table['feature '+str(f)][inputs]={}
            for c in range(num_classes):
                if calculate_prob(inputs,f,c,model_parmeters)==0:
                    value = value_info["min"]
                else:
                    value = math.log(calculate_prob(inputs,f,c,model_parmeters),2)
                Bayes_separate_table['feature '+str(f)][inputs]["class "+str(c)] = value
                if value > value_info["max"]:
                    value_info["max"] = value
                if value < value_info["min"]:
                    value_info["min"] = value

    Bayes_separate_table["class prob"] = {}
    for c in range(num_classes):
        value = clf.class_prior_[c]
        Bayes_separate_table["class prob"]['class '+str(c)]= math.log(value,2)
        if value > value_info["max"]:
            value_info["max"] = value
        if value < value_info["min"]:
            value_info["min"] = value

    scale = (2**num_bits)/(num_features+1)
    Exact_Table = {}
    Exact_Table['class prob'] = {}
    for c in range(num_classes):
        min_x = value_info["min"]
        max_x = value_info["max"]
        x = copy.deepcopy(Bayes_separate_table['class prob']['class '+str(c)])
        value = Single_MaxMinNormalization(x, min_x, max_x)
        Exact_Table['class prob']['class '+str(c)] = np.int(np.round(value*scale))


    for f in range(num_features):
        Exact_Table['feature '+str(f)] = {}
        for inputs in range(0,feature_max[f]+1):
            Exact_Table['feature ' + str(f)][inputs] = {}
            for c in range(num_classes):
                min_x = value_info["min"]
                max_x = value_info["max"]
                x = Bayes_separate_table['feature '+str(f)][inputs]["class "+str(c)]
                value = Single_MaxMinNormalization(x, min_x, max_x)
                Exact_Table['feature '+str(f)][inputs]["class "+str(c)] = np.int(np.round(value*scale))

    # =================== convert model timer ===================
    Planter_config['timer log']['convert model']['end'] = time.time()
    # =================== convert model timer ===================

    json.dump(Exact_Table, open('Tables/Exact_Table.json', 'w'), indent=4)
    print('Exact_Table is generated')

    feature_tbl_len = []
    for f in range(num_features):
        feature_tbl_len += [len(Exact_Table['feature ' + str(f)].keys())]



    Planter_config['p4 config'] = {}
    Planter_config['p4 config']["model"] = "Bayes"
    Planter_config['p4 config']["number of features"] = num_features
    Planter_config['p4 config']["number of classes"] = num_classes
    Planter_config['p4 config']["action data bits"] = num_bits
    Planter_config['p4 config']['table name'] = 'Exact_Table.json'
    Planter_config['p4 config']["feature tbl len"] = feature_tbl_len
    Planter_config['test config'] = {}
    Planter_config['test config']['type of test'] = 'classification'


    json.dump(Planter_config, open(Planter_config['directory config']['work'] + '/src/configs/Planter_config.json', 'w'), indent=4, cls=NpEncoder)
    print(Planter_config['directory config']['work'] + '/src/configs/Planter_config.json is generated')

    return sklearn_y_predict.tolist()

def test_tables(sklearn_test_y, test_X, test_y):

    config_file = 'src/configs/Planter_config.json'
    Planter_config = json.load(open(config_file, 'r'))
    num_features = Planter_config['data config']['number of features']
    num_classes = Planter_config['model config']['number of classes']
    Exact_Table = json.load(open('Tables/Exact_Table.json', 'r'))

    print("Test the generated table")
    same = 0
    correct = 0
    error = 0
    switch_test_y = []

    for i in range(np.shape(test_X.values)[0]):
        input_feature_value = test_X.values[i]
        class_prob = np.zeros(num_classes).tolist()

        for c in range(num_classes):
            class_prob[c] = Exact_Table['class prob']['class '+str(c)]


        for f in range(num_features):
            for c in range(num_classes):
                class_prob[c] += Exact_Table['feature '+str(f)][str(input_feature_value[f])]['class '+str(c)]

        switch_prediction = class_prob.index(np.max(class_prob))
        switch_test_y += [switch_prediction]

        if switch_prediction == test_y[i]:
            correct += 1

        if switch_prediction == sklearn_test_y[i]:
            same += 1
        else:
            error += 1

        if i % 10 == 0 and i != 0:
            print(
                '\rswitch_prediction: {}, test_y: {}, with acc: {:.3}, with acc to sklearn: {:.4}, with error: {:.3}, M/A format macro f1: {:.3}, macro f1: {:.3}'.format(
                    switch_prediction, test_y[i], correct / (i + 1), same / (i + 1), error / (i + 1),
                    accuracy_score(switch_test_y[:i], test_y[:i]), accuracy_score(sklearn_test_y[:i], test_y[:i])),
                end="")
    print('\nThe accuracy of the match action format of Bayes is', correct / np.shape(test_X.values)[0])
    result = classification_report(test_y, switch_test_y, digits=4)
    print('\n', result)






def resource_prediction():
    config_file = 'src/configs/Planter_config.json'
    Planter_config = json.load(open(config_file, 'r'))

    Planter_config['resource info'] = {}



    tcam_per_stage = 1000
    exact_per_stage = 1000
    print('The predicted number of stages usage in table allocation:')