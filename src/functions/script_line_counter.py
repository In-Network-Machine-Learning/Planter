# THIS FILE IS PART OF Planter PROJECT
# Planter.py - The core part of the Planter library
#
# THIS PROGRAM IS FREE SOFTWARE TOOL, WHICH MAPS MACHINE LEARNING ALGORITHMS TO DATA PLANE, IS LICENSED UNDER Apache-2.0
# YOU SHOULD HAVE RECEIVED A COPY OF WTFPL LICENSE, IF NOT, PLEASE CONTACT THE FOLLOWING E-MAIL ADDRESSES
#
# Copyright (c) 2020-2021 Changgang Zheng
# Copyright (c) Computing Infrastructure Group, Department of Engineering Science, University of Oxford
# E-mail: changgang.zheng@eng.ox.ac.uk or changgangzheng@qq.com
#
# Functions: This file counts the lines of codes.
#            Please refer to ./Docs/Planter_User_Document.pdf or further information.

# coding=utf-8
import os
import json
import sys
import signal

base_path = input('- Where is your project folder? (default = \''
                                            +os.path.abspath(os.path.join(os.getcwd(),".."))+'/Planter\')') or (
                                            os.path.abspath(os.path.join(os.getcwd(),".."))+'/Planter')


def collect_files(dir):
    filelist = []
    for parent,dirnames,filenames in os.walk(dir):
         for filename in filenames:
             if filename.endswith('.py'):
                 filelist.append(os.path.join(parent,filename))
    return filelist


def calc_linenum(file):
    with open(file) as fp:
        content_list = fp.readlines()
        code_num = 0
        blank_num = 0
        annotate_num =0
        for content in content_list:
            content = content.strip()
            if content == '':
                blank_num += 1
            elif content.startswith('#'):
                annotate_num += 1
            else:
                code_num += 1
    return code_num,blank_num,annotate_num

if __name__ == '__main__':
    files = collect_files(base_path)
    total_code_num = 0
    total_blank_num = 0
    total_annotate_num = 0
    for f in files:
        code_num, blank_num, annotate_num = calc_linenum(f)
        total_code_num += code_num
        total_blank_num += blank_num
        total_annotate_num += annotate_num
        print("File:", f)
        print("Lines of codes:", code_num)
        print("Lines of comments:", annotate_num)
        print("Lines of blanks", blank_num)
    print("\nIn total, the project has")
    print("Total lines of codes:", total_code_num)
    print("Total lines of comments:", total_annotate_num)
    print("Total lines of blanks", total_blank_num)
