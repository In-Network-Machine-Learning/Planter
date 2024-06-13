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

import math

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
from src.functions.numeric_conversion import *






def relative_code_lookup(idx, num_features, feature_num, look_up, label):
    if feature_num ==num_features:
        code = ''
        for f in range(num_features):
            code += str(int(idx[f]))
        look_up[code] = label
        label += 1
        return look_up, label
    else:
        for r in [0,1]:
            idx[feature_num] = r
            feature_num+=1
            look_up,label = relative_code_lookup(idx,num_features,feature_num, look_up, label)
            feature_num-=1
    return look_up, label


def get_codes(lookup, x, num_features, num_depth, depth_num, border_max, border_min):
    code = ''
    need_split = True
    while need_split:
        if num_depth == depth_num:
            break
        center = np.zeros(num_features)
        for f in range(num_features):
            center[f] = (copy.deepcopy(border_max[f]) + copy.deepcopy(border_min[f])) / 2
        con = ''
        for f in range(num_features):
            if x[f]>= center[f]:
                con += '1'
                border_min[f] = copy.deepcopy(center[f])
            else:
                con += '0'
                border_max[f] = copy.deepcopy(center[f])
        code += ten_to_bin(lookup[con], num_features)
        depth_num += 1
    return code



def get_boarder_list(border_dict, num_features, feature_num, num_depth, border_max, border_min, value_list, idx):
    if num_features == feature_num:
        border_dict[idx] = copy.deepcopy(value_list)
        idx+=1
        return border_dict, idx
    else:
        for i in [0,1]:
            if i==0:
                value_list[feature_num] = border_min[feature_num]
            else:
                value_list[feature_num] = border_max[feature_num]
            feature_num += 1
            border_dict, idx = get_boarder_list(border_dict, num_features, feature_num, num_depth, border_max, border_min, value_list, idx)
            feature_num -= 1
    return border_dict, idx


def check_if_not_finish(center,width, division, num_features,num_depth, num_classes, clf_centers):
    not_finish = False
    border_max_test = np.zeros(num_features)
    border_min_test = np.zeros(num_features)
    for f in range(num_features):

        border_min_test[f] = center[f] - width[f]
        border_max_test[f] = center[f] + width[f]

    border_list = {}
    border_list, _ = get_boarder_list(border_list, num_features, 0, num_depth, border_max_test, border_min_test, np.zeros(num_features), 0)
    # print(border_list)
    for idx in border_list:
        dis = np.zeros(num_classes).tolist()
        for c in range(num_classes):
            for f in range(num_features):
                dis[c] += (clf_centers['c'+str(c)]['f'+str(f)] - border_list[idx][f])**2
        # print(dis, dis.index(np.min(dis)))
        if idx == 0:
            cla = dis.index(np.min(dis))
        else:
            if cla != dis.index(np.min(dis)):
                not_finish = True
                cla = 404
                break
    # print(clf_centers)
    return not_finish, cla




def clustream(table, idx, code, lookup, num_features, num_classes, num_depth, depth_num, center, width, border_max, border_min, clf_centers, division, is_return):
    cla = 0
    # if not is_return:
    is_return == False
    for f in range(num_features):
        center[f] = (copy.deepcopy(border_max[f]) + copy.deepcopy(border_min[f])) / 2
        width[f] = (copy.deepcopy(border_max[f]) - copy.deepcopy(border_min[f])) / 2


    not_finish = True
    if depth_num ==0:
        not_finish = True
    elif depth_num < num_depth:
        not_finish, cla = check_if_not_finish(copy.deepcopy(center), copy.deepcopy(width), division, num_features,
                                              num_depth, num_classes, clf_centers)
    else:
        not_finish = False
        # cla = 404
        _, cla = check_if_not_finish(copy.deepcopy(center), copy.deepcopy(width), division, num_features,
                                              num_depth, num_classes, clf_centers)


    if not_finish:

        for division in lookup:
            new_boarder_max = np.zeros(num_features)
            new_boarder_mim = np.zeros(num_features)
            for f in range(num_features):
                if division[f] == '0':
                    new_boarder_mim[f] = copy.deepcopy(center[f]) - copy.deepcopy(width[f])
                    new_boarder_max[f] = copy.deepcopy(center[f])
                else:
                    new_boarder_max[f] = copy.deepcopy(center[f]) + copy.deepcopy(width[f])
                    new_boarder_mim[f] = copy.deepcopy(center[f])
            # print('3. max', new_boarder_max, 'min', new_boarder_mim)
            depth_num += 1
            code += ten_to_bin(lookup[division], num_features)
            table, idx, is_return = clustream(table, idx, copy.deepcopy(code), lookup, num_features, num_classes,
                                   num_depth, copy.deepcopy(depth_num), copy.deepcopy(center), copy.deepcopy(width),
                                   copy.deepcopy(new_boarder_max), copy.deepcopy(new_boarder_mim), clf_centers, division, is_return)
            depth_num -=1
            code = code[:-num_features]
    else:
        mask = (depth_num)*(num_features*'1')+(num_depth-depth_num)*(num_features*'0')
        value = code+(num_depth-depth_num)*(num_features*'0')

        table[idx] = [int(mask,2), int(value,2), cla]
        idx += 1
        is_return == True
        return table, idx, is_return
    is_return == True
    return table, idx, is_return



