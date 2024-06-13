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
    config['column_width'] = config_file['width of feature']
    config['result_width'] = config_file['width of result']
    config['code_width'] = config_file['width of code']
    config['feature_table_depth'] = config_file['used columns']
    config['headers_list'] = config_file['standard headers']
    config['code_tbl_depth'] = config_file['code table size']
    config["decision_table_size"] = config_file["decision table size"]
    config['probability_width'] = config_file['width of probability']
    config['model'] = config_file['model']
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


def separate_metadata(fname, config, xsa_architecture=False):
    if xsa_architecture:
        return
    with open(fname, 'a') as headers:
        # write the metadata struct
        # headers.write("struct metadata_t {\n")
        for i in range(0, config['num_features']):
            headers.write(
                "    bit<" + str(int(sum(np.array(config['code_width'])[:, i]))) + "> code_f" + str(i) + ";\n")
        headers.write("    bit<" + str(config['probability_width']) + "> sum_prob" + ";\n")
        for t in range(config['num_trees']):
            headers.write("    bit<4> tree_" + str(t) + "_vote;\n")
        for t in range(config['num_trees']):
            headers.write("    bit<7> tree_" + str(t) + "_prob;\n")
        headers.write("    bit<32>  DstAddr;\n")
        # headers.write("}\n\n")

def separate_variables(fname, config):
    with open(fname, 'a') as processing:
        for i in range(0, config['num_features']):
            processing.write(
                "    bit<" + str(int(sum(np.array(config['code_width'])[:, i]))) + "> code_f" + str(i) + ";\n")
        processing.write("    bit<" + str(config['probability_width']) + "> sum_prob" + ";\n")
        for t in range(config['num_trees']):
            processing.write("    bit<4> tree_" + str(t) + "_vote;\n")
        for t in range(config['num_trees']):
            processing.write("    bit<7> tree_" + str(t) + "_prob;\n")
        processing.write("    bit<32>  DstAddr;\n")

def separate_logics(fname, config):
    # this should only be called for xsa architecture
    with open(fname, 'a') as ingress:
        for i in range(0, config['num_features']):
            ingress.write("        lookup_feature" + str(i) + ".apply();\n")
        for i in range(config['num_trees']):
            ingress.write("        lookup_leaf_id" + str(i) + ".apply();\n")
        ingress.write("        decision.apply();\n")


