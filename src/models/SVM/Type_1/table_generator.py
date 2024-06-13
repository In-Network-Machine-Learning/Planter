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
from sklearn.linear_model import SGDClassifier
import math

import os
import sys
# import grpc
import json
from src.functions.json_encoder import *
from src.functions.normalization import *




def ten_to_bin(num,count):
    num= num.astype(np.int)
    num = bin(num).lstrip('0b')

    if len(num) != count:
        cont = count - len(num)
        num = cont * '0' + num
    return num


def votes_to_class(class_num, vote_list, num_votes, num_classes, g_table, num):
    if class_num  == num_classes:
        if np.sum(vote_list) == num_votes:
            g_table['decision'][num] = {}
            for c in range(num_classes):
                g_table['decision'][num]['c'+str(c)+' vote'] = vote_list[c]
            g_table['decision'][num]['class'] = vote_list.index(np.max(vote_list))
            num += 1
        return g_table, num
    else:
        for v in range(num_votes+1):
            vote_list[class_num] = v
            class_num += 1
            g_table, num = votes_to_class(class_num, vote_list, num_votes, num_classes, g_table, num)
            class_num -= 1
    return g_table, num

def run_model(train_X, train_y, test_X, test_y, used_features):
    config_file = 'src/configs/Planter_config.json'

    Planter_config = json.load(open(config_file, 'r'))
    Planter_config['model config']['number of bits'] = np.int(input('- Number of bits for each action data? (default = 16) ') or '16')
    Planter_config['model config']['number of classes'] = np.int(np.max(train_y) + 1)


    num_bits = Planter_config['model config']['number of bits']
    num_features = Planter_config['data config']['number of features']
    num_classes = Planter_config['model config']['number of classes']
    num_hps = np.int(num_classes * (num_classes - 1) / 2)



    feature_names = []
    for i, f in enumerate(used_features):
        train_X.rename(columns={f: "f"+str(i)}, inplace=True)
        test_X.rename(columns={f: "f" + str(i)}, inplace=True)
        feature_names+=["f"+str(i)]
    
    feature_max = []
    for i in feature_names:
        t_t = [test_X[[i]].max()[0], train_X[[i]].max()[0]]
        feature_max += [max(t_t)]

    # =================== train model timer ===================
    Planter_config['timer log']['train model'] = {}
    Planter_config['timer log']['train model']['start'] = time.time()
    # =================== train model timer ===================

    #SVM instance
    SVM = SVC(kernel = 'linear')
    SVM.fit(train_X, train_y)
    sklearn_y_predict = SVM.predict(test_X)
    result = classification_report(test_y, sklearn_y_predict, digits=4)
    print('\n', result)

    # =================== train model timer ===================
    Planter_config['timer log']['train model']['end'] = time.time()
    # =================== train model timer ===================

    # =================== convert model timer ===================
    Planter_config['timer log']['convert model'] = {}
    Planter_config['timer log']['convert model']['start'] = time.time()
    # =================== convert model timer ===================

    coe = SVM.coef_
    int = SVM.intercept_
    
    
    outputfile = 'src/temp/svm.txt'
    model = open(outputfile,"w+")
    for i in range(len(coe)):
        model.write("hyperplane"+str(i)+" = ")
        for f in range(num_features):
            model.write(str(coe[i][f]) + "x"+str(f+1)+" + ")
        model.write(str(int[i]))
        model.write(";\n")
    model.close()
    
    # Table without fitting to switch
    SVM_separate_table = {}

    value_info = {}
    for hp in range(num_hps):
        SVM_separate_table["bias hp"+str(hp)]=int[hp]
        value_info["hp "+str(hp)] = {}
        value_info["hp " + str(hp)]["max"] = int[hp]
        value_info["hp " + str(hp)]["min"] = int[hp]



    for i,fn in enumerate(feature_names):

        SVM_separate_table[fn] = {}
        for feature in range(feature_max[i]+1):
            SVM_separate_table[fn][feature] = {}
            for hp in range(num_hps):
                middle_value = coe[hp][i] * feature
                SVM_separate_table[fn][feature]["hp "+str(hp)] = middle_value
                if middle_value > value_info["hp " + str(hp)]["max"]:
                    value_info["hp " + str(hp)]["max"] = middle_value
                if middle_value < value_info["hp " + str(hp)]["min"]:
                    value_info["hp " + str(hp)]["min"] = middle_value

    for hp in range(num_hps):
        SVM_separate_table['threshold hp'+str(hp)] = 0

    # Table fit to switch
    scale = np.floor((2**num_bits)/ (value_info["hp " + str(hp)]["max"] - value_info["hp " + str(hp)]["min"])/num_features)
    Exact_Table = {}

    print("Generating decision table...", end="")
    Exact_Table['decision'] = {}
    Exact_Table, _ = votes_to_class(0, np.zeros(num_classes).tolist(), num_hps, num_classes, Exact_Table, 0)
    print('Done')

    for hp in range(num_hps):
        x = SVM_separate_table["bias hp"+str(hp)]
        min_x = value_info["hp " + str(hp)]["min"]
        max_x = value_info["hp " + str(hp)]["max"]

        Exact_Table['threshold hp' + str(hp)] =   -np.int(scale*((num_features + 1) * min_x))
        Exact_Table["bias hp" + str(hp)] =  np.int(scale*(x - min_x))



    for i,fn in enumerate(feature_names):
        Exact_Table[fn] = {}
        for feature in range(feature_max[i]+1):
            Exact_Table[fn][feature] = {}
            for hp in range(num_hps):
                x = SVM_separate_table[fn][feature]["hp "+str(hp)]
                min_x = value_info["hp " + str(hp)]["min"]
                max_x = value_info["hp " + str(hp)]["max"]

                Exact_Table[fn][feature]["hp "+str(hp)] = np.int(scale*(x - min_x))

    # =================== convert model timer ===================
    Planter_config['timer log']['convert model']['end'] = time.time()
    # =================== convert model timer ===================

    json.dump(Exact_Table,open('Tables/Exact_Table.json','w'),indent=4)
    print('Exact_Table is generated')

    feature_tbl_len = []
    for f in range(num_features):
        feature_tbl_len += [len(Exact_Table['f'+str(f)].keys())]

    thresh_and_bias = ''
    for h in range(num_hps):
        if h == 0:
            thresh_and_bias += str(Exact_Table['threshold hp' + str(h)])
        else:
            thresh_and_bias += (', '+ str(Exact_Table['threshold hp' + str(h)]))
    for h in range(num_hps):
        thresh_and_bias += (', ' + str(Exact_Table['bias hp' + str(h)]))

    hp_info = {}
    count = 0
    initial = 0
    while True:
        for c in range(num_classes):
            if c > initial:
                hp_info[count] = [initial, c]
                count += 1
        initial += 1
        if initial >= num_classes - 1:
            break


    Planter_config['p4 config'] = {}

    Planter_config['p4 config'] = {}
    Planter_config['p4 config']["model"] = "SVM"
    Planter_config['p4 config']["number of features"] = num_features
    Planter_config['p4 config']["number of classes"] = num_classes
    Planter_config['p4 config']["action data bits"] = num_bits
    Planter_config['p4 config']["number of hps"] = num_hps
    Planter_config['p4 config']["feature tbl len"] = feature_tbl_len
    Planter_config['p4 config']['table name'] = 'Exact_Table.json'
    Planter_config['p4 config']['thresh and bias'] = thresh_and_bias
    Planter_config['p4 config']['hp_info'] = hp_info

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

    hp_info = {}
    count = 0
    initial = 0
    while True:
        for c in range(num_classes):
            if c> initial:
                hp_info[count] = [initial,c]
                count+=1
        initial+=1
        if initial >= num_classes-1:
            break


    for i in range(np.shape(test_X.values)[0]):
        class_vote = np.zeros(num_classes).tolist()
        input_feature_value = test_X.values[i]
        for hp in range(np.int(num_classes * (num_classes - 1) / 2)):
            hp_value = 0
            for f in range(num_features):
                hp_value += Exact_Table["f"+str(f)][str(input_feature_value[f])]["hp "+str(hp)]
            hp_value += Exact_Table["bias hp"+str(hp)]
            if num_classes ==2:
                if hp_value>Exact_Table["threshold hp"+str(hp)]:
                    class_vote[hp_info[hp][1]] += 1
                else:
                    class_vote[hp_info[hp][0]] += 1
            else:
                if hp_value>Exact_Table["threshold hp"+str(hp)]:
                    class_vote[hp_info[hp][0]] += 1
                else:
                    class_vote[hp_info[hp][1]] += 1

        switch_prediction = class_vote.index(np.max(class_vote))
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



    print('\nThe accuracy of the match action format of SVM is', correct / np.shape(test_X.values)[0])
    result = classification_report(switch_test_y, test_y, digits=4)
    print('\n', result)



    
def resource_prediction():

    config_file = './src/configs/Planter_config.json'
    Planter_config = json.load(open(config_file, 'r'))

    print('Exact match entries: ',np.sum(Planter_config['p4 config']["feature tbl len"]) )


