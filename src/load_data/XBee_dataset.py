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

import numpy as np
import pandas as pd
from tensorflow import keras

def load_data(num_features, data_dir):

    train_data=[]
    train_labels=[]
    test_data=[]
    test_labels=[]


    dataset_dir=data_dir+'/XBee/'
    dataset_name=['xbee']


    for dataset in dataset_name:
        lines=open(dataset_dir+dataset+'_normal.txt','r').readlines()
        for i,line in enumerate(lines):
            strlist=np.array(line.split())
            if i%5==0:
                test_data.append(strlist.astype(np.float))
                test_labels.append(0)
            else:
                train_data.append(strlist.astype(np.float))
                train_labels.append(0)

    for dataset in dataset_name:
        lines=open(dataset_dir+dataset+'_attack.txt','r').readlines()
        for i,line in enumerate(lines):
            strlist=np.array(line.split())
            if i%5==0:
                test_data.append(strlist.astype(np.float))
                test_labels.append(1)
            else:
                train_data.append(strlist.astype(np.float))
                train_labels.append(1)



    N = 128

    train_labels = np.array(train_labels)
    train_data = np.array(train_data)
    train_data = keras.preprocessing.sequence.pad_sequences(train_data,
                                                            value=0,
                                                            padding='post',
                                                            maxlen=N)
    test_labels = np.array(test_labels)
    test_data = np.array(test_data)
    test_data = keras.preprocessing.sequence.pad_sequences(test_data,
                                                           value=0,
                                                           padding='post',
                                                           maxlen=N)

    used_features = [42, 41, 12, 33, 38, 34, 37, 31, 32, 39, 29, 45, 36]

    used_features = used_features[:int(num_features)]

    X_train = pd.DataFrame(np.array(train_data)).astype(int)[used_features]
    y_train = np.array(train_labels)

    X_test = pd.DataFrame(np.array(test_data)).astype(int)[used_features]
    y_test = np.array(test_labels)


    return X_train, y_train, X_test, y_test, used_features