def separate_tables(fname, config, xsa_architecture=False):
    if xsa_architecture:
        min_code_width=10
    else:
        min_code_width=0

    with open(fname, 'a') as ingress:
        # writing features: all features should be 32 bits, so this should be okay without minimum code width
        for i in range(0, config['num_features']):
            ingress.write("    action extract_feature" + str(i) + "(out bit<" + str(
                int(sum(np.array(config['code_width'])[:, i]))) + "> meta_code, bit<" + str(
                int(sum(np.array(config['code_width'])[:, i]))) + "> tree){\n" \
                                                                  "        meta_code = tree;\n" \
                                                                  "    }\n\n")

        ingress.write("    action read_lable(bit<32> label){\n")
        if xsa_architecture:
            ingress.write("        hdr.Planter.result = label;\n")
        else:
            ingress.write("        meta.result = label;\n")
        ingress.write("    }\n\n")

        for i in range(0, config['num_features']):
            ingress.write("    table lookup_feature" + str(i) + " {\n")
            if xsa_architecture:
                ingress.write("        key = { hdr.Planter.feature" + str(i) + ":exact;}\n")
            else:
                ingress.write("        key = { meta.feature" + str(i) + ":exact; }\n")
            ingress.write( "        actions = {\n")
            if xsa_architecture:
                ingress.write("            extract_feature" + str(i) + "(code_f" + str(i) + ");\n")
            else:
                ingress.write("            extract_feature" + str(i) + "(meta.code_f" + str(i) + ");\n")
            ingress.write("            NoAction;\n" \
                     "            }\n" \
                     "        size = " + str( config['feature_table_depth'][i]) + ";\n" \
                     "        default_action = NoAction;\n" \
                     "    }\n\n")
  
        for i in range(config['num_trees']):
            ingress.write("\n    action read_prob" + str(i) + "(")
            ingress.write("bit<" + str(config['probability_width']) + "> prob, bit<4> vote){\n")
            if xsa_architecture:
                ingress.write("        tree_" + str(i) + "_prob" + " = prob;\n" \
                             "        tree_" + str(i) + "_vote" + " = vote;\n" )
            else:
                ingress.write("        meta.tree_" + str(i) + "_prob" + " = prob;\n" \
                             "        meta.tree_" + str(i) + "_vote" + " = vote;\n" )
            ingress.write("    }\n")

        count_code = {}
        for j in range(0, config['num_features']):
            count_code[j] = 0
        for i in range(config['num_trees']):
            ingress.write("    table lookup_leaf_id" + str(i) + " {\n" \
                          "        key = { ")
            for j in range(0, config['num_features']):
                if xsa_architecture:
                    key_len = 1 + int(count_code[j] + config['code_width'][i][j] - 1) - int(count_code[j])
                    ingress.write("(bit<" + str(max(key_len, min_code_width)) + ">) code_f" + str(j) + "[" + str(int(count_code[j] + config['code_width'][i][j] - 1)) + ":" + str(int(count_code[j])) + "]:exact @name(\"lookup" +  "_leaf_id" + str(i) + "\");\n                ")
                else:
                    ingress.write(
                        "meta.code_f" + str(j) + "[" + str(int(count_code[j] + config['code_width'][i][j] - 1)) + ":" + str(int(count_code[j])) + "]:exact;\n                ")
                count_code[j] += config['code_width'][i][j]
            ingress.write("}\n")
            ingress.write("        actions={read_prob" + str(i) + ";}\n")
            ingress.write("        size = " + str(config['code_tbl_depth'][i]) + ";\n" \
                          "    }\n\n")
        ingress.write("    table decision {\n        key = { ")
        for t in range(config['num_trees']):
            if xsa_architecture:
                ingress.write("tree_" + str(t) + "_vote:exact;\n                ")
            else:
                ingress.write("meta.tree_" + str(t) + "_vote:exact;\n                ")
        ingress.write("}\n")
        ingress.write("        actions={read_lable;}\n")
        ingress.write("        size = " + str(config["decision_table_size"]) + ";\n" \
                      "    }\n\n")
###################################################
# Create a tables load script
# input: table script file name, tables data json file name, configuration
# output: none
###################################################
def ten_to_bin(num, count):
    num = bin(num).lstrip('0b')
    if len(num) != count:
        cont = count - len(num)
        num = cont * '0' + num
    return num

def create_tables(Planter_config):
    Table_entries = []
    config_file = 'src/configs/Planter_config.json'
    Planter_config = json.load(open(config_file, 'r'))
    num_features = Planter_config['data config']['number of features']
    num_classes = Planter_config['model config']['number of classes']
    num_trees = Planter_config['model config']['number of trees']
    Exact_Table = json.load(open('Tables/Exact_Table.json', 'r'))
    for f in range(num_features):
        for idx in Exact_Table['feature ' + str(f)]:
            key_value = int(idx)
            Entry = {}
            Entry["table"] = "SwitchIngress.lookup_feature"+str(f)
            Entry["match"] = {}
            Entry["match"]["meta.feature"+str(f)] = key_value
            Entry["action_name"] = "SwitchIngress.extract_feature"+str(f)
            Entry["action_params"] = {}
            codes = ''
            for t in range(num_trees):
                c_tree = Exact_Table['feature '+str(f)][idx][t]
                c_len = Planter_config['p4 config']['width of code'][t][f]
                codes = ten_to_bin(int(c_tree), int(c_len)) + codes
            Entry["action_params"]["tree"] = int(codes, 2)
            Table_entries += [Entry]

    count_code = {}
    for f in range(num_features):
        count_code[f] = 0

    for t in range(num_trees):
        for idx in Exact_Table['tree '+str(t)]:
            key_value = int(idx)
            Entry = {}
            Entry["table"] = "SwitchIngress.lookup_leaf_id"+str(t)
            Entry["match"] = {}
            for f in range(num_features):
                key = "meta.code_f"+str(f)+"[" + str(int(count_code[f] + Planter_config['p4 config']['width of code'][t][f] - 1)) + ":" + str(int(count_code[f])) + "]"
                Entry["match"][key] = int(Exact_Table['tree '+str(t)][idx]['f'+str(f)+' code'])
            Entry["action_name"] = "SwitchIngress.read_prob"+str(t)
            Entry["action_params"] = {}
            Entry["action_params"]["prob"] = 0
            Entry["action_params"]["vote"] = int(Exact_Table['tree '+str(t)][idx]['leaf'])
            Table_entries += [Entry]
        for f in range(num_features):
            count_code[f] += Planter_config['p4 config']['width of code'][t][f]

    for idx in Exact_Table['decision']:
        key_value = int(idx)
        Entry = {}
        Entry["table"] = "SwitchIngress.decision"
        Entry["match"] = {}
        for t in range(num_trees):
            Entry["match"]["meta.tree_" + str(t)+"_vote"] = int(Exact_Table['decision'][idx]['t' + str(t) + ' vote'])
        Entry["action_name"] = "SwitchIngress.read_lable"
        Entry["action_params"] = {}
        Entry["action_params"]["label"] = np.int(Exact_Table['decision'][idx]['class'])
        Table_entries += [Entry]

    Runtime = {}
    Runtime["table_entries"] = Table_entries
    json.dump(Runtime, open('Tables/Runtime.json', 'w'), indent=4)

