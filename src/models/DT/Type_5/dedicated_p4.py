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
# Functions: This file is a P4 generator of the ML model.
#            Please refer to ./Docs/Planter_User_Document.pdf or further information.

import numpy as np
import json
import math


def load_config(fname):
    Planter_config = json.load(open('src/configs/' + fname, 'r'))
    config_file = Planter_config['p4 config']
    config = {}
    config['num_features'] = config_file["number of features"]
    config['num_classes'] = config_file["number of classes"]
    config['column_width'] = config_file['width of feature']
    config['result_width'] = config_file['width of result']
    config['code_width'] = config_file['width of code']
    config['feature_width'] = config_file["width of feature"]
    config['feature_table_depth'] = config_file['used columns']
    config['code_tbl_depth'] = config_file['code table size']
    config['probability_width'] = config_file['width of probability']
    config['model'] = config_file['model']
    config['default_lable'] = config_file["default lable"]
    return config, Planter_config


def add_model_intro(fname, config):
    with open(fname, 'a') as intro:
        intro.write("/*\n"
                     " * Planter\n"
                     " *\n"
                     " * This program implements a simple protocol. It can be carried over Ethernet\n"
                     " * (Ethertype 0x1234).\n"
                     " *\n"
                     " * The Protocol header looks like this:\n"
                     " *\n"
                     " *        0                1                  2              3\n"
                     " * +----------------+----------------+----------------+---------------+\n"
                     " * |      P         |       4        |     Version    |     Type      |\n"
                     " * +----------------+----------------+----------------+---------------+\n")
        for f in range(config['num_features']):
            intro.write( " * |                              feature"+str(f)+"                            |\n"
                         " * +----------------+----------------+----------------+---------------+\n")
        intro.write( " * |                              Result                              |\n"
                     " * +----------------+----------------+----------------+---------------+\n"
                     " *\n"
                     " * P is an ASCII Letter 'P' (0x50)\n"
                     " * 4 is an ASCII Letter '4' (0x34)\n"
                     " * Version is currently 1 (0x01)\n"
                     " * Type is currently 1 (0x01)\n"
                     " *\n"
                     " * The device receives a packet, do the classification, fills in the\n"
                     " * result and sends the packet back out of the same port it came in on, while\n"
                     " * swapping the source and destination addresses.\n"
                     " *\n"
                     " * If an unknown operation is specified or the header is not valid, the packet\n"
                     " * is dropped\n"
                     " */\n\n")


def separate_metadata(fname, config):
    with open(fname, 'a') as headers:
        # write the metadata struct
        for i in range(0, config['num_features']):
            headers.write(
                "    bit<" + str(int(config['code_width'][i])) + "> code_f" + str(i) + ";\n")
        headers.write("    bit<" + str(config['probability_width']) + "> sum_prob" + ";\n")
        headers.write("    bit<32>  DstAddr;\n")
        headers.write("    bit<32> decision_key;\n")


def separate_logics(fname, config):
    with open(fname, 'a') as ingress:
        for i in range(0, config['num_features']):
            ingress.write("        lookup_feature" + str(i) + ".apply();\n")

        ingress.write("        meta.decision_key["+str(int(np.sum(config["code_width"])-1))+ ":0] = ")
        count_code = {}
        for j in range(0, config['num_features']):
            count_code[j] = 0
        for j in range(0, config['num_features']):
            if j!=config['num_features']-1:
                ingress.write("meta.code_f" + str(j) + "[" + str(int(count_code[j] + config['code_width'][j] - 1)) + ":" + str(int(count_code[j])) + "] ++ ")
            else:
                ingress.write(
                    "meta.code_f" + str(j) + "[" + str(int(count_code[j] + config['code_width'][j] - 1)) + ":" + str(int(count_code[j])) + "] ;\n")
        ingress.write("        decision.apply();\n")



def separate_tables(fname, config):
    with open(fname, 'a') as ingress:
        for i in range(0, config['num_features']):
            ingress.write("    action extract_feature" + str(i) + "(out bit<" + str(
                int(np.array(config['code_width'])[i])) + "> meta_code, bit<" + str(
                int(np.array(config['code_width'])[i])) + "> tree){\n" \
                                                                  "        meta_code = tree;\n" \
                                                                  "    }\n\n")

        ingress.write("    action read_lable(bit<32> label){\n" \
                      "        meta.result = label;\n" \
                      "    }\n\n")

        for i in range(0, config['num_features']):
            ingress.write("    @pragma stage 0\n")
            ingress.write("    table lookup_feature" + str(i) + " {\n" \
                     "        key = { meta.feature" + str(i) + ":lpm; }\n" \
                     "        actions = {\n" \
                     "            extract_feature" + str(i) + "(meta.code_f" + str(i) + ");\n" \
                     "            NoAction;\n" \
                     "            }\n" \
                     "        size = " + str( config['feature_table_depth'][i]) + ";\n" \
                     "        default_action = NoAction;\n" \
                     "    }\n\n")


        ingress.write("    action write_default_class() {\n"
                      "        meta.result = " + str(config['default_lable']) + ";\n"
                      "    }\n\n")

        count_code = {}
        for j in range(0, config['num_features']):
            count_code[j] = 0

        ingress.write("    table decision {\n"  
                      "        key = { ")
        ingress.write("meta.decision_key:lpm;\n ")
        ingress.write("}\n")
        ingress.write("        actions={\n"
                      "            read_lable;\n"
                      "            write_default_class;\n"
                      "        }\n")
        ingress.write("        size = " + str(config['code_tbl_depth']) + ";\n" 
                      "        default_action = write_default_class;\n"
                      "    }\n\n")

