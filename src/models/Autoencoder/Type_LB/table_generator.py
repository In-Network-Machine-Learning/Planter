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

import torch.nn as nn
from torch.autograd import Variable as V
import torch
from torch.utils.data import DataLoader, Dataset, TensorDataset
from sklearn.datasets import load_iris
from sklearn.preprocessing import MinMaxScaler
import numpy
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
import numpy as np
import json
import copy
from scipy.stats import pearsonr
from src.functions.json_encoder import *
import math
import time
import time
# print(isinstance(my_dataset,Dataset))


###### Define an autoencoder model
class autoencoder(nn.Module):
    def __init__(self, num_features, num_components):
        super(autoencoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(num_features, num_components),
            # nn.Tanh(),
            # nn.Linear(3, 2),
        )
        self.decoder = nn.Sequential(
            # nn.Linear(2, 3),
            # nn.Tanh(),
            nn.Linear(num_components, num_features),
            # nn.Sigmoid()
        )

    def forward(self, x):
        encoder = self.encoder(x)
        decoder = self.decoder(encoder)
        return encoder, decoder


def run_model(train_X, train_y, test_X, test_y, used_features):
    config_file = 'src/configs/Planter_config.json'

    Planter_config = json.load(open(config_file, 'r'))
    Planter_config['model config']['number of classes'] = np.int(np.max(train_y) + 1)
    Planter_config['model config']['num components'] = np.int(input('- Number of components? (default = 2) ') or '2')
    Planter_config['model config']['learning rate'] = np.float(input('- Model learning rate? (default = 0.01) ') or '0.01')
    Planter_config['model config']['batch size'] = np.int(input('- Model batch size? (default = 100) ') or '100')
    Planter_config['model config']['num epoch'] = np.int(input('- Number of training epoch? (default = 50) ') or '50')
    Planter_config['model config']['number of bits'] = np.int(
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
        train_X.rename(columns={f: "f" + str(i)}, inplace=True)
        test_X.rename(columns={f: "f" + str(i)}, inplace=True)
        feature_names += ["f" + str(i)]

    feature_max = []
    for i in feature_names:
        t_t = [test_X[[i]].max()[0], train_X[[i]].max()[0]]
        feature_max += [max(t_t)+1]
     ###### Normalize the input as the autoencoder only uses the input
    # MMScaler = MinMaxScaler()
    # x = MMScaler.fit_transform(x)
    # iforestX = x

    ###### Convert input data to the dataset type accepted by the neural network, set batch size to 10
    tensor_x = torch.from_numpy(train_X.to_numpy().astype(numpy.float32))
    tensor_y = torch.from_numpy(train_y.astype(numpy.float32))
    # X_new = copy.deepcopy(test_X)
    sklearn_X_new = copy.deepcopy(test_X)
    test_X = torch.from_numpy(test_X.to_numpy().astype(numpy.float32))
    test_y = torch.from_numpy(test_y.astype(numpy.float32))
    my_dataset = TensorDataset(tensor_x, tensor_y)
    my_test_dataset = TensorDataset(test_X, test_y)
    my_dataset_loader = DataLoader(my_dataset, batch_size=batch_size, shuffle=False)


    model = autoencoder(num_features,num_components)

    ####### Define the loss function

    criterion = nn.MSELoss()

    ####### Define the optimization function
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)  # If using SGD, convergence does not decrease

    # =================== train model timer ===================
    Planter_config['timer log']['train model'] = {}
    Planter_config['timer log']['train model']['start'] = time.time()
    # =================== train model timer ===================

    ####### Set epoch to 300

    for epoch in range(num_epoch):
        total_loss = 0
        for i, (x, y) in enumerate(my_dataset_loader):
            _, pred = model(V(x))
            loss = criterion(pred, x)


            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss
        if epoch % 10 == 0:
            print('\rTraining loss {}'.format(total_loss.data.numpy()),end=" ")

    # =================== train model timer ===================
    Planter_config['timer log']['train model']['end'] = time.time()
    # =================== train model timer ===================

    # =================== convert model timer ===================
    Planter_config['timer log']['convert model'] = {}
    Planter_config['timer log']['convert model']['start'] = time.time()
    # =================== convert model timer ===================

    model_info = {}
    for i, param in enumerate (model.parameters()):
        # print(param)
        model_info[i] =  param.detach().numpy()
    model_info['weights'] = model_info[0].T
    model_info['bias'] = model_info[1]
    ###### Perform dimensionality reduction and visualization based on the trained model

    print('\nGenerate the table...',end="")

    value_info = {}
    value_info["max"] = np.max(model_info['bias'])
    value_info["min"] = np.min(model_info['bias'])
    for ax in range(num_components):
        value_info["ax " + str(ax)] = {}
        value_info["ax " + str(ax)]["max"] = model_info['bias'][ax]
        value_info["ax " + str(ax)]["min"] = model_info['bias'][ax]

    g_table = {}
    for f in range(num_features):
        g_table['feature ' + str(f)] = {}
        for input_value in range(feature_max[f]):
            g_table['feature ' + str(f)][input_value] = {}
            for ax in range(num_components):
                middle_value = copy.deepcopy(input_value * model_info['weights'][f, ax])
                g_table['feature ' + str(f)][input_value]['ax' + str(ax)] = middle_value
                if middle_value > value_info["ax " + str(ax)]["max"]:
                    value_info["ax " + str(ax)]["max"] = middle_value
                if middle_value < value_info["ax " + str(ax)]["min"]:
                    value_info["ax " + str(ax)]["min"] = middle_value
                if middle_value > value_info["max"]:
                    value_info["max"] = middle_value
                if middle_value < value_info["min"]:
                    value_info["min"] = middle_value

    scale = (2 ** num_bits) / ((value_info["max"] - value_info["min"]) * (num_features+1))

    Exact_Table = {}
    for f in range(num_features):
        Exact_Table['feature ' + str(f)] = {}
        for input_value in range(feature_max[f]):
            Exact_Table['feature ' + str(f)][input_value] = {}
            for ax in range(num_components):
                middle_value = copy.deepcopy(g_table['feature ' + str(f)][input_value]['ax' + str(ax)])
                middle_value = np.int(np.floor((middle_value - value_info["min"])*scale))
                Exact_Table['feature ' + str(f)][input_value]['ax' + str(ax)] = middle_value

    Exact_Table['bias'] = {}
    for ax in range(num_components):
        Exact_Table['bias']['ax' + str(ax)] = np.int(np.floor((model_info['bias'][ax]- value_info["min"])*scale))


    # =================== convert model timer ===================
    Planter_config['timer log']['convert model']['end'] = time.time()
    # =================== convert model timer ===================

    print('Done')
    json.dump(Exact_Table, open('Tables/Exact_Table.json', 'w'), indent=4)
    print('Exact_Table is generated')

    feature_tbl_len = []
    for f in range(num_features):
        feature_tbl_len += [len(Exact_Table['feature ' + str(f)].keys())]

    Planter_config['p4 config'] = {}

    Planter_config['p4 config'] = {}
    Planter_config['p4 config']["model"] = "Autoencoder"
    Planter_config['p4 config']["number of features"] = num_features
    Planter_config['p4 config']["number of classes"] = num_classes
    Planter_config['p4 config']["action data bits"] = num_bits
    Planter_config['p4 config']['table name'] = 'Exact_Table.json'
    Planter_config['p4 config']["feature tbl len"] = feature_tbl_len
    Planter_config['p4 config']["num components"] = num_components
    Planter_config['test config']  = {}
    Planter_config['test config']['type of test'] = 'dimension_reduction'


    json.dump(Planter_config,
              open(Planter_config['directory config']['work'] + '/src/configs/Planter_config.json', 'w'), indent=4,
              cls=NpEncoder)
    print(Planter_config['directory config']['work'] + '/src/configs/Planter_config.json is generated')

    x_ = []
    y_ = []
    for i, (x, y) in enumerate(my_test_dataset):
        _, pred = model(V(x))
        dimension = _.data.numpy()
        for ax in range(num_components):
            sklearn_X_new.values[i,ax] = dimension[ax] - (num_features + 1) * value_info["min"]
        # prepare for plot
        x_.append(dimension[0]-(num_features+1)*value_info["min"])
        y_.append(dimension[1]-(num_features+1)*value_info["min"])


    plot_result =  input('- Plot the training result ? (default = n) ') or 'n'

    if plot_result == 'y':
        print('plot')
        plt.scatter(numpy.array(x_), numpy.array(y_), c=test_y.detach().numpy())

        for i in range(len(numpy.array(x_))):
            plt.annotate(i, (x_[i], y_[i]))
        plt.show()
    return sklearn_X_new.values


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
            switch_test_x[i][ax] = copy.deepcopy(Exact_Table['bias']['ax'+str(ax)])
        for f in range(num_features):
            ax_middle = Exact_Table["feature "+str(f)][str(input_feature_value[f])]
            for ax in range(num_components):
                switch_test_x[i][ax] += ax_middle["ax"+str(ax)]
        # print(sklearn_test_x[i], switch_test_x[i])
        # test_X.values[i]
        # switch_test_x.values[i]
    for ax in range(num_components):
        corr, _ = pearsonr(sklearn_test_x[:, ax],switch_test_x[:, ax])
        print('Pearsons correlation of M/A PCA and output of Pytorch for axis '+str(ax)+' is: %.4f' % corr)

def resource_prediction():

    config_file = './src/configs/Planter_config.json'
    Planter_config = json.load(open(config_file, 'r'))

    print('Exact match entries: ',np.sum(Planter_config['p4 config']["feature tbl len"]) )


