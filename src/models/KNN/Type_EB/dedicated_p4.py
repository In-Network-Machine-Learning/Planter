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


def load_config(fname):
    Planter_config = json.load(open('src/configs/' + fname, 'r'))
    config_file = Planter_config['p4 config']
    config = {}
    config['num_features'] = config_file["number of features"]
    config['num_classes'] = config_file["number of classes"]
    config['tbl_len'] = Planter_config['p4 config']["table length"]
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
        # headers.write("struct metadata_t {\n"
        #               "    bit<8> Place_holder;\n"
        #               "}\n\n")
        headers.write("    bit<8> Place_holder;\n" )




def separate_tables(fname, config):
    with open(fname, 'a') as ingress:

        ingress.write("    action extract_label(bit<16> label){\n"
                      "        hdr.Planter.result = (bit<32>) label;\n"
                      "    }\n\n")




        ingress.write("    table lookup_clustream {\n"
                 "        key = { hdr.Planter.feature0:ternary; }\n"
                 "        actions = {\n"
                 "            extract_label();\n"
                 "            NoAction;\n"
                 "            }\n"
                 "        size = " + str( config['tbl_len']) + ";\n"
                 "        default_action = NoAction;\n"
                 "    }\n\n")



def separate_logics(fname, config):
    with open(fname, 'a') as ingress:

        ingress.write("        lookup_clustream.apply();\n")






###################################################
# Create a tables load script
# input: table script file name, tables data json file name, configuration
# output: none
###################################################


def create_tables_Commend(fname, config):
    num_features = config['data config']['number of features']
    num_classes = config['model config']['number of classes']

    Ternary_Table = json.load(open('Tables/Ternary_Table.json', 'r'))
    with open(fname, 'w') as file:

        for idx in Ternary_Table:
            priority = int(idx)
            key = Ternary_Table[idx][1]
            mask = Ternary_Table[idx][0]
            label = Ternary_Table[idx][2]
            file.write("table_add SwitchIngress.lookup_clustream extract_label " +
                       str(key) + "&&&" + str(mask) + " => " + str(label) + " " + str(priority) + "\n")


def create_load_tables(fname, fjson, config, Planter_config, file_name):
    work_root = Planter_config['directory config']['work']

    commend_file = work_root + "/src/targets/bmv2/software/model_test/test_environment/s1-commands.txt"
    create_tables_Commend(commend_file, Planter_config)

    commend_file = work_root + "/Tables/s1-commands.txt"
    create_tables_Commend(commend_file, Planter_config)


    config['debug_load_table'] = False
    with open(fname, 'a') as tload:
        tload.write("import json\n"
                    "import os\n"
                    "import binascii\n"
                    "import sys\n" +
                    ((not config['debug_load_table']) * ("sys.path.append('" + work_root + "')\n"
                    "os.chdir('" + work_root + "')\n")) +
                    "print('working dir: ' + os.getcwd())\n"
                    "table = json.load(open('./Tables/" + fjson + "','r'))\n"
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



        tload.write("print('load clustream table with',len(table.keys()),'entries')\n"
                    "for idx in table:\n")
        tload.write("    key = table[idx][1]\n"
                    "    mask = table[idx][0]\n"
                    "    label = table[idx][2]\n")
        
        tload.write("    " + (config['debug_load_table'] * "# ") +
                    "Ingress.lookup_clustream.add_with_extract_label(key, mask, int(idx), label)\n"
                    "    print(idx)\n")









