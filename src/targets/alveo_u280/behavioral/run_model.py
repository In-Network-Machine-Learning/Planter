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
    model_test_root = Planter_config['directory config']['work']+'/src/targets/alveo_u280/behavioral/test_environment'
    file_name = Planter_config['model config']['model'] + '_' + Planter_config['target config']['use case'] + '_' + \
                Planter_config['data config']['dataset']
    test_file_name = 'test_switch_model_' + Planter_config['target config']['device'] + '_' +  Planter_config['target config']['type']

    packets_in_test_file_name = 'test_add_packets_switch_model_' + Planter_config['target config']['device'] + '_' +  Planter_config['target config']['type']
    return work_root, model_test_root, file_name, test_file_name, packets_in_test_file_name

def add_makefile_test_environment(fname, config):
    work_root, model_test_root, file_name, test_file_name, packets_in_test_file_name = file_names(config)
    with open(fname, 'w') as makefile:
        makefile.write("compile :\n")
        makefile.write("\tp4c-vitisnet " + file_name + ".p4 -o " + file_name + ".json")

def add_makefile_sim(fname, config):
    """used to generate Makefile that is called to run behavioural simulation
    based on esnet-smartnic-hw file, only modified with necessary filenames"""
    work_root, model_test_root, file_name, test_file_name, packets_in_test_file_name = file_names(config)
    with open(fname, 'w') as makefile:
            makefile.write(        
                "# ===========================================================================\n"
                "# ESnet smartnic P4 simulation\n"
                "# ===========================================================================\n\n"
                "# ---------------------------------------------------------------------------\n"
                "# Variables\n"
                "# ---------------------------------------------------------------------------\n"
                "# P4 source file. \n"
                "# Note that the build target creates a .json file (used by the P4 behavioral simulator)\n"
                "# in the same directory as the P4 source file, which may be different from the Makefile\n"
                "# directory.\n")
            makefile.write("P4_SOURCE = ../" + file_name + ".p4\n")
            makefile.write(
                "P4_OBJECT = $(P4_SOURCE:.p4=.json)\n\n"
                "# JSON object file as seen from $(P4BM_DIR)\n"
                "P4_OBJECT_TEST = ../$(P4_OBJECT)\n\n"
                "# Default testcase directory.  Assumes each test case is a subdir below the sim dir.\n"
                "P4BM_DIR = test-case0\n\n"
                "# Testcase directory list to use for p4bm simulation\n"
                "# P4BM_DIRS = test-case1 test-case2 test-case3\n"
                "P4BM_DIRS = test-case0\n\n"
                "# Files within each testcase directory, as seen from within $(P4BM_DIR)\n"
                "# Note that $(P4BM_OUTPUT_PCAP) and $(P4BM_OUTPUT_META) are\n"
                "# implicitly named in $(P4BM_SCRIPT).\n"
                "P4BM_SCRIPT         = runsim.txt\n"
                "P4BM_LOGFILE_PREFIX = $(P4BM_SCRIPT)\n"
                "P4BM_OUTPUT_PCAP    = packets_out.pcap\n"
                "P4BM_OUTPUT_META    = packets_out.meta\n"
                "P4BM_OUTPUTS        = $(P4BM_LOGFILE_PREFIX)_cli.txt $(P4BM_LOGFILE_PREFIX)_model.txt \\\n"
                "                      $(P4BM_OUTPUT_META) $(P4BM_OUTPUT_PCAP)\n\n"
                "# Executable pathnames (particularly if they're not in $PATH)\n"
                "P4C_VITISNET      = p4c-vitisnet\n"
                "RUN_P4BM_VITISNET = run-p4bm-vitisnet\n\n"
                "# ---------------------------------------------------------------------------\n"
                "# Targets\n"
                "# ---------------------------------------------------------------------------\n"
                "sim-all:\n"
                "\tfor d in $(P4BM_DIRS); do $(MAKE) P4BM_DIR=$$d sim || exit 1; done\n\n"
                "sim: build\n"
                "# Make sure that $(P4BM_DIR)/$(P4BM_SCRIPT) exists (avoids issues if script is missing).\n"
                "\t(cd $(P4BM_DIR) && wc $(P4BM_SCRIPT) > /dev/null)\n"
                "\t(cd $(P4BM_DIR) && $(RUN_P4BM_VITISNET) -l $(P4BM_LOGFILE_PREFIX) \\\n"
                "                                             -j $(P4_OBJECT_TEST) -s $(P4BM_SCRIPT) )\n"
                "build: $(P4_OBJECT)\n\n\n"
                "cleansim-all:\n"
                "\tfor d in $(P4BM_DIRS); do $(MAKE) P4BM_DIR=$$d cleansim; done\n\n"
                "cleansim:\n"
                "\tcd $(P4BM_DIR) && rm -f $(P4BM_OUTPUTS)\n\n"
                "clean: cleansim-all\n"
                "\trm -f $(P4_OBJECT)\n\n"
                "%.json: %.p4\n"
                "\t$(P4C_VITISNET) $< -o $@\n")