def create_tables_Commend(fname, config):
    num_features = config['data config']['number of features']
    num_classes = config['model config']['number of classes']
    num_trees = config['model config']['number of trees']
    Exact_Table = json.load(open('Tables/Exact_Table.json', 'r'))
    with open(fname, 'w') as file:
        for f in range(num_features):
            for idx in Exact_Table['feature ' + str(f)]:
                key = int(idx)
                codes = ''
                for t in range(num_trees):
                    c_tree = Exact_Table['feature ' + str(f)][idx][t]
                    c_len = config['p4 config']['width of code'][t][f]
                    codes = ten_to_bin(int(c_tree), int(c_len)) + codes
                label = int(codes, 2)
                file.write("table_add SwitchIngress.lookup_feature" + str(f)+" extract_feature" + str(f)+
                           " "+str(key)+" => "+str(label)+"\n")

            file.write("\n")

        for t in range(num_trees):
            for idx in Exact_Table['tree ' + str(t)]:
                file.write("table_add SwitchIngress.lookup_leaf_id" + str(t) + " read_prob" + str(t) + " ")
                for f in range(num_features):
                    file.write(str(Exact_Table['tree ' + str(t)][idx]['f' + str(f) + ' code']) + " ")
                file.write("=> 0 " + str(Exact_Table['tree ' + str(t)][idx]['leaf']) + "\n")

            file.write("\n")

        for idx in Exact_Table['decision']:
            file.write("table_add SwitchIngress.decision read_lable ")
            for t in range(num_trees):
                file.write(str(Exact_Table['decision'][idx]['t' + str(t) + ' vote'])+" ")
            file.write("=> "+str(Exact_Table['decision'][idx]['class'])+"\n")


def create_tables_Commend_esnet(fname, config):
    num_features = config['data config']['number of features']
    num_classes = config['model config']['number of classes']
    num_trees = config['model config']['number of trees']
    Exact_Table = json.load(open('Tables/Exact_Table.json', 'r'))
    with open(fname, 'w') as file:
        for f in range(num_features):
            for idx in Exact_Table['feature ' + str(f)]:
                key = int(idx)
                codes = ''
                for t in range(num_trees):
                    c_tree = Exact_Table['feature ' + str(f)][idx][t]
                    c_len = config['p4 config']['width of code'][t][f]
                    codes = ten_to_bin(int(c_tree), int(c_len)) + codes
                label = int(codes, 2)
                file.write("table_add lookup_feature" + str(f)+" extract_feature" + str(f)+
                           " "+str(key)+" => "+str(label)+"\n")

            file.write("\n")

        for t in range(num_trees):
            for idx in Exact_Table['tree ' + str(t)]:
                file.write("table_add lookup_leaf_id" + str(t) + " read_prob" + str(t) + " ")
                for f in range(num_features):
                    file.write(str(Exact_Table['tree ' + str(t)][idx]['f' + str(f) + ' code']) + " ")
                file.write("=> 0 " + str(Exact_Table['tree ' + str(t)][idx]['leaf']) + "\n")

            file.write("\n")

        for idx in Exact_Table['decision']:
            file.write("table_add decision read_lable ")
            for t in range(num_trees):
                file.write(str(Exact_Table['decision'][idx]['t' + str(t) + ' vote'])+" ")
            file.write("=> "+str(Exact_Table['decision'][idx]['class'])+"\n")

