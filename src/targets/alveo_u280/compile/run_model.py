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
    model_test_root = Planter_config['directory config']['work']+'/src/targets/alveo_u280/compile/model_test'
    file_name = Planter_config['model config']['model'] + '_' + Planter_config['target config']['use case'] + '_' + \
                Planter_config['data config']['dataset']
    test_file_name = 'test_switch_model_' + Planter_config['target config']['device'] + '_' +  Planter_config['target config']['type']
    return work_root, model_test_root, file_name, test_file_name


def add_make_run_model(fname, config):
    work_root, model_test_root, file_name, test_file_name = file_names(config)
    password = config['test config']['sudo password']
    test_command = 'python3 '+work_root+'/src/test/' + test_file_name + '.py'
    with open(fname, 'w') as command:
        command.write("#!/bin/bash\n")
        command.write("echo '" + password + "' | sudo -S " + test_command + "\n")
    os.chmod(fname, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

def run_command(command, root):
    sub.run(command, cwd=root, shell=True)

def add_make_esnet_hw_build(fname, config):
    # should be run within model_test_root: /hardware/model_test
    work_root, model_test_root, file_name, test_file_name = file_names(config)
    with open(fname, 'w') as command:
        command.write("#!/bin/bash\n")
        command.write("rm -r .app\n")
        command.write("rm -r artifacts\n")
        command.write("mkdir artifacts\n")
        command.write("cp " + work_root+"/P4/"+file_name+".p4 " + model_test_root+"/p4/esnet-smartnic.p4\n")
        command.write("git submodule deinit -f .\n")
        command.write("git submodule update --init --recursive\n")
        command.write("sed -i 's/Vivado Implementation Defaults/Performance_Explore/g' ./esnet-smartnic-hw/open-nic-shell/script/build.tcl\n")
        command.write("make > make_run_output.txt\n") 
        command.write("cp artifacts/model_test/artifacts.au280.model_test.0.zip esnet-smartnic-fw/sn-hw/\n")
    os.chmod(fname, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

def add_esnet_env_files(config):
    work_root, model_test_root, file_name, test_file_name = file_names(config)
    env_file_name_base = model_test_root+"/esnet-smartnic-fw/.env"
    os_codename = config['test config']['os codename']
    fpga_pcie_dev_name = config['test config']['fpga pcie dev']
    with open(env_file_name_base, 'w') as env:
        env.write("SN_HW_APP_NAME = model_test\n")
        env.write("SN_HW_BOARD = au280\n")
        env.write("SN_HW_VER = 0\n")
        env.write("SN_FW_VER=${USER}.001\n")
        env.write("OS_CODENAME=" + os_codename + "\n")
    env_file_name_sn_stack = model_test_root+"/esnet-smartnic-fw/sn-stack/.env"
    with open(env_file_name_sn_stack, 'w') as env:
        env.write("COMPOSE_PROJECT_NAME=sn-stack-${USER}\n")
        env.write("FPGA_PCIE_DEV=" + fpga_pcie_dev_name + "\n")
          
def add_make_esnet_load_to_hw(fname, config):
    # should be run within model_test/esnet-smartnic-fw
    work_root, model_test_root, file_name, test_file_name = file_names(config)
    with open(fname, 'w') as command:
        command.write("#!/bin/bash\n")
        command.write("docker compose build --no-cache\n")
        command.write("docker compose run --rm sn-fw-pkg\n")
    os.chmod(fname, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

def add_setup_fpga(fname, config):
    # this should be run within model_test/esnet-smartnic-fw/sn-stack
    work_root, model_test_root, file_name, test_file_name = file_names(config)
    with open(fname, 'w') as command:
        command.write("#!/bin/bash\n")
        command.write("docker compose down -v\n")
        command.write("docker compose build --no-cache\n")
        command.write("docker compose up -d --wait\n")
        # command.write("docker compose exec smartnic-fw sn-cli sw in-port-rename cmac0:cmac0 cmac1:cmac1 host0:host0 host1:host1\n")
        # command.write("docker compose exec smartnic-fw sn-cli sw in-port-connect cmac0:app0 cmac1:app0 host0:bypass host1:bypass\n")
        # command.write("docker compose exec smartnic-fw sn-cli sw app0-port-redirect cmac0:cmac0 cmac1:cmac1 host0:host0 host1:host1\n")
        command.write("sleep 30\n")
        command.write("docker compose cp " + work_root + "/src/targets/alveo_u280/hardware/s1-commands.txt smartnic-fw:/s1-commands.txt\n")
        command.write("docker compose exec smartnic-fw sn-p4-cli p4bm-apply s1-commands.txt\n")
    os.chmod(fname, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            

def term(sig_num, addition):
    print('Killing pid %s with group id %s' % (os.getpid(), os.getpgrp()))
    os.killpg(os.getpgid(os.getpid()), signal.SIGKILL)


def main(if_using_subprocess):
    # =================== set directory config ===================
    # reload the config file
    config_file = 'src/configs/Planter_config.json'
    Planter_config = json.load(open(config_file, 'r'))

    Planter_config['test config']['port'] = input("- Send packets to which port? (default = 'mel0'): ") or 'mel0'
    Planter_config['test config']['sudo password'] = getpass.getpass(
        "- Please input your password for 'sudo' command: ") or '12345'
    Planter_config['test config']['os codename'] = input("- Please enter OS codename (default = 'focal'): ") or 'focal'
    Planter_config['test config']['fpga pcie dev'] = input("- Please enter address of PCIe device that application stack should bind again (default = '0000:c1:00'): ") or '0000:c1:00'

    json.dump(Planter_config, open('src/configs/Planter_config.json', 'w'), indent=4, cls=NpEncoder)

    ##################################################
    work_root, model_test_root, file_name, test_file_name= file_names(Planter_config)
    # =================== compile the generated model ===================
    make_run_model_command = Planter_config['directory config']['work'] + '/src/scripts/make_run_model.sh'
    add_make_run_model(make_run_model_command, Planter_config)

    make_esnet_hw_command = Planter_config['directory config']['work'] + '/src/scripts/make_esnet_hw.sh'
    add_make_esnet_hw_build(make_esnet_hw_command, Planter_config)

    make_esnet_load_to_hw_command = Planter_config['directory config']['work'] + '/src/scripts/load_esnet_to_hw.sh'
    add_make_esnet_load_to_hw(make_esnet_load_to_hw_command, Planter_config)

    setup_fpga_command = Planter_config['directory config']['work'] + '/src/scripts/setup_fpga.sh'
    add_setup_fpga(setup_fpga_command, Planter_config)

    run_command(make_esnet_hw_command, model_test_root)

    add_esnet_env_files(Planter_config)

    esnet_load_to_hw_cwd = model_test_root + '/esnet-smartnic-fw'
    run_command(make_esnet_load_to_hw_command, esnet_load_to_hw_cwd) 
    
    setup_fpga_cwd = model_test_root + '/esnet-smartnic-fw/sn-stack'
    run_command(setup_fpga_command, setup_fpga_cwd)

    # =================== commands in sub process ===================
    # find the current pid
    #signal.signal(signal.SIGTERM, term)
    print('current pid is %s' % os.getpid())
    # create the process list
    processes = []

    if_using_subprocess = False

    return processes, if_using_subprocess

