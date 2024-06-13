# *************************************************************************
#
# Copyright 2021 Tushar Swamy (Stanford University),
#                Annus Zulfiqar (Purdue University),
#                Muhammad Shahbaz (Stanford/Purdue University)
# Modified by Planter's working group
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# *************************************************************************

from sklearn.model_selection import train_test_split
from itertools import accumulate
import numpy as np
import csv

import numpy as np
import pandas as pd
import os
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import socket
import struct
import gc
import copy

# Loader for (modified) FlowLens Botnet Detection Dataset - https://gitlab.com/dataplane-ai/homunculus/datasets/-/tree/main/flowlens-flowmarkers-traces

PL_HIST_LENGTH  = 46
IPT_HIST_LENGTH = 56
labels_to_class = {
    "benign":       [1, 0],
    "malicious":    [0, 1]
}


def load_data(num_features, data_dir):
    file_dir = data_dir+'/flowlens-flowmarkers-traces/'
    train_file = 'Dataset_64_512.csv'
    test_file = 'PerPktHist_Subset10k_24k_64_512.csv'
    label_index = 'class'
    
    files = []
    full_data = []
    full_labels = []
    shift =4
    print('read data from file: '+train_file+' ...')
    train_dataset = pd.read_csv(file_dir+train_file)
    train_data = pd.DataFrame(train_dataset)
    train_label = train_data[label_index]
    train_data = train_data[train_data.columns[shift:]] 
    print('DEBUG train_data.info(): ', train_data.info())
    feature_name = train_data.columns
    test_dataset = pd.read_csv(file_dir+test_file)
    test_data = pd.DataFrame(test_dataset)
    test_data.columns = feature_name[-31:]
    print('DEBUG test_data.info(): ', test_data.info())
    
    for key in range(len(train_data[label_index].values)):
        if train_data[label_index].values[key]=='malicious':
            train_data[label_index].values[key] = 1
        elif train_data[label_index].values[key]=='benign':
            train_data[label_index].values[key] = 0
        else:
            train_data[label_index].values[key] = -1
    for key in range(len(test_data[label_index].values)):
        if test_data[label_index].values[key]=='malicious':
            test_data[label_index].values[key] = 1
        elif test_data[label_index].values[key]=='benign':
            test_data[label_index].values[key] = 0
        else:
            test_data[label_index].values[key] = -1
     
    print('DEBUG train_data.columns:', train_data.columns) 
    

    used_features = train_data.columns[:num_features]
    


    X_train = copy.deepcopy(train_data[used_features])
    y_train = copy.deepcopy(train_data[label_index].astype("int"))
    X_test = copy.deepcopy(test_data[used_features])
    y_test = copy.deepcopy(test_data[label_index].astype("int"))

    print('dataset is loaded')
    return X_train, np.array(y_train), X_test, np.array(y_test), used_features
