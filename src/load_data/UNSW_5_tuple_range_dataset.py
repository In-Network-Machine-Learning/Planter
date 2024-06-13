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
import numpy as np

from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import LabelEncoder
from src.functions.normalization import *
###############################################################################
###############################################################################
def ip2long(ip):
    """
    Convert an IP string to long
    """
    packedIP = socket.inet_aton(ip)
    return struct.unpack("!L", packedIP)[0]


def bin2dec(ip):
    return int(ip,2)

# Convert IP to bin
def ip2bin(ip):
    ip1 = '.'.join([bin(int(x)+256)[3:] for x in ip.split('.')])
    return ip1

# Convert IP to hex
def ip2hex(ip):
    ip1 = '-'.join([hex(int(x)+256)[3:] for x in ip.split('.')])
    return ip1

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
        return X, y

    if not os.path.exists("datasets"):
        os.makedirs("datasets")

    # Set features and labels names correctly
    features_df = pd.read_csv(data_dir+'/UNSW-NB15/'+features_file, encoding="ISO-8859-1", engine='python')
    feature_names = features_df['Name']
    dfs = []
    for file in all_filenames:
        path = data_dir+'/UNSW-NB15/'+file
        dfs.append(pd.read_csv(path, header = None))
    for df in dfs:
        df.columns = feature_names
    df = pd.concat(dfs)
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
    df['dstip_part_4'] = df['dstip_part_4'].apply(bin2dec)


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


    proto_list = ['udp', 'tcp']
    df = df[df['proto'].isin(proto_list)]
    df.loc[df['proto'] == 'udp', 'proto'] = 17
    df.loc[df['proto'] == 'tcp', 'proto'] = 6



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
    # print('Done')

    skf = StratifiedKFold(n_splits=5, random_state=101,shuffle=True)

    used_features = ['sport', 'dsport', 'proto', 'srcip_part_1', 'dstip_part_1'][:num_features]  # 5-tuple
    X = X[used_features]
    X = X.astype(int)
    for f in used_features:
        X[[f]] = MaxMinNormalization_with_scale(X[[f]], 500)

    for train_index, test_index in skf.split(X, y):


        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]

        X_train = X_train[used_features]
        X_test = X_test[used_features]
        X_train = X_train.astype(int)
        X_test = X_test.astype(int)



    return X_train, np.array(y_train), X_test, np.array(y_test), used_features
