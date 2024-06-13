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

def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]

def ip2long(ip):
    """
    Convert an IP string to long
    """
    packedIP = socket.inet_aton(ip)
    return struct.unpack("!L", packedIP)[0]

# Convert IP to bin
def ip2bin(ip):
    ip1 = '.'.join([bin(int(x)+256)[3:] for x in ip.split('.')])
    return ip1

# Convert IP to hex
def ip2hex(ip):
    ip1 = '-'.join([hex(int(x)+256)[3:] for x in ip.split('.')])
    return ip1

def bin2dec(ip):
    return int(ip,2)

def load_data(num_features, data_dir):


    label_index = ' Label'
    # normal_label = 'BENIGN'

    file_dir = data_dir+'/CICIDS/'

    files = []

    for dirpath, dirnames, filenames in os.walk(file_dir):
        for file in filenames:
          # print(file.split("-")[0] == 'Friday')
          if file.split(".")[1] == 'pcap_ISCX' and file.split("-")[0] == 'Friday':
                files.append(os.path.join(dirpath, file))

    for i,file in enumerate (files):
        print('read data from file: '+file+' ...')
        dataset = pd.read_csv(file)
        if  i==0:
            data = pd.DataFrame(dataset)
            # break
        else:
            new_data = pd.DataFrame(dataset)
            data  = pd.concat([data,new_data],axis=0)

    data[['srcip_part_1', 'srcip_part_2', 'srcip_part_3', 'srcip_part_4']] = data[' Source IP'].apply(ip2bin).str.split('.',expand=True)
    data[['dstip_part_1', 'dstip_part_2', 'dstip_part_3', 'dstip_part_4']] = data[' Destination IP'].apply(ip2bin).str.split('.',expand=True)

    data['srcip_part_1'] = data['srcip_part_1'].apply(bin2dec)
    data['srcip_part_2'] = data['srcip_part_2'].apply(bin2dec)
    data['srcip_part_3'] = data['srcip_part_3'].apply(bin2dec)
    data['srcip_part_4'] = data['srcip_part_4'].apply(bin2dec)
    data['dstip_part_1'] = data['dstip_part_1'].apply(bin2dec)
    data['dstip_part_2'] = data['dstip_part_2'].apply(bin2dec)
    data['dstip_part_3'] = data['dstip_part_3'].apply(bin2dec)
    data['dstip_part_4'] = data['dstip_part_4'].apply(bin2dec)

    data[' Source IP'] = data[' Source IP'].apply(ip2long)
    data[' Destination IP'] = data[' Destination IP'].apply(ip2long)
    print('data.head: ', data.head())

    for key in range(len(data[label_index].values)):
        if data[label_index].values[key]=='BENIGN':
            data[label_index].values[key] = 0
        else:
            data[label_index].values[key] = 1



        percent = np.int(np.ceil(50*key/len(data[label_index].values)))
        if key%10==0:
            print('\rProcessing the raw Data ['+percent*'#'+(50-percent)*'-'+'] '+str(int(np.round(100*key/len(data[label_index].values))))+"%",end="")

    #Replace values with NaN, inf, -inf
    # data.replace([np.inf, -np.inf], np.nan)
    print('')
    data.replace([np.inf, -np.inf], np.nan)
    #Remove rows containing NaN
    data.dropna(how="any", inplace = True)
    data = data[data.replace([np.inf, -np.inf], np.nan).notnull().all(axis=1)]

    data.describe()
    data.info()
    print(data[label_index].value_counts())



    used_features = [' Source Port', ' Destination Port', ' Protocol', 'srcip_part_1', 'dstip_part_4'][:num_features]


    X = copy.deepcopy(data[used_features].astype("int"))
    y = copy.deepcopy(data[label_index].astype("int"))
    del data
    gc.collect()



    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42, shuffle=True)

    print('dataset is loaded')

    return X_train, np.array(y_train), X_test, np.array(y_test), used_features
