# THIS FILE IS PART OF Planter PROJECT
# Planter.py - The core part of the Planter library
#
# THIS PROGRAM IS FREE SOFTWARE TOOL, WHICH MAPS MACHINE LEARNING ALGORITHMS TO DATA PLANE, IS LICENSED UNDER Apache-2.0
# YOU SHOULD HAVE RECEIVED A COPY OF WTFPL LICENSE, IF NOT, PLEASE CONTACT THE FOLLOWING E-MAIL ADDRESSES
#
# Copyright (c) Computing Infrastructure Group, Department of Engineering Science, University of Oxford
# E-mail: changgang.zheng@eng.ox.ac.uk or changgangzheng@qq.com
#
# Functions: This file loads the data from the given dataset.
#            Please refer to ./Docs/Planter_User_Document.pdf or further information.

import numpy as np
import pandas as pd
import csv
import time
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
global label_list  # label_list is a global variable


# Define kdd99 data preprocessing function
def preHandel_data():
    source_file = '/home/Data/KDD99/kddcup.data.corrected'
    handled_file = '/home/Data/KDD99/kddcup.data.corrected.csv'
    data_file = open(handled_file, 'w', newline='')  # Add the parameter newline='' in python3.x to avoid extra blank lines in the written file
    with open(source_file, 'r') as data_source:
        csv_reader = csv.reader(data_source)
        csv_writer = csv.writer(data_file)
        count = 0  # Record the number of rows of data, initialized to 0
        for row in csv_reader:
            temp_line = np.array(row)  # Store each row of data into the temp_line array
            temp_line[1] = handleProtocol(row)  # Convert the 3 protocol types in the source file row to numerical identifiers
            temp_line[2] = handleService(row)  # Convert the 70 network service types in the source file row to numerical identifiers
            temp_line[3] = handleFlag(row)  # Convert the 11 network connection states in the source file row to numerical identifiers
            temp_line[41] = handleLabel(row)  # Convert the 23 attack types in the source file row to numerical identifiers
            csv_writer.writerow(temp_line)
            count += 1
            # Output the modified state in each row of data
            print(count, 'status:', temp_line[1], temp_line[2], temp_line[3], temp_line[41])
        data_file.close()


# Convert the corresponding non-numeric types to numerical identifiers, i.e., convert symbolic data to numeric data
def find_index(x, y):
    return [i for i in range(len(y)) if y[i] == x]


# Define a function to convert the 3 protocol types in the source file row to numerical identifiers
def handleProtocol(input):
    protocol_list = ['tcp', 'udp', 'icmp']
    if input[1] in protocol_list:
        return find_index(input[1], protocol_list)[0]


# Define a function to convert the 70 network service types in the source file row to numerical identifiers
def handleService(input):
    service_list = ['aol', 'auth', 'bgp', 'courier', 'csnet_ns', 'ctf', 'daytime', 'discard', 'domain', 'domain_u',
                    'echo', 'eco_i', 'ecr_i', 'efs', 'exec', 'finger', 'ftp', 'ftp_data', 'gopher', 'harvest',
                    'hostnames',
                    'http', 'http_2784', 'http_443', 'http_8001', 'imap4', 'IRC', 'iso_tsap', 'klogin', 'kshell',
                    'ldap',
                    'link', 'login', 'mtp', 'name', 'netbios_dgm', 'netbios_ns', 'netbios_ssn', 'netstat', 'nnsp',
                    'nntp',
                    'ntp_u', 'other', 'pm_dump', 'pop_2', 'pop_3', 'printer', 'private', 'red_i', 'remote_job', 'rje',
                    'shell',
                    'smtp', 'sql_net', 'ssh', 'sunrpc', 'supdup', 'systat', 'telnet', 'tftp_u', 'tim_i', 'time',
                    'urh_i', 'urp_i',
                    'uucp', 'uucp_path', 'vmnet', 'whois', 'X11', 'Z39_50']
    if input[2] in service_list:
        return find_index(input[2], service_list)[0]


def attack_class(train):
    train.loc[(train['label'].isin(['back.','land.','neptune.','pod.','smurf.','teardrop.'])),'label_type']='DOS'
    train.loc[train['label'].isin(['ipsweep.','nmap.','portsweep.','satan.']),'label_type']='Probing'
    train.loc[train['label'].isin(['ftp_write.','guess_passwd.','imap.','multihop.','phf.','spy.','warezclient.','warezmaster.']),'label_type']='R2L'
    train.loc[train['label'].isin(['buffer_overflow.','loadmodule.','perl.','rootkit.']),'label_type']='U2R'
    train.loc[train['label']=='normal.','label_type']='Normal'
    return train