def run_model(train_X, train_y, test_X, test_y, used_features):
    
    config_file = 'src/configs/Planter_config.json'

    Planter_config = json.load(open(config_file, 'r'))
    Planter_config = json.load(open(config_file, 'r'))
    Planter_config['model config']['depth of quadtree'] = int(input('- Number of depth of the quadtree? (default = 2) ') or '2')
    Planter_config['model config']['random state'] = int(input('- What is the model random state? (default = 4) ') or '4')
    Planter_config['model config']['number of classes'] = int(np.max(train_y) + 1)

    random_state = Planter_config['model config']['random state']
    num_features = Planter_config['data config']['number of features']
    num_classes = Planter_config['model config']['number of classes']
    num_depth = Planter_config['model config']['depth of quadtree']


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

    print('Generating Ternary Tables for Clustream K-means ... ', end='')
    lookup = {}
    lookup, _ = relative_code_lookup(np.zeros(num_features), num_features, 0, lookup, 0)
    Ternary_Table = {}
    Ternary_Table, _, _ = clustream(Ternary_Table, 0, '', lookup, num_features, num_classes, num_depth, 0, np.zeros(num_features), np.zeros(num_features), feature_max, feature_min, centers, '', False)
    print('Done')

    # =================== convert model timer ===================
    Planter_config['timer log']['convert model']['end'] = time.time()
    # =================== convert model timer ===================

    json.dump(Ternary_Table, open('Tables/Ternary_Table.json', 'w'), indent=4)


    # ========================== prepare the test data =====================================
    for i in range(np.shape(test_X.values)[0]):
        distance = np.zeros(num_classes).tolist()
        input_feature_value = test_X.values[i]
        code = get_codes(lookup, input_feature_value, num_features, num_depth, 0, copy.deepcopy(feature_max),
                         copy.deepcopy(feature_min))
        test_X.values[i][0] = int(code, 2)

    # =======================================================================================

    Planter_config['p4 config'] = {}
    Planter_config['p4 config']["model"] = "KM"
    Planter_config['p4 config']["number of features"] = num_features
    Planter_config['p4 config']["number of classes"] =  num_classes
    Planter_config['p4 config']["table length"] = len(Ternary_Table.keys())
    Planter_config['p4 config']['table name'] = 'Ternary_Table.json'
    Planter_config['model config']['lookup'] = lookup
    Planter_config['model config']['feature max'] = feature_max
    Planter_config['model config']['feature min'] = feature_min
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
    random_state = Planter_config['model config']['random state']
    num_depth = Planter_config['model config']['depth of quadtree']
    lookup = Planter_config['model config']['lookup']
    feature_max = Planter_config['model config']['feature max']
    feature_min = Planter_config['model config']['feature min']
    Ternary_Table = json.load(open('Tables/Ternary_Table.json', 'r'))


    print("Test the generated table")
    same = 0
    correct = 0
    error = 0
    switch_test_y = []

    for i in range(np.shape(test_X.values)[0]):
        code = test_X.values[i][0]

        match_or_not = False


        keys = list(Ternary_Table.keys())

        for count in keys:

            if code & Ternary_Table[count][0] == Ternary_Table[count][0] & Ternary_Table[count][1]:
                switch_prediction = Ternary_Table[count][2]
                match_or_not = True
                break

        if not match_or_not:
            print('feature table not matched')

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

    print('\nThe accuracy of the match action format of Kmeans is', correct / np.shape(test_X.values)[0])
    result = classification_report(switch_test_y, test_y, digits=4)
    print('\n', result)


def resource_prediction():

    config_file = './src/configs/Planter_config.json'
    Planter_config = json.load(open(config_file, 'r'))

    print('Ternary match entries: ',np.sum(Planter_config['p4 config']["table length"]) )


