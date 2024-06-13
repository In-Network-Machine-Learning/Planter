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
from pandas import Series,DataFrame
from pandas import plotting
import os

# %matplotlib inline
import matplotlib.pyplot as plt
plt.style.use('seaborn')

import seaborn as sns
sns.set_style("whitegrid")


import copy
import json
from src.functions.Range_to_TCAM_Top_Down import *
from src.functions.json_encoder import *
from src.models.NN.Type_2.BinaryNet.models.xnor_layers import *
from src.models.NN.Type_2.BinaryNet.models.xnor_mlp import *
from src.models.NN.Type_2.BinaryNet.models import *
from src.models.NN.Type_2.BinaryNet.classifiers.xnor_classifier import *
from sklearn.metrics import *
import torch.nn as nn
from torch.autograd import Variable as V
from torch.utils.data import DataLoader, Dataset, TensorDataset
import torch
from pathlib import Path
from datetime import datetime
import os

import numpy as np
import pandas as pd
from scapy.compat import raw
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether
from scapy.packet import Padding
from scipy import sparse

from joblib import Parallel, delayed

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from keras.constraints import maxnorm

from sklearn.model_selection import train_test_split

from imblearn.over_sampling import RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler

from keras.utils.np_utils import to_categorical
import matplotlib.pyplot as plt

import seaborn as sn


def inttobit(n):
    return [1 if digit == '1' else -1 for digit in '{0:056b}'.format(n)]


def bintoint(binary):
    number = 0
    for b in binary:
        number = (2 * number) + int(b)
    return number


def conv_header(proto, sport, dport, size):
    proto_bin = [int(x) for x in '{0:08b}'.format(proto)]
    sport_bin = [int(x) for x in '{0:016b}'.format(sport)]
    dport_bin = [int(x) for x in '{0:016b}'.format(dport)]
    size_bin = [int(x) for x in '{0:016b}'.format(size)]
    metric = proto_bin + sport_bin + dport_bin + size_bin
    metric_int = bintoint(metric)
    return metric, metric_int


# convert weights to binary weights and to integer
def convert_weight_to_file(weight_data, filename):
    weight = []
    weights = []
    for i in weight_data:
        for j in i:
            if j < 0:
                weight.append(0)
            else:
                weight.append(1)
        weights.append(bintoint(weight))
        weight.clear()
    txtfile = open(filename, "w")
    for i in weights:
        txtfile.write(str(i) + "\n")
    txtfile.close()





