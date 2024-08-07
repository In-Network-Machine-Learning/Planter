# THIS FILE IS PART OF Planter PROJECT
# Planter.py - The core part of the Planter library
#
# THIS PROGRAM IS FREE SOFTWARE TOOL, WHICH MAPS MACHINE LEARNING ALGORITHMS TO DATA PLANE, IS LICENSED UNDER Apache-2.0
# YOU SHOULD HAVE RECEIVED A COPY OF WTFPL LICENSE, IF NOT, PLEASE CONTACT THE FOLLOWING E-MAIL ADDRESSES
#
# E-mail: changgang.zheng@eng.ox.ac.uk or changgangzheng@qq.com
#
# Functions: This file loads the data from the given dataset.
#            Please refer to ./Docs/Planter_User_Document.pdf or further information.
# -*- coding: utf-8 -*-
"""unsw-nb15 prep-5tuple-rf.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1UjY3A4MPT6yCdmVgQ2G0qk_8bPmj5A2Q
"""

# !pip install wget

from glob import glob
from time import time
import warnings
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, MinMaxScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier

import numpy as np
import pandas as pd
 
import pickle

import os

import socket, struct
import wget
from sklearn.model_selection import StratifiedKFold

# from google.colab import drive
# drive.mount('/content/gdrive')

num_features = 13
data_dir = "/content/gdrive/My Drive/"

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

def UNSW_NB15(data_dir, drop = False, multi=False, save=False, load=False):

    url = 'https://cloudstor.aarnet.edu.au/plus/s/2DhnLGDdEECo4ys?path=%2FUNSW-NB15%20-%20CSV%20Files/{}'

    all_filenames = ['UNSW-NB15_1.csv']
    features_file = 'NUSW-NB15_features.csv'
    # Don;t use local pickle when running over AWS instance
    if 'ip-' in socket.gethostname():
        load_dataset = False
        save_dataset = False

    if multi:
        postfix = 'multi'
    else:
        postfix = 'binary'

    if load:
        X, y = pickle.load(open(data_dir+"/UNSW-NB15/UNSW_NB15_{}.pickle".format(postfix), "rb"))
        # data = pd.read_csv(data_dir+"/UNSW-NB15/UNSW_NB15_1.csv")
        return X, y

    if not os.path.exists("datasets"):
        os.makedirs("datasets")

    # Set features and labels names correctly
    features_df = pd.read_csv(data_dir+'/UNSW-NB15/'+features_file, encoding="ISO-8859-1", engine='python')
    feature_names = features_df['Name']
    # print('feature_names = features_df[Name]... ')
    dfs = []
    for file in all_filenames:
        path = data_dir+'/UNSW-NB15/'+file
        dfs.append(pd.read_csv(path, header = None, delimiter=','))
        # print('reading... ', path)
    for df in dfs:
        df.columns = feature_names
        # print('reading... ', df)
    df = pd.concat(dfs)
    # print('df.columns = feature_names... ')
    # irrelevant data

    df[['srcip_part_1', 'srcip_part_2', 'srcip_part_3', 'srcip_part_4']] = df['srcip'].apply(ip2bin).str.split('.',expand=True)
    df[['dstip_part_1', 'dstip_part_2', 'dstip_part_3', 'dstip_part_4']] = df['dstip'].apply(ip2bin).str.split('.',expand=True)

    df['srcip_part_1'] = df['srcip_part_1'].apply(bin2dec)
    df['srcip_part_2'] = df['srcip_part_2'].apply(bin2dec)
    df['srcip_part_3'] = df['srcip_part_3'].apply(bin2dec)
    df['srcip_part_4'] = df['srcip_part_4'].apply(bin2dec)
    df['dstip_part_1'] = df['dstip_part_1'].apply(bin2dec)
    df['dstip_part_2'] = df['dstip_part_2'].apply(bin2dec)
    df['dstip_part_3'] = df['dstip_part_3'].apply(bin2dec)
    # print(df['dstip_part_4'].value_counts())
    df['dstip_part_4'] = df['dstip_part_4'].apply(bin2dec)
    # print(df['dstip_part_4'].value_counts())

    if drop:
        to_drop = ['srcip', 'dstip', 'sttl', 'dttl', 'sloss', 'dloss', 'swin', 'dwin', 'stcpb', 'dtcpb',
                   'trans_depth', 'res_bdy_len', 'Sjit', 'Djit', 'Stime', 'Ltime', 'tcprtt', 'synack',
                   'ackdat', 'ct_flw_http_mthd', 'is_ftp_login', 'ct_ftp_cmd']
    else:
        df['srcip'] = df['srcip'].apply(ip2long)
        df['dstip'] = df['dstip'].apply(ip2long)
        df = df.drop(['is_ftp_login','ct_ftp_cmd'], axis=1)


    attack_types = df['attack_cat'].unique()
    attack_types[0] = 'Normal'


    if multi:
        df = df.drop(['Label'], axis=1)
    else:
        df = df.drop(['attack_cat'],axis=1)

    if drop:
        df = df.drop(to_drop, axis=1)

    # protocol name -> protocol num
    proto_num_df = pd.read_csv(data_dir+'/ipprotocolnumbers.csv', delimiter=';')
    proto_num_df.rename(columns={'Keyword': 'proto'}, inplace=True)
    print('proto_num_df.head(): ', proto_num_df.head())
    proto_num_df['proto'] = proto_num_df['proto'].str.lower()
    proto_num_df['Decimal'] = proto_num_df['Decimal'].astype(int)
    dict_proto = proto_num_df.set_index('proto')['Decimal'].to_dict()
    
    df.replace({"proto": dict_proto},inplace=True)
    proto_list = list(range(0, 255))
    df = df[df['proto'].isin(proto_list)]
    df['proto'] = df['proto'].astype(int)
    print('df[proto].value_counts(): ', df['proto'].value_counts())


    df['sport'].str.replace('0x000b', '11').astype(int)
    df['sport'].str.replace('0x000c', '12').astype(int)
    df['dsport'].str.replace('-', '0').astype(int)
    df['sport'].str.replace('-', '0').astype(int)
    df['dsport'] = df['dsport'].fillna(0)
    df['sport'] = df['sport'].fillna(0)


    num_attr = len(df.columns)
    features = df.columns[:num_attr]
    decision = 'Label'

    if save:
        pickle.dump((df[features], df[decision]), open("UNSW_NB15_{}.pickle".format(postfix), "wb"))

    return df[features], df[decision]

