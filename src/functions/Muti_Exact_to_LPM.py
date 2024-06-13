# THIS FILE IS PART OF Planter PROJECT
# Planter.py - The core part of the Planter library
#
# THIS PROGRAM IS FREE SOFTWARE TOOL, WHICH MAPS MACHINE LEARNING ALGORITHMS TO DATA PLANE, IS LICENSED UNDER Apache-2.0
# YOU SHOULD HAVE RECEIVED A COPY OF WTFPL LICENSE, IF NOT, PLEASE CONTACT THE FOLLOWING E-MAIL ADDRESSES
#
# Copyright (c) 2020-2021 Changgang Zheng and Riyad Bensoussane
# Copyright (c) Computing Infrastructure Group, Department of Engineering Science, University of Oxford
# E-mail: changgang.zheng@eng.ox.ac.uk or changgangzheng@qq.com
#
# Functions: This file is a M/A table format converter.
#            Please refer to ./Docs/Planter_User_Document.pdf or further information.

import numpy as np
import math
from collections import Counter
from src.functions.Range_to_LPM import *
from src.functions.Range_to_TCAM_Top_Down import *



def Muti_Exact_to_LPM_Concatination(table, key_len, key_name, action_name):
    exact_table = {}
    for num in table:
        binary_key = ''
        for i, kn in enumerate(key_name):
            binary_key = binary_key + ten_to_bin(int(table[num][kn]),int(key_len[i]))
        decimal_key = int(binary_key,2)
        exact_table[decimal_key] = int(table[num][action_name])
    key_max = np.max(list(exact_table.keys()))
    for key in range(key_max):
        if key not in exact_table.keys():
            exact_table[key] = 404404
    code_len = int(np.sum(key_len))
    R_Table= Table_to_LPM(exact_table, code_len)
    LPM_table = {}
    for key in R_Table:
        if R_Table[key][2] != 404404:
            LPM_table[key] = R_Table[key]
    return LPM_table




def Muti_Exact_to_Ternary_Concatination(table, key_len, key_name, action_name):
    exact_table = {}
    for num in table:
        binary_key = ''
        for i, kn in enumerate(key_name):
            binary_key = binary_key + ten_to_bin(int(table[num][kn]),int(key_len[i]))
        decimal_key = int(binary_key,2)
        exact_table[decimal_key] = int(table[num][action_name])
    key_max = np.max(list(exact_table.keys()))
    for key in range(key_max):
        if key not in exact_table.keys():
            exact_table[key] = 404404
    code_len = int(np.sum(key_len))
    R_Table= Table_to_TCAM(exact_table, code_len)
    Ternary_table = {}
    for key in R_Table:
        if R_Table[key][2] != 404404:
            Ternary_table[key] = R_Table[key]
    return Ternary_table
