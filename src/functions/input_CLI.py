# This file is part of the Planter extend project: DINC.
# This program is a free software tool, which does ensemble in-network machine learning.
# licensed under Apache-2.0
#
# Copyright (c) 2020-2021 Changgang Zheng
# Copyright (c) Computing Infrastructure Group, Department of Engineering Science, University of Oxford & Yale University
# E-mail: changgang.zheng@eng.ox.ac.uk (valid until July 2024),
# changgang.zheng@yale.edu (valid until October 2022) or changgangzheng@qq.com (no expiration date)
#
# Functions: This file contains the functions necessary to implement the Planter & DINC CLI.
#            Please refer to ./Docs/Planter_User_Document.pdf or further information.

import os
import copy
import numpy as np
from src.functions.directory_management import *

def CLI_loop(question, default, check_dir_existance, check_available_options, option_address, option_prefix, option_suffix):
    while True:
        if check_available_options:
            CLI_input = input('+ ' + question + ' (default = ' + str(default) + ' | options = -h) ') or default
        else:
            CLI_input = input('+ ' + question + ' (default = ' + str(default) + ') ') or default
        if check_dir_existance:
            if not check_available_options: 
                if not os.path.exists(CLI_input):
                    print('  Warning! The input does not exist, please input again.')
                else:
                    break
            else:
                input_dir = os.getcwd() + option_address + '/' + option_prefix + CLI_input + option_suffix
                if not os.path.exists(input_dir):
                    if CLI_input != "-h":
                        print('  Warning! The input: ' + CLI_input + ' does not available, please input again.')
                    find_folder_options(os.getcwd() + option_address)
                else:
                    break
        else:
            break
    return CLI_input


def take_CLI_input(DINC_config, config_type, config_name, question, default, manually_input = False, check_dir_existance = False, check_available_options = False, option_address = '', numeric = False, option_prefix= '', option_suffix = ''):
    if not manually_input:
        try:
            CLI_input = DINC_config[config_type][config_name]
            print('= Config type: \''+config_type+'\' config name: \''+config_name+'\' is auto filled with: ' + str(CLI_input))
        except Exception as e:
            try:
                _ = DINC_config[config_type]
            except Exception as e:
                DINC_config[config_type] = {}
            CLI_input = CLI_loop(question, default, check_dir_existance, check_available_options, option_address, option_prefix, option_suffix)
    else:
        try:
            _ = DINC_config[config_type]
        except Exception as e:
            DINC_config[config_type] = {}
        CLI_input = CLI_loop(question, default, check_dir_existance, check_available_options, option_address, option_prefix, option_suffix)
    if numeric:
        CLI_input = int(CLI_input)
    DINC_config[config_type][config_name] = CLI_input
    return DINC_config


def try_convert_str_input_to_int(input):
    if input.isdigit():
        return copy.deepcopy(int(input))
    return copy.deepcopy(input)

def str_to_array(input, margine = 1, marker = ','):
    if type(input) == str:
        if margine != 0:
            input = input[margine:-margine].split(marker)
        else:
            input = input.split(marker)
        for i, content in enumerate(input):
            input[i] = content.lstrip().rstrip()
            if input[i].isdigit():
                input[i] = int(input[i])
    return copy.deepcopy(input)
