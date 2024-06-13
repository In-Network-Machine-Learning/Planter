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
    config['num_hps'] = Planter_config['p4 config']["number of hps"]
    config['f_tbl_len'] = Planter_config['p4 config']["feature tbl len"]
    config['thresh_and_bias'] = Planter_config['p4 config']['thresh and bias']
    config['hp_info'] = Planter_config['p4 config']['hp_info']

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
        for f in range(0, config['num_features']):
            for h in range(0, config['num_hps']):
                headers.write("    bit<" + str(config['num_bits']) + "> f" + str(f) +"_hp" + str(h)+ ";\n")
        for h in range(0, config['num_hps']):
            headers.write("    bit<" + str(config['num_bits']) + "> bias_hp" + str(h) + ";\n")
        for h in range(0, config['num_hps']):
            headers.write("    bit<" + str(config['num_bits']) + "> threshold_hp" + str(h) + ";\n")
        for h in range(0, config['num_hps']):
            headers.write("    bit<" + str(config['num_bits']) + "> result_hp" + str(h) + ";\n")
        for c in range(0, config['num_classes']):
            headers.write("    bit<4> vote_c" + str(c) + ";\n")


        # headers.write("}\n\n")




def separate_tables(fname, config):
    with open(fname, 'a') as ingress:
        for f in range(0, config['num_features']):
            ingress.write("    action extract_feature" + str(f)+'(')
            for h in range(0, config['num_hps']):
                if h==0:
                    ingress.write("bit<" + str(config['num_bits']) + "> f" + str(f) + "hp" + str(h))
                else:
                    ingress.write(", bit<" + str(config['num_bits']) + "> f"+str(f)+"hp"+str(h))
            ingress.write("){\n")
            for h in range(0, config['num_hps']):
                ingress.write("        meta.result_hp" + str(h)+" = meta.result_hp" + str(h)+" + f"+str(f)+"hp"+str(h) +";\n")
            ingress.write("    }\n\n")



        for f in range(0, config['num_features']):
            ingress.write("    table lookup_feature" + str(f) + " {\n"
                     "        key = { meta.feature" + str(f) + ":exact; }\n"
                     "        actions = {\n"
                     "            extract_feature" + str(f) + "();\n"
                     "            NoAction;\n"
                     "            }\n"
                     "        size = " + str( config['f_tbl_len'][f]) + ";\n"
                     "        default_action = NoAction;\n"
                     "    }\n\n")


        ingress.write("    action read_thresh_and_bias(")
        for h in range(0, config['num_hps']):
            if h==0:
                ingress.write("bit<" + str(config['num_bits']) + "> thresh_hp" + str(h))
            else:
                ingress.write(", bit<" + str(config['num_bits']) + "> thresh_hp"+str(h))
        for h in range(0, config['num_hps']):
            ingress.write(", bit<" + str(config['num_bits']) + "> bia_hp" + str(h))
        ingress.write("){\n")
        for h in range(0, config['num_hps']):
            ingress.write("        meta.threshold_hp" + str(h)+ " = thresh_hp"+str(h) +";\n")
        for h in range(0, config['num_hps']):
            ingress.write("        meta.result_hp" + str(h)+ " = bia_hp"+str(h) +";\n")
        ingress.write("    }\n\n")



        ingress.write("    table thresh_and_bias {\n"
                      "        key = {meta.flag:exact;}\n"
                      "        actions={read_thresh_and_bias; NoAction;}\n"
                      "        default_action = NoAction;\n"
                      "        size = 1;\n"
                      "    }\n\n")

        ingress.write("    action read_lable(bit<32> label){\n"
                      "        meta.result = label;\n"
                      "    }\n\n")

        ingress.write("    table decision {\n"
                      "        key = {\n")
        for c in range(config['num_classes']):
            ingress.write("            meta.vote_c"+str(c)+": exact;\n")
        ingress.write("        }\n"
                      "        actions={read_lable; NoAction;}\n"
                      "        default_action = NoAction;\n"
                      "        size = "+str(config['num_classes']**config['num_hps'])+";\n"
                      "    }\n\n")


