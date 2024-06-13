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
# Functions: This file prints the timer.
#            Please refer to ./Docs/Planter_User_Document.pdf or further information.

import os
import time
import sys
import json

def print_timer():
    try:
        # =================== print timers ===================
        # reload the config file
        config_file = 'src/configs/Planter_config.json'
        Planter_config = json.load(open(config_file, 'r'))
        for timer_name in Planter_config['timer log']:
            process_time = (Planter_config['timer log'][timer_name]['end'] - Planter_config['timer log'][timer_name]['start'])
            print("Process <" +timer_name +"> cost " +str(round(process_time,4)) +"s")
    except Exception as e:
        pass
