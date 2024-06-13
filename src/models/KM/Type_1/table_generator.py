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
from sklearn.metrics import *
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
import os
import sys
import copy
import json
from src.functions.Range_to_TCAM_Top_Down import *
from src.functions.normalization import *
from src.functions.json_encoder import *


def run_model(train_X, train_y, test_X, test_y, used_features):
    
    config_file = 'src/configs/Planter_config.json'

    Planter_config = json.load(open(config_file, 'r'))
    Planter_config = json.load(open(config_file, 'r'))
    Planter_config['model config']['number of bits'] = int(input('- Number of bits for each action data? (default = 16) ') or '16')
    Planter_config['model config']['random state'] = int(input('- What is the model random state? (default = 5) ') or '5')
    Planter_config['model config']['number of classes'] = int(np.max(train_y) + 1)

    random_state = Planter_config['model config']['random state']
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
        feature_max += [np.max(t_t) + 1]
    # print(feature_max)

    feature_min = []
    for i in feature_names:
        t_t = [test_X[[i]].min()[0], train_X[[i]].min()[0]]
        feature_min += [np.min(t_t) ]
    # print(feature_min)

    # =================== train model timer ===================
    Planter_config['timer log']['train model'] = {}
    Planter_config['timer log']['train model']['start'] = time.time()
    # =================== train model timer ===================

    # kmeans fit
    kmeans = KMeans(n_clusters=num_classes, random_state=random_state, n_init=random_state).fit(train_X,train_y)
    # kmeans = KMeans(n_clusters=num_classes, n_init=random_state).fit(train_X,train_y)
    

    sklearn_y_predict = kmeans.predict(test_X)
    result = classification_report(test_y, sklearn_y_predict, digits=4)
    print('\n', result)

    # =================== train model timer ===================
    Planter_config['timer log']['train model']['end'] = time.time()
    # =================== train model timer ===================

    # =================== convert model timer ===================
    Planter_config['timer log']['convert model'] = {}
    Planter_config['timer log']['convert model']['start'] = time.time()
    # =================== convert model timer ===================
    
    centre = kmeans.cluster_centers_
    
    # record the model
    outputfile = 'src/temp/Kmeans.txt'
    centers = {}
    model = open(outputfile,"w+")
    for c in range(len(centre)):
        model.write("centre point for class "+str(c)+" : \n")
        centers["c"+str(c)]={}
        model.write("(")
        for f in range(num_features):
            centers["c"+str(c)]['f'+str(f)] = centre[c][f]
            if f+1>=num_features:
                model.write('f' + str(f) + ': ' + str(centre[c][f]) + ")")
            else:
                model.write( 'f'+str(f)+': '+str(centre[c][f]) + ", " )
        model.write(";\n")
    model.close()
    
    Tables= {}
    value_info = {}
    value_info["max"] = 0
    for f in range(num_features):
        Tables['feature ' + str(f)] = {}
        x_m = np.mean(train_X[feature_names[f]])
        x_std = np.std(train_X[feature_names[f]])
        for input_value in range(feature_min[f], feature_max[f]):
            Tables['feature '+str(f)][input_value] = {}
            for c in range(num_classes):
                value = (centers["c"+str(c)]['f'+str(f)] - input_value) ** 2
                Tables['feature ' + str(f)][input_value]["c" + str(c)] = value
                if value>value_info["max"]:
                    value_info["max"] = value

    scale = (2**num_bits)/ (value_info["max"]*num_features)

    Exact_Table = {}
    for f in range(num_features):
        Exact_Table['feature ' + str(f)] = {}
        for input_value in range(feature_min[f], feature_max[f]):
            Exact_Table['feature ' + str(f)][input_value] = {}
            for c in range(num_classes):
                value = copy.deepcopy(Tables['feature ' + str(f)][input_value]["c" + str(c)])
                value = int(np.floor(value*scale))
                Exact_Table['feature ' + str(f)][input_value]["c" + str(c)] = value

    # =================== convert model timer ===================
    Planter_config['timer log']['convert model']['end'] = time.time()
    # =================== convert model timer ===================

    json.dump(Exact_Table, open('Tables/Exact_Table.json', 'w'), indent=4)
    print('Exact_Table is generated')

    feature_tbl_len = []
    for f in range(num_features):
        feature_tbl_len += [len(Exact_Table['feature ' + str(f)].keys())]

    Planter_config['p4 config'] = {}

    Planter_config['p4 config'] = {}
    Planter_config['p4 config']["model"] = "KM"
    Planter_config['p4 config']["number of features"] = num_features
    Planter_config['p4 config']["number of classes"] =  num_classes
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
        distance = np.zeros(num_classes).tolist()
        input_feature_value = test_X.values[i]
        for f in range (num_features):
            for c in range(num_classes):
                distance[c] += Exact_Table['feature ' + str(f)][str(input_feature_value[f])]["c"+str(c)]


        switch_prediction = distance.index(np.min(distance))
        switch_test_y += [switch_prediction]

        if switch_prediction == test_y[i]:
            correct += 1

        if switch_prediction == sklearn_test_y[i]:
            same += 1
        else:
            error += 1

        if i % 10 == 0 and i != 0:
            print(
                '\rswitch_prediction: {}, test_y: {}, with acc: {:.3}, with acc to sklearn: {:.4}, with error: {:.4}, M/A format macro f1: {:.3}, macro f1: {:.3}'.format(
                    switch_prediction, test_y[i], correct / (i + 1), same / (i + 1), error / (i + 1),
                    accuracy_score(switch_test_y[:i], test_y[:i]), accuracy_score(sklearn_test_y[:i], test_y[:i])),
                end="")


    print('\nThe accuracy of the match action format of Kmeans is', correct / np.shape(test_X.values)[0])
    result = classification_report(switch_test_y, test_y, digits=4)
    print('\n', result)


def resource_prediction():

    config_file = './src/configs/Planter_config.json'
    Planter_config = json.load(open(config_file, 'r'))

    print('Exact match entries: ',np.sum(Planter_config['p4 config']["feature tbl len"]) )


