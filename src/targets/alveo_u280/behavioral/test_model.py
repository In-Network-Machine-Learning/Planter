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


def file_names(Planter_config):
    work_root = Planter_config['directory config']['work']
    # this should be changed for consistency with run_model.py
    model_test_root = Planter_config['directory config']['work']+'/src/targets/alveo_u280/behavioral/test_environment/sim'
    file_name = Planter_config['model config']['model'] + '_' + Planter_config['target config']['use case'] + '_' + \
                Planter_config['data config']['dataset']
    test_file_name = 'test_switch_model_' + Planter_config['target config']['device'] + '_' +  Planter_config['target config']['type']
    return work_root, model_test_root, file_name, test_file_name


def run_command(command, root):
    sub.run(command, cwd = root)

def write_packets_in_pcap_classification(fname, Planter_config):
    work_root, model_test_root, file_name, test_file_name = file_names(Planter_config)
    num_features = Planter_config['data config']['number of features']
    send_port = Planter_config['test config']['port']

    with open(fname, 'w') as test:
        test.write("import json\n"
                   "import numpy as np\n"
                   "from scapy.all import *\n")

        test.write("class Planter(Packet):\n"
                   "    name = 'Planter'\n"
                   "    fields_desc = [StrFixedLenField('P', 'P', length=1),\n"
                   "        StrFixedLenField('Four', '4', length=1),\n"
                   "        XByteField('version', 0x01),\n"
                   "        XByteField('type', 0x01),\n")
        for f in range(num_features):
            test.write("        IntField('feature" + str(f) + "', 0),\n")
        test.write("        IntField('result', 0xDEADBABE)]\n\n")

        test.write("bind_layers(Ether, Planter, type=0x1234)\n\n")

        data_file = work_root + '/src/temp/Test_Data.json'
        test.write("config_file = '" + data_file + "'\n"
                                                   "Test_Data = json.load(open(config_file, 'r'))\n"
                                                   "sklearn_test_y = Test_Data['sklearn_test_y']\n"
                                                   "test_X = Test_Data['test_X']\n\n")

        test.write( 
            "packets_in = []\n\n"
            "for i in range(np.shape(test_X)[0]):\n"
            "    iface = '" + send_port + "'\n"
                                          "    pkt = Ether(dst='00:04:00:00:00:00', type=0x1234) / Planter( ")

        for f in range(num_features):
            test.write("feature" + str(f) + " = int(test_X[i][" + str(f) + "]), ")
        test.write("result  = int(404))\n")

        test.write("    pkt = pkt/' '\n\n"
                   "    packets_in.append(pkt)\n\n")

        test.write("wrpcap('" + model_test_root + "/test-case0/packets_in.pcap', packets_in)\n\n")

def write_common_test_classification(fname, Planter_config):
    work_root, model_test_root, file_name, test_file_name = file_names(Planter_config)
    num_features = Planter_config['data config']['number of features']
    send_port = Planter_config['test config']['port']

    with open(fname, 'a') as test:
        test.write("import json\n"
                   "import numpy as np\n"
                   "from scapy.all import *\n"
                   "from sklearn.metrics import *\n"
                   "from multiprocessing import *\n" 
                   "import readline\n"
                   "import time\n"
                   "import os\n"
                   "print('Predicted load table time ... ("+str(predicted_time)+"s)')\n"
                   "time.sleep("+str(predicted_time)+")\n")

        test.write("class Planter(Packet):\n"
                   "    name = 'Planter'\n"
                   "    fields_desc = [StrFixedLenField('P', 'P', length=1),\n"
                   "        StrFixedLenField('Four', '4', length=1),\n"
                   "        XByteField('version', 0x01),\n"
                   "        XByteField('type', 0x01),\n")
        for f in range(num_features):
            test.write("        IntField('feature" + str(f) + "', 0),\n")
        test.write("        IntField('result', 0xDEADBABE)]\n\n")

        test.write("bind_layers(Ether, Planter, type=0x1234)\n\n")

        data_file = work_root + '/src/temp/Test_Data.json'
        test.write("config_file = '" + data_file + "'\n"
                                                   "Test_Data = json.load(open(config_file, 'r'))\n"
                                                   "sklearn_test_y = Test_Data['sklearn_test_y']\n"
                                                   "test_X = Test_Data['test_X']\n"
                                                   "test_y = Test_Data['test_y']\n\n")

        
        test.write("def extract(pkt):\n"
                   "    if pkt:\n"
                   "        receive_info = pkt[Planter]\n"
                   "        if receive_info:\n"
                   "            return int(receive_info.result)\n"
                   "        else:\n"
                   "            print('\\rCannot find Planter header in the {}th packet |'.format(i), end='')\n"
                   "    else:\n"
                   "        print('\\rDid not receive response of the {}th packet |'.format(i), end='')\n\n")

        test.write(
            "print(\"\\n==============================================================================================\")\n"
            "print(\"=        Two steps to exit Planter: 1. input 'exit', press 'return'; 2. press ctrl + c       =\")\n"
            "print(\"==============================================================================================\")\n"
            "print('Test the switch model, the result should be the same as previous python test')\n"
            "same = 0\n"
            "correct = 0\n"
            "error = 0\n"
            "switch_test_y = []\n")

        test.write("packets_out_pcap_reader = PcapReader('" + model_test_root + "/test-case0/packets_out.pcap')\n\n")
        test.write("for i in range(np.shape(test_X)[0]):\n"
                   "    packet_out = packets_out_pcap_reader.next()\n"
                   "    received_result = extract(packet_out)\n\n"
                   
                   "    switch_prediction = received_result\n"
                   "    switch_test_y += [switch_prediction]\n\n"
                   "    if switch_prediction == test_y[i]:\n"
                   "        correct += 1\n"
                   "    if switch_prediction == sklearn_test_y[i]:\n"
                   "        same += 1\n"
                   "    else:\n"
                   "        error += 1\n"
                   "    print( '\\rSwitch model {}th prediction: {}, test_y: {}, with acc: {:.3}, with acc to sklearn:"
                   " {:.4}, with error: {:.4}, M/A format macro f1: {:.4}, macro f1: {:.4}'"
                   ".format(i+1, switch_prediction, test_y[i], correct / (i + 1), same / (i + 1),"
                   " error / (i + 1), accuracy_score(switch_test_y[:i+1], test_y[:i+1]), accuracy_s"
                   "core(sklearn_test_y[:i+1], test_y[:i+1])), end='')\n"
                   "result = classification_report(switch_test_y, test_y, digits=4)\n"
                   "print('\\n\\n', result)\n")
        test.write("print(\"======================================= Test Finished ========================================\")\n")





