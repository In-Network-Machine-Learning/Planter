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
                          +" = meta.middle_c" +str(int(compare[0])) +" - meta.middle_c"+str(int(compare[1]))+";\n")

            c_n += 1
            write_compare(c_n, con_list, num_class, txt)
            c_n -= 1

    return


def do_compare(c_n, con_list, num_class, txt, label, config):
    if c_n == num_class-1:
        txt.write("         "+c_n*"    "+"hdr.Planter.result = "+str(int(label))+";\n"
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
                          +(10-1)*"0"+"!=0){\n") #<0
            else:
                label = compare[0]
                txt.write("        "+c_n*"    "+con + "{\n")
            c_n += 1
            do_compare(c_n, con_list, num_class, txt, label, config)
            c_n -= 1
            if con == 'else' and c_n != 0:
                txt.write("        " + (c_n-1) * "    " + "}\n")
    return


def load_config(fname):
    Planter_config = json.load(open('src/configs/' + fname, 'r'))
    config_file = Planter_config['p4 config']
    config = {}
    config['num_features'] = config_file["number of features"]
    config['num_hidden_nodes'] = config_file['num hidden nodes']
    config['num_layers'] = config_file["number of layers"]
    config['num_classes'] = config_file["number of classes"]
    config['model'] = config_file['model']
    config['width'] = config_file["width of inputs"]
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
                     " *        0                1                  2               3\n"
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
            headers.write("    bit<" + str(10) + "> middle_c" + str(c) + ";\n")

        for c in range(config['num_classes']):
            for c1 in range(c + 1, config['num_classes']):
                headers.write("    bit<" + str(10) + "> compare" + str(c) + "_" + str(c1) + ";\n")

        headers.write("    bit<64> bnnInput;\n"
                      "    bit<64> XNOROutput;\n"
                      "    bit<64> NextLayerInput;\n"
                      "    bit<1> activated;\n"
                      "    bit<32>  DstAddr;\n")
        # headers.write("}\n\n")

def separate_logics(fname, config):
    with open(fname, 'a') as ingress:
        ingress.write("        meta.bnnInput = 0;\n"
                      "        meta.XNOROutput = 0;\n"
                      "        meta.NextLayerInput = 0;\n"
                      "        BuildInput();\n\n")

        count = 0
        for l in range(config['num_layers']):
            ingress.write("        Layer"+str(l)+"_Process("+str(int(count))+");\n")
            if l + 1 != config['num_layers']:
                ingress.write("        meta.bnnInput = meta.NextLayerInput;\n"
                              "        meta.NextLayerInput = 0;\n")
            ingress.write("\n")
            if l+1== config['num_layers']:
                break
            count+=config['num_hidden_nodes'][l]

        ingress.write("        compare();\n")
        do_compare(0, (np.ones(config['num_classes'])).tolist(), config['num_classes'], ingress, 0, config)

        # ingress.write("        \n"
        #               "        bit<48> tmp;\n"
        #               "        /* Swap the MAC addresses */\n"
        #               "        tmp = hdr.ethernet.dstAddr;\n"
        #               "        hdr.ethernet.dstAddr = hdr.ethernet.srcAddr;\n"
        #               "        hdr.ethernet.srcAddr = tmp;\n"
        #               # "        bit < 64 > weight = 0;\n"
        #               # "        weights.read( weight, 0); \n"
        #               # "        hdr.Planter.result = (bit<32>)meta.bnnInput;\n"
        #               # "        hdr.Planter.result = debug;\n"
        #               # "        hdr.Planter.result = (bit<32>)meta.middle_c2;\n"
        #               "        send(ig_intr_md.ingress_port);\n")


