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
    config['num_trees'] = config_file["number of trees"]
    config['num_classes'] = config_file["number of classes"]
    config['num_depth'] = config_file["number of depth"]
    config['model'] = config_file['model']
    config["decision_table_size"] = config_file["decision table size"]
    config['default label'] = config_file["default label"]
    config['first_entry'] = config_file["first entry info"]
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
                     " */\n\n"
                     "#define CLASS_NOT_SET 10\n\n")


def separate_metadata(fname, config):
    with open(fname, 'a') as headers:
        # write the metadata struct

        # headers.write("#define CLASS_NOT_SET 10\n\n")
        # headers.write("struct metadata_t {\n")
        for t in range(0, config['num_trees']):
            headers.write("    bit<16> tree_" + str(t+1) + "_vote;\n")
        headers.write("    bit<16> node_id;\n"
                      "    bit<16> prevFeature;\n"
                      "    bit<16> isTrue;\n"
                      "    bit<32>  DstAddr;\n")
                      # "}\n\n")

def separate_logics(fname, config):
    with open(fname, 'a') as ingress:
        for t in range(0, config['num_trees']):
            ingress.write("        meta.tree_" + str(t+1) + "_vote = CLASS_NOT_SET;\n")
        ingress.write("\n")
        for t in range(0, config['num_trees']):
            ingress.write("        meta.node_id = "+str(config['first_entry'][t][0])+";\n"
                          "        meta.prevFeature = "+str(config['first_entry'][t][1])+";\n"
                          "        meta.isTrue = "+str(config['first_entry'][t][2])+";\n")
            for d in range(0, config['num_depth']):
                ingress.write("        "+d*"  "+"level_"+str(t+1)+"_"+str(d+1)+".apply();\n")
                ingress.write("        "+d*"  "+"if (meta.tree_" + str(t+1) + "_vote == CLASS_NOT_SET) {\n")
            ingress.write("        " + config['num_depth'] * "  " + "level_"+str(t+1)+"_"+str(config['num_depth']+1)+".apply();\n")
            ingress.write("        " + (config['num_depth']) * "} " + "\n\n")

        ingress.write("        decision.apply();\n")


