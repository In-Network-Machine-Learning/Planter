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
from src.functions.logic_gates import *
import time

# %matplotlib inline
import matplotlib.pyplot as plt
plt.style.use('seaborn')

import seaborn as sns
sns.set_style("whitegrid")


import copy
import json
from src.functions.Range_to_TCAM_Top_Down import *
from src.functions.json_encoder import *
from src.models.NN.Type_1.BinaryNet.models.xnor_layers import *
from src.models.NN.Type_1.BinaryNet.models.xnor_mlp import *
from sklearn.metrics import *
import torch.nn as nn
from torch.autograd import Variable as V
from torch.utils.data import DataLoader, Dataset, TensorDataset
import torch
from src.models.NN.Type_1.BinaryNet.models import *
from src.models.NN.Type_1.BinaryNet.classifiers.xnor_classifier import *
from src.functions.numeric_conversion import *


def bintoint(binary):
    number = 0
    for b in binary:
        number = (2 * number) + int(b)
    return number


def convert_weight_to_register_data(weight_data):
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
    return weights


def run_model(train_X, train_y, test_X, test_y, used_features):
    config_file = 'src/configs/Planter_config.json'

    Planter_config = json.load(open(config_file, 'r'))
    Planter_config['model config']['number of classes'] = int(np.max(train_y) + 1)
    Planter_config['model config']['learning rate'] = np.float(input('- Model learning rate? (default = 0.01) ') or '0.01')
    Planter_config['model config']['batch size'] = int(input('- Model batch size? (default = 10) ') or '10')
    Planter_config['model config']['num epoch'] = int(input('- Number of training epoch? (default = 15) ') or '15')
    Planter_config['model config']['number of layers'] = int(input('- Number of layers? (default = 3) ') or '3')
    Planter_config['model config']['num hidden nodes'] = []
    for l in range(Planter_config['model config']['number of layers']-1):
        Planter_config['model config']['num hidden nodes'] += [int(input('- Number of hidden nodes for layer '+str(l+1)+'? (default = 56) ') or '56')]

    num_layers = Planter_config['model config']['number of layers']
    num_hidden_nodes = Planter_config['model config']['num hidden nodes']
    num_features = Planter_config['data config']['number of features']
    num_classes = Planter_config['model config']['number of classes']
    learning_rate = Planter_config['model config']['learning rate']
    batch_size = Planter_config['model config']['batch size']
    num_epoch = Planter_config['model config']['num epoch']

    feature_names = []
    for i, f in enumerate(used_features):
        train_X.rename(columns={f: "f" + str(i)}, inplace=True)
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

    cuda = torch.cuda.is_available()
    device = torch.device('cuda' if cuda else 'cpu')
    torch.manual_seed(0)
    if cuda:
        torch.backends.cudnn.deterministic = True
        torch.cuda.manual_seed(0)

    # =================== train model timer ===================
    Planter_config['timer log']['train model'] = {}
    Planter_config['timer log']['train model']['start'] = time.time()
    # =================== train model timer ===================

    model = eval('mlp')(width_row, num_hidden_nodes, num_layers, num_classes)
    model.to(device)

    classification = XnorClassifier(model, train_loader, test_loader, device)

    criterion = torch.nn.CrossEntropyLoss()
    criterion.to(device)

    if hasattr(model, 'init_w'):
        model.init_w()


    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=1e-5)

    scheduler = torch.optim.lr_scheduler.MultiStepLR(optimizer, [100, 200] , gamma=0.1)

    classification.train(criterion, optimizer, num_epoch, scheduler, Planter_config['directory config']['work']+'/src/temp/mlp')

    # =================== train model timer ===================
    Planter_config['timer log']['train model']['end'] = time.time()
    # =================== train model timer ===================

    # =================== convert model timer ===================
    Planter_config['timer log']['convert model'] = {}
    Planter_config['timer log']['convert model']['start'] = time.time()
    # =================== convert model timer ===================
 
    Exact_Table = {}

    Exact_Table['weights'] = []
    for l in range(num_layers):
        Exact_Table['weights'] += convert_weight_to_register_data(model.classifier._modules['layer'+str(l)].weight.detach().numpy())

    # =================== convert model timer ===================
    Planter_config['timer log']['convert model']['end'] = time.time()
    # =================== convert model timer ===================

    json.dump(Exact_Table, open('Tables/Exact_Table.json', 'w'), indent=4)
    print('Exact_Table is generated')

    Planter_config['p4 config'] = {}
    Planter_config['p4 config']["model"] = "NN"
    Planter_config['p4 config']["num hidden nodes"] = num_hidden_nodes
    Planter_config['p4 config']["number of features"] = num_features
    Planter_config['p4 config']["number of layers"] = num_layers
    Planter_config['p4 config']["number of classes"] = num_classes
    Planter_config['p4 config']["width of inputs"] = width
    Planter_config['p4 config']['table name'] = 'Exact_Table.json'
    Planter_config['test config'] = {}
    Planter_config['test config']['type of test'] = 'classification'

    json.dump(Planter_config,
              open(Planter_config['directory config']['work'] + '/src/configs/Planter_config.json', 'w'), indent=4,
              cls=NpEncoder)
    print(Planter_config['directory config']['work'] + '/src/configs/Planter_config.json is generated')

    return test_y.tolist()