def separate_logics(fname, config):
    with open(fname, 'a') as ingress:
        for c in range(0, config['num_classes']):
            ingress.write("        meta.vote_c"+str(c)+"=0;\n")

        ingress.write("        thresh_and_bias.apply();\n")
        for f in range(0, config['num_features']):
            ingress.write("        lookup_feature" + str(f) + ".apply();\n")

        for h in range(0, config['num_hps']):
            ingress.write("        meta.result_hp" + str(h) + " = meta.threshold_hp"+str(h)+" - meta.result_hp"+str(h)+ ";\n")
        for h in range(0, config['num_hps']):
            ingress.write("        if(meta.result_hp" + str(h) + " & 0b1"+"0"*(config['num_bits']-1)+"==0){\n")
            if config['num_classes']!=2:
                ingress.write( "            meta.vote_c" + str(config['hp_info'][str(h)][1]) + " = meta.vote_c" + str(config['hp_info'][str(h)][1]) + "+ 1;\n")
            else: ingress.write( "            meta.vote_c" + str(config['hp_info'][str(h)][0]) + " = meta.vote_c" + str(config['hp_info'][str(h)][0]) + "+ 1;\n")
            ingress.write("        }else{")
            if config['num_classes']!=2:
                ingress.write("meta.vote_c"+str(config['hp_info'][str(h)][0]) +" = meta.vote_c"+str(config['hp_info'][str(h)][0]) +"+ 1;}\n\n")
            else:ingress.write("meta.vote_c"+str(config['hp_info'][str(h)][1]) +" = meta.vote_c"+str(config['hp_info'][str(h)][1]) +"+ 1;}\n\n")
        ingress.write("        decision.apply();\n")




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
    num_hps = np.int(num_classes * (num_classes - 1) / 2)
    Exact_Table = json.load(open('Tables/Exact_Table.json', 'r'))
    for f in range(num_features):
        for idx in Exact_Table['f' + str(f)]:
            key_value = int(idx)
            Entry = {}
            Entry["table"] = "SwitchIngress.lookup_feature"+str(f)
            Entry["match"] = {}
            Entry["match"]["meta.feature"+str(f)] = key_value
            Entry["action_name"] = "SwitchIngress.extract_feature"+str(f)
            Entry["action_params"] = {}
            for hp in range(num_hps):
                Entry["action_params"]["f"+str(f)+"hp"+str(hp)] = Exact_Table['f' + str(f)][idx]["hp "+str(hp)]
            Table_entries += [Entry]


    for idx in Exact_Table['decision']:
        Entry = {}
        Entry["table"] = "SwitchIngress.decision"
        Entry["match"] = {}
        for c in range(num_classes):
            Entry["match"]["meta.vote_c"+str(c)] = np.int(Exact_Table['decision'][idx]['c'+str(c)+' vote'])
        Entry["action_name"] = "SwitchIngress.read_lable"
        Entry["action_params"] = {}
        Entry["action_params"]["label"] = np.int(Exact_Table['decision'][idx]["class"])
        Table_entries += [Entry]

    Entry = {}
    Entry["table"] = "SwitchIngress.thresh_and_bias"
    Entry["match"] = {}
    Entry["match"]["meta.flag"] = 1
    Entry["action_name"] = "SwitchIngress.read_thresh_and_bias"
    Entry["action_params"] = {}
    for hp in range(num_hps):
        Entry["action_params"]["thresh_hp"+str(hp)] = np.int(Exact_Table['threshold hp'+str(hp)])
        Entry["action_params"]["bia_hp" + str(hp)] = np.int(Exact_Table['bias hp' + str(hp)])
    Table_entries += [Entry]

    Runtime = {}
    Runtime["table_entries"] = Table_entries
    json.dump(Runtime, open('Tables/Runtime.json', 'w'), indent=4)
    # print('BMv2 runtime file is partly generated')


def create_tables_Commend(fname, config):
    num_features = config['data config']['number of features']
    num_classes = config['model config']['number of classes']
    num_hps = np.int(num_classes * (num_classes - 1) / 2)
    Exact_Table = json.load(open('Tables/Exact_Table.json', 'r'))
    with open(fname, 'w') as file:

        for f in range(num_features):
            for idx in Exact_Table['f' + str(f)]:
                key = int(idx)

                file.write("table_add SwitchIngress.lookup_feature" + str(f)+" extract_feature" + str(f)+
                           " "+str(key)+" => ")
                for hp in range(num_hps):
                    file.write(str(Exact_Table['f' + str(f)][idx][ "hp " + str(hp)])+" ")
                file.write("\n")
            file.write("\n")


        for idx in Exact_Table['decision']:
            key_value = int(idx)
            file.write("table_add SwitchIngress.decision read_lable ")
            for c in range(num_classes):
                file.write(str(int(Exact_Table['decision'][idx]['c' + str(c) + ' vote']))+" ")
            file.write("=> "+str(Exact_Table['decision'][idx]['class'])+"\n")


        file.write("table_add SwitchIngress.thresh_and_bias read_thresh_and_bias 1 => ")
        for hp in range(num_hps):
            file.write(str(np.int(Exact_Table['threshold hp' + str(hp)]))+" ")
        for hp in range(num_hps):
            file.write(str(np.int(np.int(Exact_Table['bias hp' + str(hp)]))) + " ")
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
            tload.write("print('load feature " + str(f) + " table with',len(table['f" + str(f) + "'].keys()),'entries')\n"
                        "for k in range(len(table['f" + str(f) + "'].keys())):\n")
            tload.write("    key = str(k)\n")
            
            tload.write("    " + (config['debug_load_table'] * "# ") +
                        "Ingress.lookup_feature" + str(f) +
                        ".add_with_extract_feature" + str(f) +
                        "(int(key), ")
            for h in range(0, config['num_hps']):
                if h==0:
                    tload.write("table['f" + str(f) + "'][key]['hp " + str(h) + "']")
                else:
                    tload.write(", table['f"+str(f)+"'][key]['hp "+str(h)+"']")
            tload.write(")\n\n")

            if config['debug_load_table']:
                tload.write(
                    "    print('\\r{}th entry —— feature value: {} mask: {} priority: {} codes: {}'.format(key, table['feature " + str(f) +
                    "'][key][1],table['feature " + str(f) +
                    "'][key][0], int(key), int(codes,2)), end='')\n\n")



        tload.write("print('load thresh_and_bias table with 1 entries')\n")
        tload.write((config['debug_load_table'] * "# ") +
                    "Ingress.thresh_and_bias.add_with_read_thresh_and_bias("
                    "1, ")
        for h in range(0, config['num_hps']):
            if h == 0:
                tload.write("table['threshold hp" + str(h) + "']")
            else:
                tload.write(", table['threshold hp" + str(h) + "']")
        for h in range(0, config['num_hps']):
            tload.write(", table['bias hp" + str(h) + "']")
        tload.write(")\n\n")

        tload.write("print('load decision table with',len(table['decision'].keys()),'entries')\n")
        tload.write("for key in table['decision']:\n")
        tload.write("    " + (config['debug_load_table'] * "# ") + \
                    "Ingress.decision.add_with_read_lable(")
        for c in range(config['num_classes']):
            tload.write("table['decision'][key]['c" + str(c) + " vote'], ")
        tload.write(" int(table['decision'][key]['class']))\n")




