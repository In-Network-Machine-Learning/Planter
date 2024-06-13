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

@author: Changgang
"""

import pandas as pd
import os
import category_encoders as ce

import socket, struct
import wget
import pickle

from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import LabelEncoder


def load_data(num_features, data_dir):
    with open('./Data/UNSW/UNSW.pkl', 'rb') as f:
        data = pickle.load(f)

    X_train = data['train_X']
    y_train = data['train_y']
    X_test = data['test_X']
    y_test = data['test_y']
    used_features = data['used_features']
    return X_train, y_train, X_test, y_test, used_features
