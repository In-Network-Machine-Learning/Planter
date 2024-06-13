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
    config['num_bits'] = Planter_config['p4 config']["action data bits"]
    config['f_tbl_len'] = Planter_config['p4 config']["feature tbl len"]
    config['num_axis'] = Planter_config['p4 config']["num components"]
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
        # headers.write("struct metadata_t {\n")

        for ax in range(0, config['num_axis']):
            # headers.write("    bit<" + str(config['num_bits']) + "> middle_ax" + str(ax) + ";\n")
            headers.write("    bit<32> middle_ax" + str(ax) + ";\n")


        # headers.write("}\n\n")




def separate_tables(fname, config):
    with open(fname, 'a') as ingress:
        for f in range(0, config['num_features']):
            ingress.write("    action extract_feature" + str(f)+'(')
            for ax in range(0, config['num_axis']):
                if ax==0:
                    ingress.write("bit<" + str(config['num_bits']) + "> f" + str(f) + "ax" + str(ax))
                else:
                    ingress.write(", bit<" + str(config['num_bits']) + "> f"+str(f)+"ax"+str(ax))
            ingress.write("){\n")

            if f==0:
                for ax in range(0, config['num_axis']):
                    ingress.write("        meta.middle_ax" + str(ax)+" = (bit<32>)f"+str(f)+"ax"+str(ax) +";\n")
            else:
                for ax in range(0, config['num_axis']):
                    ingress.write("        meta.middle_ax" + str(ax)+" = meta.middle_ax" + str(ax)+" + (bit<32>)f"+str(f)+"ax"+str(ax) +";\n")
            ingress.write("    }\n\n")



        for f in range(0, config['num_features']):
            ingress.write("    table lookup_feature" + str(f) + " {\n"
                     "        key = { hdr.Planter.feature" + str(f) + ":exact; }\n"
                     "        actions = {\n"
                     "            extract_feature" + str(f) + "();\n"
                     "            NoAction;\n"
                     "            }\n"
                     "        size = " + str( config['f_tbl_len'][f]) + ";\n"
                     "        default_action = NoAction;\n"
                     "    }\n\n")


        ingress.write("    action wrap_back( ){\n")
        for ax in range(0, config['num_axis']):
            ingress.write("        hdr.Planter.feature"+str(ax)+" = meta.middle_ax" + str(ax) + ";\n")
        ingress.write("    }\n\n")



def separate_logics(fname, config):
    with open(fname, 'a') as ingress:

        # ingress.write("        bias.apply();\n")
        for f in range(0, config['num_features']):
            ingress.write("        lookup_feature" + str(f) + ".apply();\n")

        ingress.write("        wrap_back();\n")
        # ingress.write("        /* Swap the MAC addresses */\n"
        #               "        bit<48> tmp;\n"
        #               "        tmp = hdr.ethernet.dstAddr;\n"
        #               "        hdr.ethernet.dstAddr = hdr.ethernet.srcAddr;\n"
        #               "        hdr.ethernet.srcAddr = tmp;\n"
        #               # "        send(3);\n")
        #               "        send(ig_intr_md.ingress_port);\n")



###################################################
# Create a tables load script
# input: table script file name, tables data json file name, configuration
# output: none
###################################################
def create_tables(Planter_config):
    Table_entries = []
    config_file = 'src/configs/Planter_config.json'
    Planter_config = json.load(open(config_file, 'r'))
    num_features = Planter_config['data config']['number of features']
    num_classes = Planter_config['model config']['number of classes']
    num_components = Planter_config['model config']['num components']
    Exact_Table = json.load(open('Tables/Exact_Table.json', 'r'))
    for f in range(num_features):
        for idx in Exact_Table['feature ' + str(f)]:
            key_value = int(idx)
            Entry = {}
            Entry["table"] = "SwitchIngress.lookup_feature" + str(f)
            Entry["match"] = {}
            Entry["match"]["hdr.Planter.feature" + str(f)] = key_value
            Entry["action_name"] = "SwitchIngress.extract_feature" + str(f)
            Entry["action_params"] = {}
            for ax in range(num_components):
                Entry["action_params"]["f" + str(f) + "ax" + str(ax)] = Exact_Table['feature ' + str(f)][idx]["ax" + str(ax)]
            Table_entries += [Entry]

    Runtime = {}
    Runtime["table_entries"] = Table_entries
    json.dump(Runtime, open('Tables/Runtime.json', 'w'), indent=4)
    # print('BMv2 runtime file is partly generated')



def create_tables_Commend(fname, config):
    num_features = config['data config']['number of features']
    num_classes = config['model config']['number of classes']
    num_components = config['model config']['num components']
    Exact_Table = json.load(open('Tables/Exact_Table.json', 'r'))
    with open(fname, 'w') as file:
        for f in range(num_features):
            for idx in Exact_Table['feature ' + str(f)]:
                key = int(idx)
                file.write("table_add SwitchIngress.lookup_feature" + str(f) + " extract_feature" + str(f) + " " + str(key) + " => " )
                for ax in range(num_components):
                    label = Exact_Table['feature ' + str(f)][idx][ "ax" + str(ax)]
                    file.write( str(label) + " ")
                file.write("\n")
            file.write("\n")


def create_load_tables(fname, fjson, config, Planter_config, file_name):
    work_root = Planter_config['directory config']['work']

    create_tables(Planter_config)

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

        for f in range(0, config['num_features']):
            tload.write("print('load feature " + str(f) + " table with',len(table['feature " + str(f) + "'].keys()),'entries')\n"
                        "for k in range(len(table['feature " + str(f) + "'].keys())):\n")
            tload.write("    key = str(k)\n")

            tload.write("    " + (config['debug_load_table'] * "# ") +
                        "Ingress.lookup_feature" + str(f) +
                        ".add_with_extract_feature" + str(f) +
                        "(int(key), ")
            for ax in range(0, config['num_axis']):
                if ax==0:
                    tload.write("table['feature " + str(f) + "'][key]['ax" + str(ax) + "']")
                else:
                    tload.write(", table['feature "+str(f)+"'][key]['ax"+str(ax)+"']")
            tload.write(")\n\n")

            if config['debug_load_table']:
                tload.write(
                    "    print('\\r{}th entry —— feature value: {} mask: {} priority: {} codes: {}'.format(key, table['feature " + str(f) +
                    "'][key][1],table['feature " + str(f) +
                    "'][key][0], int(key), int(codes,2)), end='')\n\n")