def separate_tables(fname, config):
    with open(fname, 'a') as ingress:

        ingress.write("    action CheckFeature(bit<16> node_id, bit<16> f_inout, bit<32> threshold) {\n"
                      "        bit<32> feature = 0;\n"
                      # "        bit<32> th = threshold ;\n"
                      "        bit<16> f = f_inout ;\n")
        for f in range(0, config['num_features']):
            ingress.write("        if (f == "+str(f)+") {\n"
                          "            feature = hdr.Planter.feature"+str(f)+";\n"
                          "        }\n")
        ingress.write("        bit<32> th = threshold - feature;\n"
                      # "        if (feature <= th){\n" # if (feature <= th){
                      "        if (th & 0b1"+31*"0"+"==0){\n" # if (feature <= th){
                      "            meta.isTrue = 1;\n"
                      "        }else{\n"
                      "            meta.isTrue = 0;\n"
                      "        }\n"
                      "        meta.prevFeature = f;\n"
                      "        meta.node_id = node_id;\n")

        ingress.write("    }\n\n")

        for t in range(0, config['num_trees']):
            ingress.write("    action SetClass" + str(t+1) + "(bit <16> node_id, bit <16> class ) {\n"
                          "        meta.tree_" + str(t+1) + "_vote = class;\n"
                          "        meta.node_id = node_id; // just for debugging otherwise not needed\n"
                          "    }\n")


        for t in range(0, config['num_trees']):
            for d in range(0, config['num_depth']+1):
                ingress.write("    table level_"+str(t+1)+"_"+str(d+1)+"{\n"
                              "        key = {\n"
                              "            meta.node_id: exact;\n"
                              "            meta.prevFeature: exact;\n"
                              "            meta.isTrue: exact;\n"
                              "        }\n"
                              "        actions = {\n"
                              "            NoAction;\n"
                              "            CheckFeature;\n"
                              "            SetClass"+str(t+1)+";\n"
                              "        }\n"
                              "        size = 1024;\n"
                              "    }\n\n")


        ingress.write("    action read_lable(bit<32> label){\n"  
                      "        hdr.Planter.result = label;\n"  
                      "    }\n\n")
        ingress.write("    action write_default_decision() {\n" 
                      "        hdr.Planter.result = " + str( config['default label']) + ";\n"
                      "    }\n\n")
        ingress.write("    table decision {\n        key = { ")
        for t in range(config['num_trees']):
            ingress.write("meta.tree_" + str(t+1) + "_vote:exact;\n                ")
        ingress.write("}\n")
        ingress.write("        actions={\n"
                      "            read_lable;\n"
                      "            write_default_decision;\n"
                      "        }\n")
        ingress.write("        size = " + str(config["decision_table_size"]) + ";\n" 
                      "        default_action = write_default_decision;\n"
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

def create_tables_command(fname, config):
    num_features = config['data config']['number of features']
    num_classes = config['model config']['number of classes']
    num_trees = config['model config']['number of trees']
    Table = json.load(open('Tables/Exact_Table.json', 'r'))

    fname_current = config['directory config']['work'] + '/Tables/Depth_Based_Table.txt'
    total_entries = 0
    with open(fname_current, 'a') as file:
        for idx in Table['decision']:
            file.write("table_add SwitchIngress.decision read_lable ")
            for t in range(num_trees):
                file.write(str(Table['decision'][idx]['t' + str(t) + ' vote']) + " ")
            file.write("=> " + str(Table['decision'][idx]['class']) + "\n")
            total_entries += 1

    with open(fname, 'w') as command:
        command.write('')
    current_file = open(fname_current, 'r')

    for line in current_file:
        new_file = open(fname, 'a')  # Use append mode here
        new_file.write(line)
        total_entries += 1
    print('Actual exact table entries:', total_entries, '...', end='')
    current_file.close()
    new_file.close()



def create_load_tables(fname, fjson, config, Planter_config, file_name):
    work_root = Planter_config['directory config']['work']

    commend_file = work_root + "/src/targets/bmv2/software/model_test/test_environment/s1-commands.txt"
    create_tables_command(commend_file, Planter_config)

    commend_file = work_root + "/Tables/s1-commands.txt"
    create_tables_command(commend_file, Planter_config)

    table = json.load(open('./Tables/Exact_Table.json', 'r'))

    config['debug_load_table'] = False

    with open(fname, 'a') as tload:
        tload.write("import json\n" \
                    "import os\n" \
                    "import binascii\n" \
                    "import sys\n" + \
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



        # Load decision tables
        tload.write("print('load vote to class (decision) table with',len(table['decision'].keys()),'entries')\n")
        tload.write("for key in table['decision']:\n")
        tload.write("    " + (config['debug_load_table'] * "# ") + \
                    "Ingress.decision.add_with_read_lable(")
        for t in range(config['num_trees']):
            tload.write("table['decision'][key]['t" + str(t) + " vote'], ")
        tload.write("table['decision'][key]['class'])\n")
        if config['debug_load_table']:
            tload.write("    print('\\r{}th entry ——")
            for t in range(config['num_trees']):
                tload.write(" tree" + str(f) + "_vote: {}")
            tload.write(" class: {}'.format(key, ")
            for t in range(config['num_trees']):
                tload.write("table['decision'][key]['t" + str(t) + " vote'], ")
            tload.write("table['decision'][key]['class']), end='')\n\n")

        # Load decision tables
        tload.write("print('load table for each nodes')\n")
        for idx in table['node table']:
            if table['node table'][idx][0] == "CheckFeature":
                key_and_values = table['node table'][idx][2] + ', ' + table['node table'][idx][3] + ', ' + \
                                 table['node table'][idx][4] + ', ' + table['node table'][idx][5] + ', ' + \
                                 table['node table'][idx][6] + ', ' + table['node table'][idx][7]
            else:
                key_and_values = table['node table'][idx][2] + ', ' + table['node table'][idx][3] + ', ' + \
                                 table['node table'][idx][4] + ', ' + table['node table'][idx][5] + ', ' + \
                                 table['node table'][idx][6]

            tload.write("Ingress."+table['node table'][idx][1]+".add_with_"+table['node table'][idx][0]+
                        '('+key_and_values+')\n')
