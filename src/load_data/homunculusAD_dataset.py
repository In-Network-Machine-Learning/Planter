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


from __future__ import division, print_function, absolute_import
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

# Loader for (modified) NSL KDD Dataset - https://gitlab.com/dataplane-ai/homunculus/datasets/-/tree/main/kdd-synthetic-traces
def load_data(num_features, data_dir):

# def load_from_file(dataset):
    file_dir = data_dir+'/kdd-synthetic-traces/'
    train_file = 'train_ad.csv'
    test_file = 'test_ad.csv'
    features_col = ['f0','f1','f2','f3','f4','f5','f6','f7','label']
    label_index = 'label'
    
    print('read data from file: '+train_file+' ...')
    train_dataset = pd.read_csv(file_dir+train_file)
    train_data = pd.DataFrame(train_dataset)
    train_data.columns = features_col
    print('DEBUG train_data.info(): ', train_data.info())
    
    test_dataset = pd.read_csv(file_dir+test_file)
    test_data = pd.DataFrame(test_dataset)
    test_data.columns = features_col
    print('DEBUG test_data.info(): ', test_data.info())
    

    used_features = ['f0','f1','f2','f3','f4','f5','f6','f7'][:num_features]
 

    X_train = copy.deepcopy(train_data[used_features])
    y_train = copy.deepcopy(train_data[label_index])
    X_test = copy.deepcopy(test_data[used_features])
    y_test = copy.deepcopy(test_data[label_index])
            
    


    print('dataset is loaded')
    return X_train, np.array(y_train), X_test, np.array(y_test), used_features
