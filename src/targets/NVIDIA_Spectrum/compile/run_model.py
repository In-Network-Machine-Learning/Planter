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



def file_names(Planter_config):
    user_code_root = Planter_config['directory config']['work'] + '/src/targets/NVIDIA_Spectrum/compile/user_code'
    compiler_version = Planter_config['directory config']['compiler_version']
    work_root = Planter_config['directory config']['work']
    file_name = Planter_config['model config']['model'] + '_' + Planter_config['target config']['use case'] + '_' +  Planter_config['data config']['dataset']
    p4_file = Planter_config['directory config']['work'] + '/P4/' + file_name + '.p4'
    return work_root, user_code_root, compiler_version, p4_file, file_name

def add_compile_model(fname, config):
    work_root, user_code_root, compiler_version, p4_file, file_name = file_names(config)
    p4_test_file = input('- Test your manually written p4 file other than ' + file_name + '? (default = n | file name) ') or 'n'
    if p4_test_file != 'n':
        file_name = p4_test_file

    with open(fname, 'w') as command:
        command.write("#!/bin/bash\n")
        command.write("cp "+p4_file+" "+user_code_root+"/"+file_name+".p4\n")
        command.write("The call to the NVIDIA compiler is subject to the confidentiality agreement. Releasing "
                      "these lines of code is pending approval. Please enter the codes related to the call to the "
                      "compiler and runtime here. For more information, please e-mail: changgang.zheng@eng.ox.ac.uk")
    print("The call to the NVIDIA compiler is subject to the confidentiality agreement. Releasing these lines of "
          "code is pending approval. Please enter the codes related to the call to the compiler and runtime here. "
          "For more information, please e-mail: changgang.zheng@eng.ox.ac.uk")
    exit()
    os.chmod(fname, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    return p4_test_file






def term(sig_num, addition):
    print('Killing pid %s with group id %s' % (os.getpid(), os.getpgrp()))
    os.killpg(os.getpgid(os.getpid()), signal.SIGKILL)


def main(if_using_subprocess):
    # =================== set directory config ===================
    # reload the config file
    config_file = 'src/configs/Planter_config.json'
    Planter_config = json.load(open(config_file, 'r'))

    Planter_config['directory config']['compiler_version'] = input('- What is your compiler version? (default = \'1.0.18.2\')') or ('1.0.18.2')
    json.dump(Planter_config, open('src/configs/Planter_config.json', 'w'), indent=4, cls=NpEncoder)

    ##################################################
    work_root, user_code_root, compiler_version, p4_file, file_name = file_names(Planter_config)
    # =================== compile the generated model ===================
    compile_model_command = Planter_config['directory config']['work'] + '/src/scripts/compile_model.sh'
    p4_test_file = add_compile_model(compile_model_command, Planter_config)
    result = sub.run(compile_model_command, cwd=user_code_root)

    if not result.returncode == 0:
        print("The generated p4 file has errors, please check commen and separate p4 generators!")
        exit()
    print('Compiler output from file: '+user_code_root+"/"+file_name+"_out/compiler.log")
    print_log_file(user_code_root+"/"+file_name+"_out/compiler.log")
    if p4_test_file == 'n':
        exit()
    else:
        exit()

    # =================== commands in sub process ===================
    # find the current pid
    signal.signal(signal.SIGTERM, term)
    print('current pid is %s' % os.getpid())
    # create the process list
    processes = []

    if_using_subprocess = True

    return processes, if_using_subprocess






