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
from sklearn.decomposition import PCA
from mpl_toolkits.mplot3d import Axes3D
import json
import matplotlib.pyplot as plt
import copy
from src.functions.json_encoder import *
from src.functions.normalization import *
from sklearn.metrics.pairwise import cosine_similarity
from scipy.stats import pearsonr
import math
import time

def run_model(train_X, train_y, test_X, test_y, used_features):
    config_file = 'src/configs/Planter_config.json'

    Planter_config = json.load(open(config_file, 'r'))
    Planter_config['model config']['number of classes'] = np.int(np.max(train_y) + 1)
    Planter_config['model config']['num components'] = np.int(input('- Number components? (default = 2) ') or '2')
    Planter_config['model config']['number of bits'] = np.int( input('- Number of bits for each action data? (default = 16) ') or '16')

    num_bits = Planter_config['model config']['number of bits']

    num_components = Planter_config['model config']['num components']
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
        feature_max += [max(t_t)+1]

    # =================== train model timer ===================
    Planter_config['timer log']['train model'] = {}
    Planter_config['timer log']['train model']['start'] = time.time()
    # =================== train model timer ===================

    pca = PCA(n_components=num_components)
    pca.fit(train_X)
    sklearn_X_new = pca.transform(test_X)

    # =================== train model timer ===================
    Planter_config['timer log']['train model']['end'] = time.time()
    # =================== train model timer ===================

    # =================== convert model timer ===================
    Planter_config['timer log']['convert model'] = {}
    Planter_config['timer log']['convert model']['start'] = time.time()
    # =================== convert model timer ===================


    model_info = {}
    model_info['means'] = pca.mean_
    model_info['components'] = pca.components_.T

    value_info = {}
    value_info["max"] = 0
    value_info["min"] = 0
    for ax in range(num_components):
        value_info["ax "+str(ax)] = {}
        value_info["ax " + str(ax)]["max"] = 0
        value_info["ax " + str(ax)]["min"] = 0

    PCA_Table = {}
    for f in range(num_features):
        PCA_Table['feature '+str(f)] = {}
        for input_value in range(feature_max[f]):
            PCA_Table['feature ' + str(f)][input_value] = {}
            value = input_value - model_info['means'][f]
            for ax in range(num_components):
                middle_value = copy.deepcopy(value*model_info['components'][f,ax])
                PCA_Table['feature ' + str(f)][input_value]['ax'+str(ax)] = middle_value
                if middle_value > value_info["ax " + str(ax)]["max"]:
                    value_info["ax " + str(ax)]["max"] = middle_value
                if middle_value < value_info["ax " + str(ax)]["min"]:
                    value_info["ax " + str(ax)]["min"] = middle_value
                if middle_value > value_info["max"]:
                    value_info["max"] = middle_value
                if middle_value < value_info["min"]:
                    value_info["min"] = middle_value

    scale = (2**num_bits)/((value_info["max"]-value_info["min"])*(num_features))


    Exact_Table = {}
    for f in range(num_features):
        Exact_Table['feature ' + str(f)] = {}
        for input_value in range(feature_max[f]):
            Exact_Table['feature ' + str(f)][input_value] = {}
            for ax in range(num_components):
                middle_value = copy.deepcopy(PCA_Table['feature ' + str(f)][input_value]['ax' + str(ax)])
                middle_value = np.int(np.floor((middle_value - value_info["min"])*scale))
                Exact_Table['feature ' + str(f)][input_value]['ax' + str(ax)] = middle_value

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
    Planter_config['p4 config']["model"] = "PCA"
    Planter_config['p4 config']["number of features"] = num_features
    Planter_config['p4 config']["number of classes"] = num_classes
    Planter_config['p4 config']["action data bits"] = num_bits
    Planter_config['p4 config']['table name'] = 'Exact_Table.json'
    Planter_config['p4 config']["feature tbl len"] = feature_tbl_len
    Planter_config['p4 config']["num components"] = num_components
    Planter_config['test config'] = {}
    Planter_config['test config']['type of test'] = 'dimension_reduction'

    json.dump(Planter_config,
              open(Planter_config['directory config']['work'] + '/src/configs/Planter_config.json', 'w'), indent=4,
              cls=NpEncoder)
    print(Planter_config['directory config']['work'] + '/src/configs/Planter_config.json is generated')

    X_new = copy.deepcopy(sklearn_X_new)

    for ax in range(num_components):
        X_new[:, ax] = sklearn_X_new[:, ax] - num_features*(value_info["min"])
    for ax in range(num_components):
        corr, _ = pearsonr(X_new[:, ax],sklearn_X_new[:, ax])
        print('Pearsons correlation for axis '+str(ax)+' is: %.3f' % corr)

    return X_new



def test_tables(sklearn_test_x, test_X, test_y):

    config_file = 'src/configs/Planter_config.json'
    Planter_config = json.load(open(config_file, 'r'))
    num_features = Planter_config['data config']['number of features']
    num_classes = Planter_config['model config']['number of classes']
    num_components = Planter_config['model config']['num components']
    Exact_Table = json.load(open('Tables/Exact_Table.json', 'r'))

    print("Test the generated table")
    same = 0
    correct = 0
    error = 0
    switch_test_x = copy.deepcopy(sklearn_test_x)



    for i in range(np.shape(test_X.values)[0]):
        input_feature_value = test_X.values[i]
        for ax in range(num_components):
            switch_test_x[i][ax] = 0
        for f in range(num_features):
            ax_middle = Exact_Table["feature "+str(f)][str(input_feature_value[f])]
            for ax in range(num_components):
                switch_test_x[i][ax] += ax_middle["ax"+str(ax)]

    for ax in range(num_components):

        corr, _ = pearsonr(sklearn_test_x[:, ax],switch_test_x[:, ax])
        print('Pearsons correlation of M/A PCA and output of Sklearn for axis '+str(ax)+' is: %.4f' % corr)


def resource_prediction():

    config_file = './src/configs/Planter_config.json'
    Planter_config = json.load(open(config_file, 'r'))

    print('Exact match entries: ',np.sum(Planter_config['p4 config']["feature tbl len"]) )


