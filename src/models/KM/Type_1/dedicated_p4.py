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

        for c in range(0, config['num_classes']):
            headers.write("    bit<" + str(config['num_bits']) + "> middle_c" + str(c) + ";\n")

        for c in range(config['num_classes']):
            for c1 in range(c+1, config['num_classes']):
                headers.write("    bit<" + str(config['num_bits']) + "> compare"+str(c)+"_"+str(c1)+";\n")

        # headers.write("}\n\n")




def separate_tables(fname, config):
    with open(fname, 'a') as ingress:
        for f in range(0, config['num_features']):
            ingress.write("    action extract_feature" + str(f)+'(')
            for c in range(0, config['num_classes']):
                if c==0:
                    ingress.write("bit<" + str(config['num_bits']) + "> f" + str(f) + "c" + str(c))
                else:
                    ingress.write(", bit<" + str(config['num_bits']) + "> f"+str(f)+"c"+str(c))
            ingress.write("){\n")
            if f==0:
                for c in range(0, config['num_classes']):
                    ingress.write( "        meta.middle_c" + str(c) + " =  f" + str(f) + "c" + str( c) + ";\n")
            else:
                for c in range(0, config['num_classes']):
                    ingress.write("        meta.middle_c" + str(c)+" = meta.middle_c" + str(c)+" + f"+str(f)+"c"+str(c) +";\n")
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




        ingress.write("    action compare(){\n")
        write_compare(0, (np.ones(config['num_classes'])).tolist(), config['num_classes'], ingress)
        ingress.write("    }\n\n")


def write_compare(c_n, con_list, num_class, txt):
    if c_n == num_class-1:
        return
    else:
        for con in ['if','else']:
            con_list[c_n] = con
            compare = [0,0]
            for d in range(c_n):
                if con_list[d] == 'if':
                    compare[0] = d+1
            compare[1] = c_n+1
            if con == 'if':
                txt.write("        meta.compare" +str(int(compare[0])) +"_"+str(int(compare[1]))
                          +" = meta.middle_c" +str(int(compare[1])) +" - meta.middle_c"+str(int(compare[0]))+";\n")

            c_n += 1
            write_compare(c_n, con_list, num_class, txt)
            c_n -= 1

    return


def do_compare(c_n, con_list, num_class, txt, label, config):
    if c_n == num_class-1:
        txt.write("         "+c_n*"    "+"meta.result = "+str(int(label))+";\n"
                  "         "+(c_n-1)*"    "+"}\n")
        return
    else:
        for con in ['if','else']:
            con_list[c_n] = con
            compare = [0,0]
            for d in range(c_n):
                if con_list[d] == 'if':
                    compare[0] = d+1
            compare[1] = c_n+1
            if con == 'if':
                label = compare[1]
                # print(con_list, c_n)
                txt.write("        "+c_n*"    "+con+"(meta.compare"
                          +str(int(compare[0]))+"_"+str(int(compare[1]))+"& 0b1"
                          +(config['num_bits']-1)*"0"+"!=0){\n") #<0
            else:
                label = compare[0]
                txt.write("        "+c_n*"    "+con + "{\n")
            c_n += 1
            do_compare(c_n, con_list, num_class, txt, label, config)
            c_n -= 1
            if con == 'else' and c_n != 0:
                txt.write("        " + (c_n-1) * "    " + "}\n")
    return


def separate_logics(fname, config):
    with open(fname, 'a') as ingress:

        # ingress.write("        class_prob.apply();\n")
        for f in range(0, config['num_features']):
            ingress.write("        lookup_feature" + str(f) + ".apply();\n")

        ingress.write("        compare();\n\n")


        do_compare(0, (np.ones(config['num_classes'])).tolist(), config['num_classes'], ingress, 0, config)




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
    Exact_Table = json.load(open('Tables/Exact_Table.json', 'r'))
    for f in range(num_features):
        for idx in Exact_Table['feature ' + str(f)]:
            key_value = int(idx)
            Entry = {}
            Entry["table"] = "SwitchIngress.lookup_feature" + str(f)
            Entry["match"] = {}
            Entry["match"]["meta.feature" + str(f)] = key_value
            Entry["action_name"] = "SwitchIngress.extract_feature" + str(f)
            Entry["action_params"] = {}
            for c in range(num_classes):
                Entry["action_params"]["f" + str(f) + "c" + str(c)] = Exact_Table['feature ' + str(f)][idx]["c" + str(c)]
            Table_entries += [Entry]

    Runtime = {}
    Runtime["table_entries"] = Table_entries
    json.dump(Runtime, open('Tables/Runtime.json', 'w'), indent=4)
    # print('BMv2 runtime file is partly generated')


def create_tables_Commend(fname, config):
    num_features = config['data config']['number of features']
    num_classes = config['model config']['number of classes']

    Exact_Table = json.load(open('Tables/Exact_Table.json', 'r'))
    with open(fname, 'w') as file:

        for f in range(num_features):
            for idx in Exact_Table['feature ' + str(f)]:
                key = int(idx)

                file.write("table_add SwitchIngress.lookup_feature" + str(f) + " extract_feature" + str(f) +
                           " " + str(key) + " => ")
                for c in range(num_classes):
                    file.write(str(Exact_Table['feature ' + str(f)][idx]["c" + str(c)]) + " ")
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
                        "for k in (table['feature " + str(f) + "'].keys()):\n")
            tload.write("    key = str(k)\n")
            
            tload.write("    " + (config['debug_load_table'] * "# ") +
                        "Ingress.lookup_feature" + str(f) +
                        ".add_with_extract_feature" + str(f) +
                        "(int(key), ")
            for c in range(0, config['num_classes']):
                if c==0:
                    tload.write("table['feature " + str(f) + "'][key]['c" + str(c) + "']")
                else:
                    tload.write(", table['feature "+str(f)+"'][key]['c"+str(c)+"']")
            tload.write(")\n\n")

            if config['debug_load_table']:
                tload.write(
                    "    print('\\r{}th entry —— feature value: {} mask: {} priority: {} codes: {}'.format(key, table['feature " + str(f) +
                    "'][key][1],table['feature " + str(f) +
                    "'][key][0], int(key), int(codes,2)), end='')\n\n")







