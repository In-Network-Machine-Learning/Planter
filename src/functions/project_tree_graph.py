# THIS FILE IS PART OF Planter PROJECT
# Planter.py - The core part of the Planter library
#
# THIS PROGRAM IS FREE SOFTWARE TOOL, WHICH MAPS MACHINE LEARNING ALGORITHMS TO DATA PLANE, IS LICENSED UNDER Apache-2.0
# YOU SHOULD HAVE RECEIVED A COPY OF THE LICENSE, IF NOT, PLEASE CONTACT THE FOLLOWING E-MAIL ADDRESSES
#
# Copyright (c) 2020-2021 Changgang Zheng
# Copyright (c) Computing Infrastructure Lab, Department of Engineering Science, University of Oxford
# Copyright (c) Author from this link: https://blog.csdn.net/zichen_ziqi/article/details/107775556
# E-mail: changgang.zheng@eng.ox.ac.uk or changgangzheng@qq.com
#
# Functions: This file plots all the files and folders in the frameworks.
#            Please refer to ./Docs/Planter_User_Document.pdf or further information.

import os
import os.path
ignore_list = ['.git', '.DS_Store','.idea','.xml','.iml', '__pycache__']

def check_include(string, sub_str_list):
    for sub_str in sub_str_list:
        if sub_str in string:
            return True
    return False

def draw_project_tree_graph(path, depth):
    global ignore_list
    if depth == 0:
        print("root:[" + path + "]")

    for item in os.listdir(path):
        if not check_include(item, ignore_list):
            print("|      " * depth + "+--" + item)
            newitem = path + '/' + item
            if os.path.isdir(newitem):
                draw_project_tree_graph(newitem, depth + 1)

