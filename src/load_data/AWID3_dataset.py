########################################################################
# THIS FILE IS PART OF Planter PROJECT
# E-mail: changgang.zheng@eng.ox.ac.uk or changgangzheng@qq.com
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at :
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#########################################################################
#
# Functions: This file loads the data from the given dataset.
#            Please refer to ./Docs/Planter_User_Document.pdf or further information.

import copy

import numpy as np
import pandas as pd
import os
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import socket
import struct
import gc
import time

def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]

def load_data(num_features, data_dir):
    start_time = time.clock()
    global label_list  # Declare a global variable list and initialize it to empty
    label_index = 'Label'
    # normal_label = 'BENIGN'

    file_dir = '/home/Data/AWID3/CSV'

    files = []

    for dirpath, dirnames, filenames in os.walk(file_dir):
        for file in filenames:
            if os.path.splitext(file)[1] == '.csv':
                files.append(os.path.join(dirpath, file))

    used_features = ['ip.dst', 'ip.proto', 'ip.src', 'ip.ttl', 'ip.version', 'Label']

    is_first = True
    for i, file in enumerate(files):
        if '12.Evil_Twin' not in file:
            continue
        print('\rread data from file: ' + file + ' ...', end="")
        dataset = pd.read_csv(file, low_memory=False)
        if is_first == True:
            data = pd.DataFrame(dataset)[used_features].fillna(0)
            is_first = False
            # break
        else:
            new_data = pd.DataFrame(dataset)[used_features].fillna(0)
            data = pd.concat([data, new_data], axis=0)
            # break
    end_time = time.clock()
    print("\nRunning time:", (end_time - start_time))  # 输出程序运行时间

    data.index = range(len(data))

    wrong_index = []
    for key in range(len(data[label_index].values)):
        try:
            if data[label_index].values[key] == 'Normal' or data[label_index].values[key] == 0 :
                data[label_index].values[key] = 0
            else:
                data[label_index].values[key] = 1
            if data['ip.src'].values[key]!=0:
                data['ip.src'].values[key] = ip2int(data['ip.src'].values[key])
            if data['ip.dst'].values[key] != 0:
                data['ip.dst'].values[key] = ip2int(data['ip.dst'].values[key])
        except:
            wrong_index+=[key]
        percent = np.int(np.ceil(50*key/len(data[label_index].values)))
        if key%10==0:
            print('\rProcessing the raw Data ['+percent*'#'+(50-percent)*'-'+'] '+str(int(np.round(100*key/len(data[label_index].values))))+"%",end="")

    data = data.drop(index=wrong_index, axis= 0)
    data.index = range(len(data))


    data.describe()
    data.info()
    print(data[label_index].value_counts())

    used_features = used_features[:num_features]


    X = copy.deepcopy(data[used_features].astype("int"))
    y = copy.deepcopy(data[label_index].astype("int"))
    del data
    gc.collect()


    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42, shuffle=True)

    print('dataset is loaded')

    return X_train, np.array(y_train), X_test, np.array(y_test), used_features













