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


def file_names(Planter_config):
    work_root = Planter_config['directory config']['work']
    model_test_root = Planter_config['directory config']['work'] + '/src/targets/' + Planter_config['target config'][
        'device'] + '/' + Planter_config['target config']['type'] + '/model_test/test_environment'
    # model_test_root = Planter_config['directory config']['work'] + '/src/targets/bmv2/software/model_test/test_environment'
    file_name = Planter_config['model config']['model'] + '_' + Planter_config['target config']['use case'] + '_' + \
                Planter_config['data config']['dataset']
    test_file_name = 'test_switch_model_' + Planter_config['target config']['device'] + '_' +  Planter_config['target config']['type']
    return work_root, model_test_root, file_name, test_file_name


def add_run_switch_model(fname, config):
    work_root, model_test_root, file_name, test_file_name = file_names(config)
    password = config['test config']['sudo password']
    test_command = 'h1 python3 '+work_root+'/src/test/' + test_file_name +'.py'
    
    with open(fname, 'w') as command:
        command.write("#!/bin/bash\n")
        command.write("echo '" + password + "' | sudo -S make clean\n")
        command.write("rm " + model_test_root + "/*.p4\n")
        command.write("cp "+work_root+"/P4/"+file_name+".p4 " + model_test_root + "/"+file_name+".p4\n")
        # command.write("echo '" + test_command + "' | sudo -S make run\n")
        command.write("sudo p4c --target bmv2 --arch v1model --std p4-16 " + model_test_root + "/"+file_name+".p4\n")# + ' > '+work_root+'/src/temp/p4c_compile.txt\n')
        command.write("sudo simple_switch -i 0@veth0 -i 1@veth1 " + model_test_root + "/"+file_name+".json\n")# + ' > '+work_root+'/src/temp/start_simple_switch_model.txt\n')
    os.chmod(fname, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

def add_load_table(fname, config):
    work_root, model_test_root, file_name, test_file_name = file_names(config)
    password = config['test config']['sudo password']
    
    with open(fname, 'w') as command:
        command.write("#!/bin/bash\n")
        # command.write("echo '" + password + "' | sudo -S make clean\n")
        # command.write("echo '" + password + "' | sudo -S simple_switch_CLI <"+work_root+"/Tables/s1-commands.txt " + model_test_root + "/"+file_name+".json" + ' > '+work_root+'/src/temp/simple_switch_CLI_load_table.txt\n')
        command.write("simple_switch_CLI <" + work_root + "/Tables/s1-commands.txt ")# + ' > ' + work_root + '/src/temp/simple_switch_CLI_load_table.txt\n')
    os.chmod(fname, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)


def term(sig_num, addition):
    print('Killing pid %s with group id %s' % (os.getpid(), os.getpgrp()))
    os.killpg(os.getpgid(os.getpid()), signal.SIGKILL)


def main(if_using_subprocess):
    if platform.system() != 'Linux':
        print('Your system is '+platform.system()+' but not linux, please make sure bmv2, p4c and mininet is installed on your os.')
        exit()
    # =================== set directory config ===================
    # reload the config file
    config_file = 'src/configs/Planter_config.json'
    Planter_config = json.load(open(config_file, 'r'))

    Planter_config['test config']['port'] = input("- Send packets to which port? (default = 'eth0'): ") or 'eth0'
    Planter_config['test config']['sudo password'] = getpass.getpass(
        "- Please input your password for 'sudo' command: ") or '12345'

    json.dump(Planter_config, open('src/configs/Planter_config.json', 'w'), indent=4, cls=NpEncoder)

    ##################################################
    work_root, model_test_root, file_name, test_file_name= file_names(Planter_config)
    # =================== compile command for the generated model ===================
    run_switch_model_command = Planter_config['directory config']['work'] + '/src/scripts/run_switch_model.sh'
    add_run_switch_model(run_switch_model_command, Planter_config)

    # =================== load table command for the generated model ===================
    load_table_command = Planter_config['directory config']['work'] + '/src/scripts/simple_switch_CLI_load_table.sh'
    add_load_table(load_table_command, Planter_config)

    

    # =================== commands in sub process ===================
    # find the current pid
    signal.signal(signal.SIGTERM, term)
    print('current pid is %s' % os.getpid())
    # create the process list
    processes = []

    if_using_subprocess = False

    return processes , if_using_subprocess






