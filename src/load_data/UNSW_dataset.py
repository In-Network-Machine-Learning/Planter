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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 01:35:19 2019

@author: shayv
"""

import pandas as pd
import os
import category_encoders as ce

import socket, struct
import wget
import pickle

from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import LabelEncoder
###############################################################################
###############################################################################

def encode(ds, columns, encoding='binary'):
    if encoding == 'oneHot':
        ds = pd.get_dummies(ds, columns=columns, prefix=columns)
    elif encoding == 'binary':
        encoder = ce.BinaryEncoder(cols=columns)
        ds = encoder.fit_transform(ds)
    elif encoding == 'label':
        for column in columns:
            print('label encoding for {}'.format(column))
            ds[column] = ds[column].astype('category')
            ds[column] = ds[column].cat.codes
    return ds

def ip2long(ip):
    """
    Convert an IP string to long
    """
    packedIP = socket.inet_aton(ip)
    return struct.unpack("!L", packedIP)[0]

###############################################################################
###############################################################################

def UNSW_NB15(data_dir, drop = True, multi=False, save=True, load=True):

    url = 'https://www.unsw.adfa.edu.au/unsw-canberra-cyber/cybersecurity/ADFA-NB15-Datasets/{}'

    all_filenames = ['UNSW-NB15_1.csv', 'UNSW-NB15_2.csv', 'UNSW-NB15_3.csv', 'UNSW-NB15_4.csv']
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
        return X, y

    if not os.path.exists("datasets"):
        os.makedirs("datasets")

    for file in all_filenames+[features_file]:
        if not os.path.exists(os.path.abspath(os.path.join(os.getcwd(), "../../../"))+'/Data/'+file):
            wget.download(url.format(file), os.path.abspath(os.path.join(os.getcwd(), "../../../"))+'/Data/.')

    # Set features and labels names correctly
    features_df = pd.read_csv(os.path.abspath(os.path.join(os.getcwd(), "../../../"))+'/Data/'+features_file, encoding="ISO-8859-1", engine='python')
    feature_names = features_df['Name']

    dfs = [pd.read_csv(os.path.abspath(os.path.join(os.getcwd(), "../../../"))+'/Data/'+f) for f in all_filenames]
    for df in dfs:
        df.columns = feature_names
    df = pd.concat(dfs)

    # irrelevant data
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

    df = encode(df, ['dsport', 'sport', 'proto', 'state', 'service', 'attack_cat', 'ct_flw_http_mthd'], encoding='label')

    if multi:
        df = df.drop(['Label'], axis=1)
    else:
        df = df.drop(['attack_cat'],axis=1)

    if drop:
        df = df.drop(to_drop, axis=1)

    num_attr = len(df.columns) - 1
    features = df.columns[:num_attr]
    decision = df.columns[num_attr]

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

    X, y = UNSW_NB15_binary(data_dir)

    skf = StratifiedKFold(n_splits=5, random_state=101,shuffle=True)

    for train_index, test_index in skf.split(X, y):
        # The X,y train/test folds are available in this loop
        print("TRAIN:", train_index, "TEST:", test_index)
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]

        used_features = ['sport', 'dsport', 'proto', 'service', 'sbytes']
        used_features = used_features[:int(num_features)]

        X_train = X_train[used_features]
        X_test = X_test[used_features]

        encoder = LabelEncoder()
        y_train = encoder.fit_transform(y_train)
        y_test = encoder.fit_transform(y_test)


    return X_train, y_train, X_test, y_test, used_features