###############################################################################
###############################################################################

def UNSW_NB15_binary(data_dir):
    return UNSW_NB15(data_dir, multi=False)

def UNSW_NB15_multi():
    return UNSW_NB15(multi=True, save=False, load=True)

def load_data(num_features, data_dir):
    print('Loading Data... ')

    X, y = UNSW_NB15_binary(data_dir)

    skf = StratifiedKFold(n_splits=5, random_state=101,shuffle=True)

    for train_index, test_index in skf.split(X, y):
        # The X,y train/test folds are available in this loop
        # print("TRAIN:", train_index, "TEST:", test_index)

        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]
        used_features = ['sport', 'dsport', 'proto', 'srcip_part_1', 'dstip_part_4']
        used_features = used_features[:int(num_features)]
        X_train = X_train[used_features]
        X_test = X_test[used_features]
        X_train = X_train.astype(int)
        X_test = X_test.astype(int)



    return X_train, np.array(y_train), X_test, np.array(y_test), used_features

X_train, y_train, X_test, y_test, used_features = load_data(num_features, data_dir)

X_train.info()

X_train.to_csv('unswdebug.csv')

import matplotlib
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
rfc = RandomForestClassifier()

# fit random forest classifier on the training set
rfc.fit(X_train, y_train)
# extract important features
score = np.round(rfc.feature_importances_,3)
importances = pd.DataFrame({'feature':X_train.columns,'importance':score})
importances = importances.sort_values('importance',ascending=False).set_index('feature')

print(importances)

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import classification_report


num_depth = 4
num_trees = 5
max_leaf_nodes = 1000
  
rfc = RandomForestClassifier(n_estimators=num_trees, max_depth=num_depth, max_leaf_nodes=max_leaf_nodes)
rfc.fit(X_train, y_train)

sklearn_y_predict = rfc.predict(X_test)


result = classification_report(y_test, sklearn_y_predict, digits= 3)
print('\n',result)