def bits_on_count(x):
  return sum(c=='1' for c in bin(x))

def test_tables(sklearn_test_y, test_X, test_y):



    config_file = 'src/configs/Planter_config.json'
    Planter_config = json.load(open(config_file, 'r'))
    num_features = Planter_config['data config']['number of features']
    num_classes = Planter_config['model config']['number of classes']
    num_hidden_nodes = Planter_config['p4 config']["num hidden nodes"]
    num_layers = Planter_config['p4 config']["number of layers"]
    width = Planter_config['p4 config']["width of inputs"]
    Exact_Table = json.load(open('Tables/Exact_Table.json', 'r'))

    print('Test the exact feature table, extact code and decision table (feel free if the acc to sklearn is slightly lower than 1)')

    correct = 0
    switch_test_y = []
    for i in range(np.shape(test_X.values)[0]):
        input = ''
        for f in range(num_features):
            input += ten_to_bin(test_X.values[i][f],width[f])
        input = int(input, 2)
        # print(' - ', input)
        node_num = 0
        for l in range(num_layers):
            if l == 0:
                num_bits = int(np.sum(width))
            else:
                num_bits = int(num_hidden_nodes[l - 1])
            next_layer_input = ''
            if l+1 != num_layers:
                for n in range(num_hidden_nodes[l]):
                    # value = XNOR(input,Exact_Table['weights'][node_num])
                    value = XNOR_with_bits(input, Exact_Table['weights'][node_num], num_bits)
                    # print(ten_to_bin(value,120))
                    # if n+1 == num_hidden_nodes[l]:
                    # if n==0 and l ==0:
                    #     print('- ',input,' xnor ', Exact_Table['weights'][node_num], ' = ', value)
                    value = bits_on_count(value)
                    # print(value)
                    node_num += 1
                    if l==0:
                        threshold = np.floor(np.sum(width)/2)
                    else:
                        threshold = np.floor(num_hidden_nodes[l-1]/2)
                    if value> threshold:
                        next_layer_input += '1'
                    else:
                        next_layer_input += '0'


                input = int(next_layer_input,2)

            else:
                result = np.zeros(num_classes).tolist()
                for c in range(num_classes):
                    # value = XNOR(input, Exact_Table['weights'][node_num])
                    value = XNOR_with_bits(input, Exact_Table['weights'][node_num], num_bits)
                    value = bits_on_count(value)
                    result[c] = copy.deepcopy(value)
                    node_num += 1


        switch_prediction = result.index(np.max(result))
        switch_test_y += [switch_prediction]
        if switch_prediction == test_y[i]:
            correct += 1

        if i % 1 == 0 and i!=0:
            print(
                '\rswitch_prediction: {}, test_y: {}, with acc: {:.3},  M/A format macro f1: {:.3}'.format(
                    switch_prediction, test_y[i], correct / (i + 1), accuracy_score(switch_test_y[:i], test_y[:i] )), end="")


    print('\nThe accuracy of the match action format of NN is', correct / np.shape(test_X.values)[0])
    result = classification_report(switch_test_y, test_y, digits=4)
    print('\n', result)