def run_model(train_X, train_y, test_X, test_y, used_features):
    config_file = 'src/configs/Planter_config.json'

    Planter_config = json.load(open(config_file, 'r'))
    Planter_config['model config']['number of classes'] = int(np.max(train_y) + 1)
    Planter_config['model config']['num components'] = int(input('- Number of components? (default = 2) ') or '2')
    Planter_config['model config']['learning rate'] = np.float(
        input('- Model learning rate? (default = 0.01) ') or '0.01')
    Planter_config['model config']['batch size'] = int(input('- Model batch size? (default = 10) ') or '10')
    Planter_config['model config']['num epoch'] = int(input('- Number of training epoch? (default = 5) ') or '5')
    Planter_config['model config']['number of bits'] = int(
        input('- Number of bits for each action data? (default = 16) ') or '16')

    num_bits = Planter_config['model config']['number of bits']

    num_components = Planter_config['model config']['num components']
    num_features = Planter_config['data config']['number of features']
    num_classes = Planter_config['model config']['number of classes']
    learning_rate = Planter_config['model config']['learning rate']
    batch_size = Planter_config['model config']['batch size']
    num_epoch = Planter_config['model config']['num epoch']

    feature_names = []
    for i, f in enumerate(used_features):
        train_X.rename(columns={f: "f"+str(i)}, inplace=True)
        test_X.rename(columns={f: "f" + str(i)}, inplace=True)
        feature_names+=["f"+str(i)]

    feature_max = []
    for i in feature_names:
        t_t = [test_X[[i]].max()[0], train_X[[i]].max()[0]]
        feature_max += [np.max(t_t)+1]

    width = []
    for f in range(num_features):
        width += [np.ceil(math.log(feature_max[f],2))]
    width_row = int(np.sum(width))


    total_count = np.shape(train_X.values)[0] + np.shape(test_X.values)[0]
    count = 0

    train_X_new = []
    test_X_new = []
    for i in range(np.shape(train_X.values)[0]):
        flag = 0
        row = (np.zeros(int(width_row)))
        for f in range(num_features):
            code = ten_to_bin(train_X.values[i][f],width[f])
            for d in range(int(width[f])):
                row[flag] = int(code[d])
                flag += 1
        train_X_new += [row]
        # ======================
        count += 1
        percent = int(np.ceil(50 * count / total_count))
        print('\rProcessing the raw Data [' + percent * '#' + (50 - percent) * '-' + '] ' + str( int(np.round(100 * count / total_count))) + "%", end="")
        # ======================
    train_X_new = np.array(train_X_new)

    for i in range(np.shape(test_X.values)[0]):
        flag = 0
        row = (np.zeros(int(width_row)))
        for f in range(num_features):
            code = ten_to_bin(test_X.values[i][f],width[f])
            for d in range(int(width[f])):
                row[flag] = int(code[d])
                flag += 1
        test_X_new += [row]
        # ======================
        count += 1
        percent = int(np.ceil(50 * count / total_count))
        print('\rProcessing the raw data [' + percent * '#' + (50 - percent) * '-' + '] ' + str(int(np.round(100 * count / total_count))) + "%", end="")
        # ======================
    test_X_new = np.array(test_X_new)
    print('\nData set is ready')


    ###### Convert input data to the dataset type accepted by the neural network, set batch size to 10
    tensor_x = torch.from_numpy(train_X_new.astype(np.float32))
    tensor_y = torch.LongTensor(train_y.astype(np.float32))
    test_X = torch.from_numpy(test_X_new.astype(np.float32))
    test_y = torch.LongTensor(test_y.astype(np.float32))
    my_train_dataset = TensorDataset(tensor_x, tensor_y)
    my_test_dataset = TensorDataset(test_X, test_y)
    train_loader = DataLoader(my_train_dataset, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(my_test_dataset, batch_size=batch_size, shuffle=False)

    # divide train and test data
    x_train, x_test, y_train, y_test = train_test_split(np.array(train_X_new, dtype=np.float32), train_y, test_size=0.2, random_state=1)
    x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=0.25, random_state=1)  # 0.25 x 0.8 = 0.2
    model = None

    model = keras.models.Sequential()
    model.add(layers.Dropout(0.2))
    model.add(layers.Dense(56, input_dim=56, activation="tanh", name="dense_1", kernel_constraint=maxnorm(2)))
    model.add(layers.Dropout(0.5))
    model.add(layers.Dense(56, activation="tanh", name="dense_2", kernel_constraint=maxnorm(2)))
    model.add(layers.Dropout(0.5))
    model.add(layers.Dense(56, activation="tanh", name="dense_3", kernel_constraint=maxnorm(2)))
    model.add(layers.Dropout(0.5))
    model.add(layers.Dense(56, activation="tanh", name="dense_4", kernel_constraint=maxnorm(2)))
    model.add(layers.Dropout(0.5))
    model.add(layers.Dense(6, activation="softmax", name="predictions"))

    # define optimizer, loss function, and metric
    model.compile(
        optimizer=keras.optimizers.Adam(),  # Optimizer
        # Loss function to minimize
        loss=keras.losses.SparseCategoricalCrossentropy(),
        # List of metrics to monitor
        metrics=[keras.metrics.SparseCategoricalAccuracy()]
        # metrics=[keras.metrics.Accuracy()],
    )

    # fit training model
    history = model.fit(
        x_train,
        y_train,
        batch_size=128,
        epochs=20,
        verbose=2,
        # We pass some validation for
        # monitoring validation loss and metrics
        # at the end of each epoch
        validation_data=(x_val, y_val),
    )

    # transpose weight dimension
    transposed_l1 = tf.transpose(model.trainable_variables[0])
    transposed_l2 = tf.transpose(model.trainable_variables[2])
    transposed_l3 = tf.transpose(model.trainable_variables[4])
    transposed_l4 = tf.transpose(model.trainable_variables[6])
    # transposed_l5 = tf.transpose(model.trainable_variables[8])

    convert_weight_to_file(transposed_l1, "./src/temp/w-l1.txt")
    convert_weight_to_file(transposed_l2, "./src/temp/w-l2.txt")
    convert_weight_to_file(transposed_l3, "./src/temp/w-l3.txt")
    convert_weight_to_file(transposed_l4, "./src/temp/w-l4.txt")



    exit()
    return test_y.tolist()