def attack_class2(train):
    train.loc[(train['label'].isin(['back','land','neptune','pod','smurf','teardrop'])),'label_type']='DOS'
    train.loc[train['label'].isin(['ipsweep','nmap','portsweep','satan']),'label_type']='Probing'
    train.loc[train['label'].isin(['ftp_write','guess_passwd','imap','multihop','phf','spy','warezclient','warezmaster']),'label_type']='R2L'
    train.loc[train['label'].isin(['buffer_overflow','loadmodule','perl','rootkit']),'label_type']='U2R'
    train.loc[train['label']=='normal','label_type']='Normal'
    return train


cleanup_nums = {"protocol_type":     {"tcp": 1, "icmp": 2, "udp": 3},
                "service": {"vmnet": 1, "smtp": 2, "ntp_u":3, "shell":4, "kshell":5, "aol":6, "imap4":7, "urh_i":8, "netbios_ssn":9,
                           "tftp_u":10, "mtp":11, "uucp":12, "nnsp":13, "echo":14, "tim_i":15, "ssh":16, "iso_tsap":17, "time":18,
                           "netbios_ns":19,"systat":20, "hostnames":21, "login":22, "efs":23, "supdup":24, "http_8001":25, "courier":26,
                           "ctf":27,"finger":28,"nntp":29,"ftp_data":30,"red_i":31,"ldap":32,"http":33,"ftp":34,"pm_dump":35,"exec":36,
                           "klogin":37,"auth":38,"netbios_dgm":39,"other":40,"link":41,"X11":42,"discard":43,"private":44,"remote_job":45,
                           "IRC":46,"daytime":47,"pop_3":48,"pop_2":49,"gopher":50,"sunrpc":51,"name":52,"rje":53,"domain":54,"uucp_path":55,
                           "http_2784":56,"Z39_50":57,"domain_u":58,"csnet_ns":59,"whois":60,"eco_i":61,"bgp":62,"sql_net":63,"printer":64,
                           "telnet":65,"ecr_i":66,"urp_i":67,"netstat":68,"http_443":69,"harvest":70},
               "flag":{"RSTR":1,"S3":2,"SF":3,"RSTO":4,"SH":5,"OTH":6,"S2":7,"RSTOS0":8,"S1":9,"S0":10,"REJ":11},
               "label_type":{"Normal":1,"DOS":2,"Probing":3,"R2L":4,"U2R":5}}
attack_map={"label_type":{"Normal":0,"DOS":1,"Probing":1,"R2L":1,"U2R":1}}

column = ["duration","protocol_type","service","flag","src_bytes","dst_bytes","land","wrong_fragment","urgent","hot","num_failed_logins","logged_in","lnum_compromised","lroot_shell","lsu_attempted","lnum_root","lnum_file_creations","lnum_shells","lnum_access_files","lnum_outbound_cmds","is_host_login","is_guest_login","count","srv_count","serror_rate","srv_serror_rate","rerror_rate","srv_rerror_rate","same_srv_rate","diff_srv_rate","srv_diff_host_rate","dst_host_count","dst_host_srv_count","dst_host_same_srv_rate","dst_host_diff_srv_rate","dst_host_same_src_port_rate","dst_host_srv_diff_host_rate","dst_host_serror_rate","dst_host_srv_serror_rate","dst_host_rerror_rate","dst_host_srv_rerror_rate","label"]


# Define a function to convert the 11 network connection states in the source file row to numerical identifiers
def handleFlag(input):
    flag_list = ['OTH', 'REJ', 'RSTO', 'RSTOS0', 'RSTR', 'S0', 'S1', 'S2', 'S3', 'SF', 'SH']
    if input[3] in flag_list:
        return find_index(input[3], flag_list)[0]


# Define a function to convert the attack types in the source file row to numerical identifiers (22 attack types appear in the training set, while the remaining 17 types only appear in the test set)
def handleLabel(input):
    global label_list  # Use and modify the global variable inside the function
    if input[41] in label_list:
        return find_index(input[41], label_list)[0]
    else:
        label_list.append(input[41])
        return find_index(input[41], label_list)[0]









def load_data(num_features, data_dir):
    print("train data loading...")
    train = pd.read_csv(data_dir+'/KDD99/kddcup.data_10_percent_corrected')
    train.columns = column
    train.insert(0, 'label_type', 'NAN')


    datapre = train

    datapre.replace(cleanup_nums, inplace=True)


    train = attack_class(datapre)

    train['label_type'].value_counts()

    train.replace(attack_map, inplace=True)

    train.drop('label', axis=1, inplace=True)


    used_features = column[:num_features]
    used_features = ["duration","protocol_type","service","flag","land"][:num_features]
    X = train[used_features]
    y = train['label_type']


    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42, shuffle=True)

    return X_train, np.array(y_train), X_test, np.array(y_test), used_features




if __name__ == '__main__':



    start_time = time.clock()
    global label_list  # Declare a global variable list and initialize it to empty
    label_list = []
    preHandel_data()
    end_time = time.clock()
    print("Running time:", (end_time - start_time))  # Output the running time of the program
