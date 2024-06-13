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

import os
from zipfile import ZipFile
import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier, IsolationForest
import xgboost as xgb

import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, make_scorer, f1_score, accuracy_score, roc_auc_score, precision_score, recall_score, balanced_accuracy_score
from sklearn.tree import export_graphviz
from IPython.display import Image
from subprocess import call
import pickle
import os
import matplotlib.pyplot as plt
import logging
import numpy as np
from sklearn.utils import resample
import argparse
import time
from scapy.all import *
from random import randint
from src.functions.normalization import *

def fit_row_data(row_data, col_width):
    return [d.ljust(col_width)[:col_width] for d in row_data]

def ten_to_bin(num, count):
    num = bin(num).lstrip('0b')
    if len(num) != count:
        cont = count - len(num)
        num = int(cont) * '0' + num
    return num

def list_to_byte_list(in_list, width):
    # width should be the multiplication of 8 and equal or higher than 8
    binary_raw = ''
    for idx in range(len(in_list)):
        binary_raw += ten_to_bin(int(in_list[idx]), width)
    byte_list = []
    num_idx = int(len(binary_raw) / 8)
    for idx in range(num_idx):
        byte_list += [int(binary_raw[:8], 2)]
        binary_raw = binary_raw[8:]
    return byte_list


def load_data(num_features, data_dir, resp=0.015, main_sample_ratio=0.25, strong_sample_ratio=0.3):

    dataset = pickle.load(open(data_dir+"/Jane-Street-Market-Prediction/finance_dataset_vanilla.pkl", "rb"))

    print('dataset is extracted')

    dataset['action'] = -1
    # TODO: might consider weight*resp instead of resp

    # 3 labels version b
    dataset.loc[dataset['resp'] <= -1*resp, 'action'] = 1 # strong sell
    dataset.loc[(dataset['resp'] > -1*resp) & (dataset['resp'] < resp), 'action'] = 0 # buy / hold / sell
    dataset.loc[dataset['resp'] >= resp, 'action'] = 1 # strong buy

    if not dataset.loc[dataset['action'] == -1].empty:
        raise Exception('Not all rows have been assigned with an action value')

    to_drop = ['date', 'resp_1', 'resp_2', 'resp_3', 'resp_4', 'ts_id', 'resp', 'weight']
    dataset = dataset.drop(columns=to_drop, axis=1)

    # resample label 2 instances (buy / hold / sell)
    main_dataset = dataset.loc[(dataset['action'] == 0)]
    main_dataset_sampled = resample(main_dataset, n_samples=round(main_dataset.shape[0]*main_sample_ratio), random_state=0)

    strong_dataset = dataset.loc[(dataset['action'] == 1)]
    strong_dataset_sampled = resample(strong_dataset, n_samples=round(strong_dataset.shape[0]*strong_sample_ratio), random_state=0)


    sampled_dataset = pd.concat([strong_dataset_sampled, main_dataset_sampled])

    info = {
        'Sell/Hold/Buy [#]': main_dataset_sampled.shape[0],
        'Strong Sell/Buy [#]': strong_dataset_sampled.shape[0],
        'Sell/Hold/Buy [%]': '{:.2f}'.format(100*main_dataset_sampled.shape[0]/sampled_dataset.shape[0]),
        'Strong Sell/Buy [%]': '{:.2f}'.format(100*strong_dataset_sampled.shape[0]/sampled_dataset.shape[0]),
        'resp': resp,
        'main_sample_ratio': main_sample_ratio,
        'strong_sample_ratio': strong_sample_ratio,
    }

    print(info)

    features = sampled_dataset.columns
    features = features.drop('action')
    sampled_dataset = sampled_dataset.fillna(0) # replace NaN with zero

    #pickle.dump([sampled_dataset[features], sampled_dataset['action'], info], open(pickle_filename, "wb"))
    X = sampled_dataset[features]
    y = sampled_dataset['action']
    used_features =  ['feature_43', 'feature_42', 'feature_124', 'feature_126', 'feature_120', 'feature_45', 'feature_128',
                        'feature_122', 'feature_44', 'feature_114', 'feature_31', 'feature_5', 'feature_41', 'feature_64', 'feature_53',
                        'feature_33', 'feature_90', 'feature_55', 'feature_39', 'feature_57', 'feature_108',
                        'feature_6', 'feature_102', 'feature_116', 'feature_95', 'feature_3', 'feature_107', 'feature_119', 'feature_83',
                        'feature_58', 'feature_96', 'feature_63', 'feature_62', 'feature_37', 'feature_84', 'feature_60', 'feature_61',
                        'feature_92', 'feature_40', 'feature_35', 'feature_121', 'feature_77', 'feature_4', 'feature_27', 'feature_89',
                        'feature_101', 'feature_113', 'feature_38', 'feature_110', 'feature_125', 'feature_29', 'feature_68', 'feature_67',
                        'feature_104', 'feature_59', 'feature_66', 'feature_65', 'feature_11', 'feature_127', 'feature_21', 'feature_47',
                        'feature_13', 'feature_23', 'feature_9', 'feature_56', 'feature_86', 'feature_129', 'feature_15', 'feature_25',
                        'feature_123', 'feature_17', 'feature_54', 'feature_7', 'feature_51', 'feature_19', 'feature_98', 'feature_32',
                        'feature_78', 'feature_34', 'feature_46', 'feature_22', 'feature_12', 'feature_30', 'feature_117', 'feature_50',
                        'feature_49', 'feature_69', 'feature_36', 'feature_80', 'feature_72', 'feature_14', 'feature_93', 'feature_24',
                        'feature_18', 'feature_28', 'feature_8', 'feature_48', 'feature_74', 'feature_20', 'feature_26', 'feature_10',
                        'feature_70', 'feature_16', 'feature_111', 'feature_1', 'feature_87', 'feature_71', 'feature_52', 'feature_81',
                        'feature_75', 'feature_2', 'feature_112', 'feature_109', 'feature_105', 'feature_118', 'feature_73', 'feature_76',
                        'feature_82', 'feature_79', 'feature_99', 'feature_115', 'feature_88', 'feature_94', 'feature_85', 'feature_91',
                        'feature_100', 'feature_106', 'feature_97', 'feature_103', 'feature_0'][:num_features]

    X = X[used_features]



    for i in range(np.shape(X)[0]):
        fit_row = fit_row_data(X.values[i].astype(str), 2)
        for idx, x_str in enumerate(fit_row):
            x_ascii_bin = ''.join(ten_to_bin(ord(c),8) for c in x_str)
            X.values[i][idx] = int(x_ascii_bin,2)
        percent = np.int(np.ceil(50 * i / np.shape(X)[0]))
        if i % 10 == 0:
            print('\rProcessing the raw Data [' + percent * '#' + (50 - percent) * '-' + '] ' + str(int(np.round(100 * i / np.shape(X)[0]))) + "%", end="")
    print('')
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    X_train[used_features] = X_train[used_features].astype('int')
    X_test[used_features] = X_test[used_features].astype('int')
    print('dataset is loaded')

    return X_train, np.array(y_train), X_test, np.array(y_test), used_features