def simple_count(file_name):
    lines = 0
    for current_line in open(file_name):
        if 'register' in current_line:
            lines += 300
        lines += 1
    return lines




def generate_test_file(config_file):
    Planter_config = json.load(open(config_file, 'r'))

    file_name = 'test_switch_model_' + Planter_config['target config']['device'] + '_' + \
                Planter_config['target config']['type']

    packets_in_file_name = 'test_add_packets_switch_model_' + Planter_config['target config']['device'] + '_' + \
                Planter_config['target config']['type']
    add_packets_in_file = Planter_config['directory config']['work'] + '/src/test/' + packets_in_file_name + '.py'
    test_file = Planter_config['directory config']['work'] + '/src/test/' + file_name + '.py'

    ##################################################
    # predict time
    commands_file = Planter_config['directory config']['work'] + '/src/targets/alveo_u280/hardware/s1-commands.txt'
    lines = simple_count(commands_file)
    global predicted_time
    predicted_time = round(lines * 0.00015, 3)
    ##################################################
    print('Generating test files ...' )
    add_license(test_file)
    if Planter_config['test config']['type of test'] == 'dimension_reduction':
        write_common_test_dimension_reduction(test_file,Planter_config)
    elif Planter_config['test config']['type of test'] == 'classification':
        write_common_test_classification(test_file,Planter_config)
        write_packets_in_pcap_classification(add_packets_in_file, Planter_config)
    return test_file, add_packets_in_file

def main(sklearn_test_y, test_X, test_y, processes, if_using_subprocess):
    # reload the config file
    config_file = 'src/configs/Planter_config.json'
    Planter_config = json.load(open(config_file, 'r'))
    work_root, model_test_root, file_name, test_file_name = file_names(Planter_config)


    Test_Data = {}
    Test_Data['sklearn_test_y'] = sklearn_test_y
    Test_Data['test_X'] = test_X.values
    Test_Data['test_y'] = test_y

    json.dump(Test_Data, open(work_root + '/src/temp/Test_Data.json', 'w'), indent=4, cls=NpEncoder)

    # =================== generate test the switch file ===================
    test_file, add_packets_in_file = generate_test_file(config_file)

    # =================== test the switch model ===================
    
    test_model_command = work_root + '/src/scripts/add_packets_in.sh'
    run_command(test_model_command, model_test_root)

    make_run_model_command = work_root + '/src/scripts/make_run_model.sh'
    run_command(make_run_model_command, model_test_root)

    test_model_command = work_root + '/src/scripts/test_model.sh'
    task1_test_model = Process(target=run_command, args=(str(test_model_command), str(model_test_root),))
    task1_test_model.daemon = True
    task1_test_model.start()
    processes.append(task1_test_model)

    if not if_using_subprocess:
        if_using_subprocess = True

    return processes, if_using_subprocess


if __name__ == "__main__":
   _ = generate_test_file('/home/liam/Planter/src/configs/Planter_config.json')