def edit_tables_command_esnet_software(fname):
    with open(fname, 'a') as file:
        file.write(
            "# run traffin\n"
            "run_traffic packets\n\n"
            "# end\n"
            "exit\n")

def create_load_tables(fname, fjson, config, Planter_config, file_name):
    work_root = Planter_config['directory config']['work']

    create_tables(Planter_config)

    commend_file = work_root + "/src/targets/bmv2/software/model_test/test_environment/s1-commands.txt"
    create_tables_Commend(commend_file, Planter_config)

    commend_file = work_root + "/Tables/s1-commands.txt"
    create_tables_Commend(commend_file, Planter_config)

    commend_file_esnet_hardware = work_root + "/src/targets/alveo_u280/hardware/s1-commands.txt"
    create_tables_Commend_esnet(commend_file_esnet_hardware, Planter_config)

    commend_file_esnet_software = work_root + "/src/targets/alveo_u280/behavioral/test_environment/sim/test-case0/runsim.txt"
    create_tables_Commend_esnet(commend_file_esnet_software, Planter_config)
    edit_tables_command_esnet_software(commend_file_esnet_software)

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


        for i in range(0, config['num_features']):
            tload.write("print('load feature " + str(i) + " table with',len(table['feature " + str( i) + "'].keys()),'entries')\n" \
                        "for k in range(len(table['feature " + str( i) + "'].keys())):\n")
            tload.write("    key = str(k)\n")
            
            tload.write("    codes = ''\n")
            tload.write("    for tree in range(config['number of trees']):\n")
            tload.write("        codes = ten_to_bin(int(table['feature " + str(
                i) + "'][key][tree]), int(config['width of code'][tree][" + str(i) + "])) + codes\n")
            tload.write("    " + (config['debug_load_table'] * "# ") + \
                        "Ingress.lookup_feature" + str(i) + \
                        ".add_with_extract_feature" + str(i) + \
                        "(int(key), int(codes,2))\n")
            if config['debug_load_table']:
                tload.write(
                    "    print('\\r{}th entry —— feature value: {} mask: {} priority: {} codes: {}'.format(key, table['feature " + str(
                        i) + \
                    "'][key][1],table['feature " + str(i) + \
                    "'][key][0], int(key), int(codes,2)), end='')\n\n")

        # Load tree tables
        for i in range(0, config['num_trees']):
            tload.write("print('load tree (code/code to vote) " + str(i) + " table with',len(table['tree " + str(
                i) + "'].keys()),'entries')\n")
            tload.write("for key in table['tree " + str(i) + "']:\n")
            tload.write("    " + (config['debug_load_table'] * "# ") + \
                        "Ingress.lookup_leaf_id" + str(
                i) + ".add_with_read_prob" + str(
                i) + "(")
            for f in range(config['num_features']):
                tload.write("table['tree " + str(i) + "'][key]['f" + str(f) + " code'], ")
            tload.write("0, table['tree " + str(i) + "'][key]['leaf'])\n")
            if config['debug_load_table']:
                tload.write("    print('\\r{}th entry ——")
                for f in range(config['num_features']):
                    tload.write(" f" + str(f) + "_code: {}")
                tload.write(" vote: {}'.format(key, ")
                for f in range(config['num_features']):
                    tload.write("table['tree " + str(i) + "'][key]['f" + str(f) + " code'], ")
                tload.write("int(table['tree " + str(i) + "'][key]['leaf'])), end='')\n\n")

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