def separate_tables(fname, config):
    with open(fname, 'a') as ingress:



        ingress.write("    register<bit<64>>(1024) weights;\n"
                      # "    //bit<8> count = 0;\n"
                      # "    bit<1> activated = 0;\n"
                      "    bit<128> m1 = 0x55555555555555555555555555555555;\n"
                      "    bit<128> m2 = 0x33333333333333333333333333333333;\n"
                      "    bit<128> m4 = 0x0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f;\n"
                      "    bit<128> m8 = 0x00ff00ff00ff00ff00ff00ff00ff00ff;\n"
                      "    bit<128> m16= 0x0000ffff0000ffff0000ffff0000ffff;\n"
                      "    bit<128> m32= 0x00000000ffffffff00000000ffffffff;\n"
                      "    bit<128> m64= 0x0000000000000000ffffffffffffffff;\n\n")



        ingress.write("    action XNOR(bit<64> weight){\n"
                      "        meta.XNOROutput = weight^meta.bnnInput;\n"
                      "        meta.XNOROutput = ~meta.XNOROutput;\n"
                      "    }\n\n")

        for l in range(config['num_layers']):
            if l+1 == config['num_layers']:
                break
            if l==0:
                threshold = np.sum(config['width']) / 2
            else:
                threshold = config['num_hidden_nodes'][l-1] / 2
            ingress.write("    action BitCount_l"+str(l)+"(bit<64> bitInput){\n"
                          "        bit<128> x= (bit<128>)bitInput;\n"
                          "        x = (x & m1 ) + ((x >>  1) & m1 );\n"
                          "        x = (x & m2 ) + ((x >>  2) & m2 );\n"
                          "        x = (x & m4 ) + ((x >>  4) & m4 );\n"
                          "        x = (x & m8 ) + ((x >>  8) & m8 );\n"
                          "        x = (x & m16) + ((x >> 16) & m16);\n"
                          "        x = (x & m32) + ((x >> 32) & m32);\n"
                          "        x = (x & m64) + ((x >> 64) & m64);\n"
                          "        meta.activated = (x>"+str(np.int(np.floor(threshold)))+") ? (bit<1>)1 : 0;\n"
                          "        meta.NextLayerInput = meta.NextLayerInput<<1;\n"
                          "        meta.NextLayerInput = meta.NextLayerInput + (bit<64>)meta.activated;\n"
                          "    }\n\n")

        for c in range(config['num_classes']):
            ingress.write("    action BitCount_c"+str(c)+"(bit<64> bitInput){\n"
                         "        bit<128> x= (bit<128>)bitInput;\n"
                         "        x = (x & m1 ) + ((x >>  1) & m1 );\n"
                         "        x = (x & m2 ) + ((x >>  2) & m2 );\n"
                         "        x = (x & m4 ) + ((x >>  4) & m4 );\n"
                         "        x = (x & m8 ) + ((x >>  8) & m8 );\n"
                         "        x = (x & m16) + ((x >> 16) & m16);\n"
                         "        x = (x & m32) + ((x >> 32) & m32);\n"
                         "        x = (x & m64) + ((x >> 64) & m64);\n"
                         "        meta.middle_c"+str(c)+" = (bit<10>) x;\n"
                         "    }\n\n")

        for l in range(config['num_layers']):
            if l == 0:
                num_zeros = np.int(128 - np.sum(config['width']))
                num_ones = np.int(np.sum(config['width']))
                bound =  int("0b"+"0"*num_zeros+"1"*num_ones,2)
            else:
                num_zeros = np.int(128 - config['num_hidden_nodes'][l - 1])
                num_ones = np.int(config['num_hidden_nodes'][l - 1])
                bound = int("0b" + "0" * num_zeros + "1" * num_ones, 2)
            if l==0:
                ingress.write("    action Layer"+str(l)+"_Process(bit <10> offset){ \n"
                              # "        bit < "+str(np.int(np.sum(config['width'])))+" > weight = 0;\n"
                              "        bit <64> weight = 0;\n")
                              # "        meta.NextLayerInput = 0;\n")
                for h in range(config['num_hidden_nodes'][l]):
                    ingress.write("        weights.read( weight, (bit<32>)offset+"+str(h)+");\n"
                                  "        XNOR(weight);\n"
                                  "        meta.XNOROutput = (bit<64>)meta.XNOROutput["+str(num_ones-1)+":0];\n"
                                  "        BitCount_l"+str(l)+"(meta.XNOROutput);\n")
                ingress.write("    }\n\n")
            elif l+1==config['num_layers']:
                ingress.write("    action Layer" + str(l) + "_Process(bit <10> offset){ \n"
                              "        bit <64> weight = 0;\n")
                              # "        meta.NextLayerInput = 0;\n")
                for c in range(config['num_classes']):
                    ingress.write("        weights.read( weight, (bit<32>)offset+" + str(c) + ");\n"
                                  "        XNOR(weight);\n"
                                  "        meta.XNOROutput = (bit<64>)meta.XNOROutput["+str(num_ones-1)+":0];\n"
                                  "        BitCount_c"+str(c)+"(meta.XNOROutput);\n")
                ingress.write("    }\n\n")
            else:
                ingress.write("    action Layer"+str(l)+"_Process(bit <10> offset){ \n"
                              "        bit <64> weight = 0;\n"
                              "        meta.NextLayerInput = 0;\n")
                for h in range(config['num_hidden_nodes'][l]):
                    ingress.write("        weights.read(weight, (bit<32>)offset+"+str(h)+");\n"
                                  "        XNOR(weight);\n"
                                  "        meta.XNOROutput = (bit<64>)meta.XNOROutput["+str(num_ones-1)+":0];\n"
                                  "        BitCount_l"+str(l)+"(meta.XNOROutput);\n")
                ingress.write("    }\n\n")

        ingress.write("    action compare(){\n")
        write_compare(0, (np.ones(config['num_classes'])).tolist(), config['num_classes'], ingress)
        ingress.write("    }\n\n")

        ingress.write("    action BuildInput(){\n")
        for f in range(config['num_features']):
            if f+1<config['num_features']:
                ingress.write("        meta.bnnInput = (meta.bnnInput + (bit <64>) hdr.Planter.feature"+str(f)+") << "+str(np.int(config['width'][f+1]))+";\n")
            else:
                ingress.write("        meta.bnnInput = (meta.bnnInput + (bit <64>) hdr.Planter.feature" + str(f) + ") ;\n")

        ingress.write("    }\n\n")

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
    Exact_Table = json.load(open('Tables/Exact_Table.json', 'r'))
    with open(fname, 'w') as file:
        for idx in range(len(Exact_Table['weights'])):
            file.write("register_write SwitchIngress.weights "+str(idx)+" "+str(Exact_Table['weights'][idx])+"\n")





def create_load_tables(fname, fjson, config, Planter_config, file_name):
    work_root = Planter_config['directory config']['work']

    commend_file = work_root + "/src/targets/bmv2/software/model_test/test_environment/s1-commands.txt"
    create_tables_Commend(commend_file, Planter_config)

    commend_file = work_root + "/Tables/s1-commands.txt"
    create_tables_Commend(commend_file, Planter_config)


