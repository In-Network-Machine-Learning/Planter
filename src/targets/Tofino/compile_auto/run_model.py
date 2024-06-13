# THIS FILE IS PART OF Planter PROJECT
# Planter.py - The core part of the Planter library
#
# THIS PROGRAM IS FREE SOFTWARE TOOL, WHICH MAPS MACHINE LEARNING ALGORITHMS TO DATA PLANE, IS LICENSED UNDER Apache-2.0
# YOU SHOULD HAVE RECEIVED A COPY OF THE LICENSE, IF NOT, PLEASE CONTACT THE FOLLOWING E-MAIL ADDRESSES
#
# Copyright (c) 2020-2021 Changgang Zheng
# Copyright (c) Computing Infrastructure Lab, Department of Engineering Science, University of Oxford
# E-mail: changgang.zheng@eng.ox.ac.uk or changgangzheng@qq.com
#
# Functions: This file is a P4 compiler and runner of the P4 target.
#            Please refer to ./Docs/Planter_User_Document.pdf or further information.

import os
import sys
import time
import stat
import subprocess as sub
import json
import time
import signal
import platform
import threading
from multiprocessing import *
import getpass
from src.functions.json_encoder import *
from src.functions.add_license import *
from src.functions.extract_log_file_info import *
from src.functions.directory_management import *
from src.functions.config_modification import *
from src.functions.input_CLI import *



def file_names(Planter_config):
    tools_root = Planter_config['directory config']['tools']
    work_root = Planter_config['directory config']['work']
    sde_root = Planter_config['directory config']['sde']
    file_name = Planter_config['model config']['model'] + '_' + Planter_config['target config']['use case'] + '_' +  Planter_config['data config']['dataset']
    p4_file = Planter_config['directory config']['work'] + '/P4/' + file_name + '.p4'
    return work_root, sde_root, tools_root, p4_file, file_name