###################################################
# Create a tables load script
# input: table script file name, tables data json file name, configuration
# output: none
###################################################

def ten_to_bin(num,count):
    num = bin(num).lstrip('0b')

    if len(num) != count:
        cont = count - len(num)
        num = cont * '0' + num
    return num


def create_tables_Commend(fname, config):
    num_features = config['data config']['number of features']
    num_classes = config['model config']['number of classes']
    LPM_Table = json.load(open('Tables/LPM_Table.json', 'r'))
    with open(fname, 'w') as file:
        for f in range(num_features):
            for idx in LPM_Table['feature ' + str(f)]:
                priority = int(idx)
                key = LPM_Table['feature ' + str(f)][idx][1]
                mask = LPM_Table['feature ' + str(f)][idx][0]
                label = LPM_Table['feature ' + str(f)][idx][2]
                file.write("table_add SwitchIngress.lookup_feature" + str(f)+" extract_feature" + str(f)+
                           " "+str(((1<<8)-1)&(key>>24))+"."+str(((1<<8)-1)&(key>>16))+"."+str(((1<<8)-1)&(key>>8))+
                           "."+str(((1<<8)-1)&(key))+"/"+str(32- int(math.log(2**config['p4 config']["width of feature"][f] - mask,2)))+" => "+str(label)+" \n")

            file.write("\n")

        for idx in LPM_Table['code to vote']:
            key = LPM_Table['code to vote'][idx][1]
            mask = LPM_Table['code to vote'][idx][0]
            label = LPM_Table['code to vote'][idx][2]
            file.write("table_add SwitchIngress.decision read_lable " + str(((1 << 9) - 1) & (key >> 24)) + "." + str(
                ((1 << 9) - 1) & (key >> 16)) + "." + str(((1 << 9) - 1) & (key >> 8)) + "." + str(((1 << 9) - 1) & (key)) +
                "/"+str(32 - int(math.log(2 ** np.sum(config['p4 config']["width of code"]) - mask, 2))) + " => " + str( label) + " \n")








def create_load_tables(fname, fjson, config, Planter_config, file_name):
    work_root = Planter_config['directory config']['work']


    commend_file = work_root+"/src/targets/bmv2/software/model_test/test_environment/s1-commands.txt"
    create_tables_Commend(commend_file, Planter_config)

    commend_file = work_root + "/Tables/s1-commands.txt"
    create_tables_Commend(commend_file, Planter_config)

    config['debug_load_table'] = False
    with open(fname, 'a') as tload:
        tload.write("import json\n" \
                    "import os\n" \
                    "import binascii\n" \
                    "import sys\n" + \
                    "import math\n" + \
                    ((not config['debug_load_table']) * ("sys.path.append('" + work_root + "')\n" \
                    "os.chdir('" + work_root + "')\n")) + \
                    "print('working dir: ' + os.getcwd())\n" \
                    "table = json.load(open('./Tables/" + fjson + "','r'))\n" \
                    "Planter_config = json.load(open('./src/configs/Planter_config.json','r'))\n"\
                    "config = Planter_config['p4 config']\n\n")
        tload.write((config['debug_load_table']) * ('# ') + "Ingress = bfrt."+file_name+".pipe.SwitchIngress\n")
        tload.write((config['debug_load_table']) * ('# ') + "Ingress.clear()" + "\n\n")

        tload.write("def ten_to_bin(num, count):\n")
        tload.write("    num = bin(num).lstrip('0b')\n")
        tload.write("    if len(num) != count:\n")
        tload.write("        cont = count - len(num)\n")
        tload.write("        num = cont * '0' + num\n")
        tload.write("    return num\n\n")


        for i in range(0, config['num_features']):
            tload.write("print('load feature " + str(i) + " table with',len(table['feature " + str( i) + "'].keys()),'entries')\n" \
                        "for k in range(len(table['feature " + str( i) + "'].keys())):\n")
            tload.write("    key = str(k)\n")
            tload.write("    codes = ''\n")
            tload.write("    codes = ten_to_bin(int(table['feature " + str(i) + "'][key][2]), int(config['width of code'][" + str(i) + "])) + codes\n")
            tload.write("    " + (config['debug_load_table'] * "# ") + \
                        "Ingress.lookup_feature" + str(i) + \
                        ".add_with_extract_feature" + str(i) + \
                        "(table['feature " + str(i) + "'][key][1], int(32-math.log(2**config['width of feature'][" + str(i) + "]-table['feature " + str(i) + "'][key][0],2)), int(codes,2) )\n")
            if config['debug_load_table']:
                tload.write(
                    "    print('\\r{}th entry —— feature value: {} mask: {} priority: {} codes: {}'.format(key, table['feature " + str(
                        i) + \
                    "'][key][1],table['feature " + str(i) + \
                    "'][key][0], int(key), int(codes,2)), end='')\n\n")

        # Load tree tables
        tload.write("print('load tree (code/code to vote) table with',len(table['code to vote'].keys()),'entries')\n")
        tload.write("for key in table['code to vote']:\n")
        tload.write("    " + (config['debug_load_table'] * "# ") + \
                    "Ingress.decision.add_with_read_lable" + \
                    "(table['code to vote'][key][1], int(32 - int(math.log(2 ** config['total width of code'] - table['code to vote'][key][0], 2))), table['code to vote'][key][2])\n")

        tload.write((config['debug_load_table']) * ('# ') + "Ingress.dump()" + "\n\n")
