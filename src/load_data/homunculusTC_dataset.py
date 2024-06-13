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

import sys
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

# Loader for (modified) TMC IoT Dataset - https://gitlab.com/dataplane-ai/homunculus/datasets/-/tree/main/tmc-iot-traces

# /datasets/tmc-iot-traces/tmc-med.csv 

train_pct = 0.8

# 0-Static Smart Home Devices
# 1-Sensors
# 2-Audio
# 3-Video
# 4-Other
# 5-Remove

#def load_data(dataset):
def load_data(num_features, data_dir):
    full_data = []
    full_labels = []
    limit = 1000000
    bins = [0, 0, 0, 0, 0]
    
    dataset = data_dir+'/tmc-iot-traces/balanced_data.csv'
    dataset = pd.read_csv(dataset)
    data = pd.DataFrame(dataset)
    used_features = ['f1','f2','f3','f4','f5','f6','f7'][:num_features]

    print('DEBUG data.info():', data.info())
    full_data = copy.deepcopy(data[used_features].astype("int"))
    full_labels = copy.deepcopy(data['label'].astype("int"))
            
    
    #return full_data, full_labels
    X_train, X_test, y_train, y_test = train_test_split(full_data, full_labels, test_size=0.2, stratify=full_labels, random_state=42, shuffle=True)
    

    print('dataset is loaded')
    return X_train, np.array(y_train), X_test, np.array(y_test), used_features