def test_tables(sklearn_test_y, test_X, test_y):



    config_file = 'src/configs/Planter_config.json'
    Planter_config = json.load(open(config_file, 'r'))
    num_features = Planter_config['data config']['number of features']
    num_classes = Planter_config['model config']['number of classes']
    num_trees = Planter_config['model config']['number of classes']* int(int(Planter_config['model config']['number of trees'])/Planter_config['model config']['number of classes'])
    num_depth = Planter_config['model config']['number of depth']
    max_leaf_nodes = Planter_config['model config']['max number of leaf nodes']
    Ternary_Table = json.load(open('Tables/Ternary_Table.json', 'r'))
    Exact_Table = json.load(open('Tables/Exact_Table.json', 'r'))


    print('Test the exact feature table, extact code and decision table (feel free if the acc to sklearn is slightly lower than 1)')
    same = 0
    correct = 0
    error = 0
    switch_test_y = []
    for i in range(np.shape(test_X.values)[0]):
        vote_list = np.zeros(num_trees).astype(dtype=int).tolist()
        for tree in range(num_trees):
            code_list = np.zeros(num_features)
            ternary_code_list = np.zeros(num_features)
            input_feature_value = test_X.values[i]

            for f in range(num_features):
                match_or_not = False

                # matcg ternary
                TCAM_table = Ternary_Table['feature ' + str(f)]
                keys = list(TCAM_table.keys())

                for count in keys:
                    
                    if input_feature_value[f] & TCAM_table[count][0] == TCAM_table[count][0] & TCAM_table[count][1]:
                        ternary_code_list[f] = TCAM_table[count][2][tree]
                        match_or_not = True
                        break

                if not match_or_not:
                    print('feature table not matched')
                # matcg exact
                code_list[f] = Exact_Table['feature ' + str(f)][str(input_feature_value[f])][tree]
                if not match_or_not:
                    print('feature table not matched')
            if str(code_list)!=str(ternary_code_list):
                print('error in exact to ternary match', code_list,ternary_code_list)
            for key in Exact_Table["tree " + str(tree)]:

                match_or_not = False
                all_True = True
                for code_f in range(num_features):
                    if not Exact_Table["tree " + str(tree)][key]['f' + str(code_f) + ' code'] == code_list[code_f]:
                        all_True = False
                        break
                if all_True:
                    vote_list[tree] = int(Exact_Table["tree " + str(tree)][key]['leaf'])
                    match_or_not = True
                    break
            if not match_or_not:
                vote_list[tree] = Planter_config['p4 config']["default vote"]
                

        for key in Exact_Table['decision']:
            match_or_not = False
            all_True = True
            for tree_v in range(num_trees):
                if not Exact_Table["decision"][key]['t' + str(tree_v) + ' vote'] == vote_list[tree_v]:
                    all_True = False
                    break
            if all_True:
                switch_prediction = Exact_Table['decision'][key]['class']
                match_or_not = True
                break
        if not match_or_not:
            switch_prediction = Planter_config['p4 config']["default label"]


        switch_test_y += [switch_prediction]
        if switch_prediction == test_y[i]:
            correct += 1

        if switch_prediction == sklearn_test_y[i]:
            same += 1
        else:
            error += 1

        if i % 1 == 0 and i!=0:
            print(
                '\rswitch_prediction: {}, test_y: {}, with acc: {:.3}, with acc to sklearn: {:.3}, with error: {:.3}, M/A format macro f1: {:.3}, macro f1: {:.3}'.format(
                    switch_prediction, test_y[i], correct / (i + 1), same / (i + 1), error / (i + 1),
                    accuracy_score(switch_test_y[:i], test_y[:i] ),accuracy_score(sklearn_test_y[:i], test_y[:i] )), end="")


    print('\nThe accuracy of the match action format of XGBoost is', correct / np.shape(test_X.values)[0])
    result = classification_report(switch_test_y, test_y, digits=4)
    print('\n', result)