def add_compile_model(fname, config):
    work_root, sde_root, tools_root, p4_file, file_name = file_names(config)
    password = config['test config']['sudo password']
    
    with open(fname, 'w') as command:
        command.write("#!/bin/bash\n"
                      "The call to the Intel compiler is subject to the confidentiality agreement. Releasing "
                      "these lines of code is pending approval. Please enter the codes related to the call to the "
                      "compiler and runtime here. For more information, please e-mail: changgang.zheng@eng.ox.ac.uk")

        p4_test_file = 'n'

    os.chmod(fname, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    return p4_test_file

def add_start_switch_model(fname, config):
    work_root, sde_root, tools_root, p4_file, file_name = file_names(config)
    
    password = config['test config']['sudo password']
    
    with open(fname, 'w') as command:
        command.write("#!/bin/bash\n"
                      "The call to the Intel compiler is subject to the confidentiality agreement. Releasing "
                      "these lines of code is pending approval. Please enter the codes related to the call to the "
                      "compiler and runtime here. For more information, please e-mail: changgang.zheng@eng.ox.ac.uk")
    os.chmod(fname, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)


def add_start_driver(fname, config):
    work_root, sde_root, tools_root, p4_file, file_name = file_names(config)
    with open(fname, 'w') as command:
        command.write("#!/bin/bash\n"
                      "The call to the Intel compiler is subject to the confidentiality agreement. Releasing "
                      "these lines of code is pending approval. Please enter the codes related to the call to the "
                      "compiler and runtime here. For more information, please e-mail: changgang.zheng@eng.ox.ac.uk")
    os.chmod(fname, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

def add_load_table(fname, config):
    work_root, sde_root, tools_root, p4_file, file_name = file_names(config)
    with open(fname, 'w') as command:
        command.write("#!/bin/bash\n"
                      "The call to the Intel compiler is subject to the confidentiality agreement. Releasing "
                      "these lines of code is pending approval. Please enter the codes related to the call to the "
                      "compiler and runtime here. For more information, please e-mail: changgang.zheng@eng.ox.ac.uk")
    os.chmod(fname, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

def print_output(file_name, print_len):
    print_len+=1
    current_len = 0
    while True:
        count = 0
        for index, line in enumerate(open(file_name, 'r')):
            count += 1
        if count<=print_len or current_len<print_len:

            file = open(file_name, "r")  # Set file object
            for i in range(count):
                if i>current_len and i<print_len:
                    print(file.readline().strip())
            current_len = count
        else:
            break

def run_command(command, sde_root):
    sub.run(command, cwd=sde_root)

def wait_until_flag(file_name,flag):
    continuous_program = False
    while True:
        time.sleep(1)
        with open(file_name, 'r') as file:
            for line in file.readlines():
                if flag in line:
                    continuous_program = True
                    break
        time.sleep(0.5)
        if continuous_program:
            break

def term(sig_num, addition):
    print('Killing pid %s with group id %s' % (os.getpid(), os.getpgrp()))
    os.killpg(os.getpgid(os.getpid()), signal.SIGKILL)


def main(if_using_subprocess):
    if platform.system() != 'Linux':
        print('Your system is not Linux, bf-sde can not run on your os.')
        exit()
    # =================== set directory config ===================
    # reload the config file
    Planter_config = reload_config('src/configs/Planter_config.json')

    # =================== set if use sde-tools config or not in config ===================
    question = 'Have you write bf-sde and tool directory into a json file?'
    default = 'y'
    Planter_config = take_CLI_input(Planter_config, 'directory config', 'sde-tools existance', question, default)
    have_dir_config = Planter_config['directory config']['sde-tools existance']
    if have_dir_config == 'y':

        # ====================== set directory json file in config ======================
        question = 'What is the name of the directory json file?'
        default = 'Directory_config.json'
        Planter_config = take_CLI_input(Planter_config, 'directory config', 'sde-tools config file name', question, default,
                                        check_dir_existance=True, check_available_options=True, option_address='/src/configs/')
        dir_file = Planter_config['directory config']['sde-tools config file name']
        dir_config = json.load(open('src/configs/'+dir_file, 'r'))
        Planter_config['directory config']['sde'] = dir_config['sde']
        print('- bf-sde directory: '+Planter_config['directory config']['sde'])
        Planter_config['directory config']['tools'] = dir_config['tools']
        print('- bf-tools directory: ' + Planter_config['directory config']['tools'])
    else:
        # ====================== set sde directory in config ======================
        question = 'Where is your sde folder?'
        default = os.path.expanduser('~') + '/mysde/bf-sde-9.2.0'
        Planter_config = take_CLI_input(Planter_config, 'directory config', 'sde', question, default, check_dir_existance=True)

        # ====================== set tools directory in config ======================
        question = 'Where is your tools folder?'
        default = os.path.expanduser('~') + '/mysde/tools'
        Planter_config = take_CLI_input(Planter_config, 'directory config', 'tools', question, default, check_dir_existance=True)
    print("The call to the Intel compiler is subject to the confidentiality agreement. Releasing these lines of "
          "code is pending approval. Please enter the codes related to the call to the compiler and runtime here. "
          "For more information, please e-mail: changgang.zheng@eng.ox.ac.uk")
    exit()

    if 'baseline model' not in Planter_config['test config'].keys():
        while True:
            Planter_config['test config']['baseline model']  = input( '- Which is the name of the baseline model? (default = switch_tofino_x3 | options = -h | disable = None) ') or 'switch_tofino_x3'
            baseline_log_file = Planter_config['directory config']['sde'] + '/XXX.json'
            # The call to the Intel compiler is subject to the confidentiality agreement. Releasing these lines of
            # code is pending approval. Please enter the codes related to the call to the compiler and runtime here.
            # For more information, please e-mail: changgang.zheng@eng.ox.ac.uk")
            if not os.path.exists(baseline_log_file):
                if Planter_config['test config']['baseline model'] != "-h":
                    if Planter_config['test config']['baseline model'] == "None":
                        break
                    else:
                        print('  Warning! The baseline model does not exits, please input again.')
                find_folder_options(Planter_config['directory config']['sde']+'/build/p4-build/tofino')
            else:
                break

    # Input the config for testing
    # ====================== set machine learning model in config ======================
    question = 'Send packets to which port?'
    default = 'veth7'
    Planter_config = take_CLI_input(Planter_config, 'test config', 'port', question, default)
 
    

    # ====================== set machine learning model in config ======================
    if 'sudo password' not in Planter_config['test config'].keys():
        Planter_config['test config']['sudo password'] = getpass.getpass( "- Please input your password for 'sudo' command: ") or '12345'

    # dump the config file
    dump_config(Planter_config, 'src/configs/Planter_config.json')

    ##################################################
    work_root, sde_root, tools_root, p4_file, file_name = file_names(Planter_config)
    # =================== compile the generated model ===================
    compile_model_command = Planter_config['directory config']['work'] + '/src/scripts/compile_model.sh'
    p4_test_file = add_compile_model(compile_model_command, Planter_config)
    # =================== compile model timer ===================
    Planter_config['timer log']['compile model'] = {}
    Planter_config['timer log']['compile model']['start'] = time.time()
    # =================== compile model timer ===================
    result = sub.run(compile_model_command, cwd=sde_root)
    # =================== compile model timer ===================
    Planter_config['timer log']['compile model']['end'] = time.time()
    # =================== compile model timer ===================
    if not result.returncode == 0:
        print("The generated p4 file has errors, please check commen and separate p4 generators!")
        exit()
    if p4_test_file == 'y':
        exit()

    
    target_log_file = './src/logs/p4_performance/' + file_name + '.json'
    if Planter_config['test config']['baseline model'] != "None":
        compare_to_baseline(target_log_file, baseline_log_file)
    else:
        absolute_result(target_log_file)
    # The call to the Intel compiler is subject to the confidentiality agreement. Releasing these lines of
    # code is pending approval. Please enter the codes related to the call to the compiler and runtime here.
    # For more information, please e-mail: changgang.zheng@eng.ox.ac.uk")
    

    # =================== commands in sub process ===================
    # find the current pid
    signal.signal(signal.SIGTERM, term)
    print('current pid is %s' % os.getpid())
    # create the process list
    processes = []
    # =================== start the generated model ===================
    start_switch_model_command = Planter_config['directory config']['work'] + '/src/scripts/start_switch_model.sh'
    add_start_switch_model(start_switch_model_command, Planter_config)
    task0_start_switch_model = Process(target=run_command, args=(str(start_switch_model_command),str(sde_root),))
    task0_start_switch_model.daemon = True
    task0_start_switch_model.start()
    processes.append(task0_start_switch_model)
    # sleep
    sleep_time = 5
    print("Sleep before starting next subprocess. Current: start_switch_model_command ("+str(sleep_time)+"s) ...")
    time.sleep(sleep_time)
    # =================== start the driver ===================
    start_driver_command = Planter_config['directory config']['work'] + '/src/scripts/start_driver.sh'
    add_start_driver(start_driver_command, Planter_config)
    task1_start_driver = Process(target=run_command, args=(str(start_driver_command), str(sde_root),))
    task1_start_driver.daemon = True
    task1_start_driver.start()
    processes.append(task1_start_driver)
    # sleep
    flag = 'bfshell>'
    file_name = './src/temp/add_start_driver.txt'
    print("Sleep before starting next subprocess. Current: start_driver_command ...")
    wait_until_flag(file_name, flag)
    # =================== load the table ===================
    load_table_command = Planter_config['directory config']['work'] + '/src/scripts/load_table.sh'
    add_load_table(load_table_command, Planter_config)
    # =================== load table timer ===================
    Planter_config['timer log']['load table'] = {}
    Planter_config['timer log']['load table']['start'] = time.time()
    # =================== compile model timer ===================
    task2_load_table = Process(target=run_command, args=(str(load_table_command), str(sde_root),))
    task2_load_table.daemon = True
    task2_load_table.start()
    processes.append(task2_load_table)
    # =================== load table timer ===================
    Planter_config['timer log']['load table']['end'] = time.time()
    # =================== compile model timer ===================
    # dump the planter config
    dump_config(Planter_config, 'src/configs/Planter_config.json')
    # sleep
    flag = 'bfshell> exit'
    file_name = './src/temp/add_load_table.txt'
    print("Sleep before starting next subprocess. Current: load_table_command ...")
    wait_until_flag(file_name, flag)

    if_using_subprocess = True

    return processes, if_using_subprocess






