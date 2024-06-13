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
# Functions: This file is a P4 tester of the P4 target.
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
import getpass
from multiprocessing import *
from src.functions.json_encoder import *
from src.functions.add_license import *


def main(sklearn_test_y, test_X, test_y, processes, if_using_subprocess):
    # reload the config file
    config_file = 'src/configs/Planter_config.json'
    Planter_config = json.load(open(config_file, 'r'))
    tools_root = Planter_config['directory config']['tools']
    work_root = Planter_config['directory config']['work']
    sde_root = Planter_config['directory config']['sde']


    return processes, if_using_subprocess