def add_test_model(fname, test_file, config):
    password = config['test config']['sudo password']
    work_root, model_test_root, file_name, test_file_name, packets_in_test_file_name = file_names(config)
    with open(fname, 'w') as command:
        command.write("#!/bin/bash\n")
        command.write("echo '"+password+"' | sudo -S python3 " + test_file + '\n')
    os.chmod(fname, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO) # check what this does 

def add_make_run_model(fname, config):
    work_root, model_test_root, file_name, test_file_name, packets_in_test_file_name = file_names(config)
    password = config['test config']['sudo password']
    with open(fname, 'w') as command:
        command.write("#!/bin/bash\n")
        command.write("make clean\n")
        command.write("cp " + work_root + "/P4/" + file_name + ".p4 ../" + file_name + ".p4\n")
        #command.write("export VitisNetP4_Option_VISIBLE=true\n")
        #command.write("source ~/.bashrc\n") # this may need to be changed later
        #xilinxd_license_file = input("- Please enter XILINXD_LICENSE_FILE (default = '2100@cegls1.physics.ox.ac.uk'): ") or '2100@cegls1.physics.ox.ac.uk'
        #command.write("export XILINXD_LICENSE_FILE=" + xilinxd_license_file + "\n")
        #command.write("source /tools/Xilinx/Vivado/2022.1/settings64.sh\n")
        #command.write("echo '" + password + "' | sudo -S sed -i s/vitis_net_p4_v1_0/vitis_net_p4_v1_1/g /tools/Xilinx/Vivado/2022.1/bin/unwrapped/lnx64.o/p4c-vitisnet.tcl\n")
        #command.write("source /home/liam/.bashrc\n")
        #command.write("printenv\n")
        command.write("make sim test-case0\n")
    os.chmod(fname, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO) # check what this does 


def term(sig_num, addition):
    print('Killing pid %s with group id %s' % (os.getpid(), os.getpgrp()))
    os.killpg(os.getpgid(os.getpid()), signal.SIGKILL)

def main(if_using_subprocess):
    config_file = 'src/configs/Planter_config.json'
    Planter_config = json.load(open(config_file, 'r'))

    Planter_config['test config']['port'] = input("- Send packets to which port? (default = 'eth0'): ") or 'eth0'
    Planter_config['test config']['sudo password'] = getpass.getpass(
        "- Please input your password for 'sudo' command: ") or '12345'

    json.dump(Planter_config, open('src/configs/Planter_config.json', 'w'), indent=4, cls=NpEncoder)

    work_root, model_test_root, file_name, test_file_name, packets_in_test_file_name = file_names(Planter_config)

    makefile_sim = model_test_root + '/sim/Makefile'
    add_makefile_sim(makefile_sim, Planter_config)

    makefile_test_environment = model_test_root + '/Makefile'
    add_makefile_test_environment(makefile_test_environment, Planter_config)
    
    test_model_command = work_root + '/src/scripts/add_packets_in.sh'
    test_file = work_root + '/src/test/' + packets_in_test_file_name + ".py"
    add_test_model(test_model_command, test_file, Planter_config)

    test_model_command = work_root + '/src/scripts/test_model.sh'
    test_file = work_root + '/src/test/' + test_file_name + ".py"
    add_test_model(test_model_command, test_file, Planter_config)

    make_run_model_command = work_root + '/src/scripts/make_run_model.sh'
    add_make_run_model(make_run_model_command, Planter_config)


    # =================== commands in sub process ===================
    # find the current pid
    signal.signal(signal.SIGTERM, term)
    print('current pid is %s' % os.getpid())
    # create the process list
    processes = []

    if_using_subprocess = False

    return processes , if_using_subprocess

