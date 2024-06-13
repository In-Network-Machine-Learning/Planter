# -----------
# Dataset source: https://github.com/Wimnet/RequetDataSet
# Scenario A used as an example
# -----------
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


import sys
import re
import os

import io


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


def colum_name():
    interval_info_cols = ['Relative_Time', 'Number_Packets_Sent', 'Number_Packets_Received', 'Number_Bytes_Sent', 'Number_Bytes_Received']
    network_info_cols = ['IP_Src', 'IP_Dst', 'Protocol', 'Number_Packets_Sent', 'Number_Packets_Received', 'Number_Bytes_Sent', 'Number_Bytes_Received']
    network_info_cols_num = []
    for i in range(26):
      num_tab = len(network_info_cols)
      for j in range(num_tab):
        name_col = network_info_cols[j]
        name = name_col+'_'+str(i+1)
        network_info_cols_num.append(name)
    playback_info_cols = ['Playback_Event', 'Epoch_Time', 'Start_Time', 'Playback_Progress', 'Video_Length', 'Playback_Quality', 'Buffer_Health', 'Buffer_Progress', 'Buffer_Valid']
    for m in range(len(playback_info_cols)):
      if playback_info_cols[m] == 'Playback_Event':
        playback_info_cols.pop(m)
        for n in range(4):
          name = 'Playback_Event'+'_'+str(4-n)
          playback_info_cols.insert(m, name)
      if playback_info_cols[m] == 'Playback_Quality':
        playback_info_cols.pop(m)
        for p in range(9):
          name = 'Playback_Quality'+'_'+str(p+1)
          playback_info_cols.insert(p+m, name)
    # print(network_info_cols_num)
    # print(playback_info_cols)

    col_name = interval_info_cols + network_info_cols_num + playback_info_cols
    return col_name




def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]

def load_data(num_features, data_dir):


    label_index = 'Buffer_Valid'


    file_dir = data_dir+'/QOE/Data'

    files = []

    for dirpath, dirnames, filenames in os.walk(file_dir):
        for file in filenames:
            if os.path.splitext(file)[1] == '.txt':
              # # print(file.split("_")[1])
              if file.split("_")[1] == 'Jan17':
                if int(file.split("_")[3]) > 25 and int(file.split("_")[3]) < 40:
                  files.append(os.path.join(dirpath, file))

    for i,file in enumerate (files):
        print('read data from file: '+file+' ...')
        with open(file, 'r') as my_file:
          text = my_file.read()
          text = text.replace("[", "")
          text = text.replace("]", "")


        # If you wish to save the updates back into a cleaned up file
        with open(file+'.cleaned', 'w') as my_file:
            my_file.write(text)

        dataset = pd.read_csv(file+'.cleaned', header = None, low_memory=False, dtype={'206':'str'})
        os.remove(file+'.cleaned')
        if  i==0:
            data = pd.DataFrame(dataset)
            # break
        else:
            new_data = pd.DataFrame(dataset)
            data  = pd.concat([data,new_data],axis=0)

    data.columns = colum_name()
    for key in range(len(data[label_index].values)):
        if data[label_index].values[key]=='true':
            data[label_index].values[key] = 1
        elif data[label_index].values[key]=='false':
            data[label_index].values[key] = 0
        else:
            data[label_index].values[key] = -1

        percent = np.int(np.ceil(50*key/len(data[label_index].values)))
        if key%10==0:
            print('\rProcessing the raw Data ['+percent*'#'+(50-percent)*'-'+'] '+str(int(np.round(100*key/len(data[label_index].values))))+"%",end="")

    #Replace values with NaN to -1
    data["Buffer_Progress"].fillna(-1, inplace = True)
    print(data[label_index].value_counts())


    used_features = ['Playback_Quality_8', 'Epoch_Time', 'Playback_Progress',
           'Playback_Quality_9', 'Playback_Event_4', 'Playback_Quality_4',
           'Relative_Time', 'Number_Packets_Sent_1', 'Number_Bytes_Received_1',
           'Number_Packets_Received_1'][:num_features]


    X = copy.deepcopy(data[used_features].astype("int"))
    y = copy.deepcopy(data[label_index].astype("int"))
    del data
    gc.collect()


    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42, shuffle=True)

    print('dataset is loaded')

    return X_train, np.array(y_train), X_test, np.array(y_test), used_features
