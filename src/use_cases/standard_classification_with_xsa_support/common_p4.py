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
# Functions: This file is a use case-related P4 generator (common P4).
#            Please refer to ./Docs/Planter_User_Document.pdf or further information.

import numpy as np

def common_basic_headers(fname, config):
    with open(fname, 'a') as headers:

        headers.write("const bit<16> ETHERTYPE_Planter = 0x1234;\n"
                      "const bit<8>  Planter_P     = 0x50;   // 'P'\n"
                      "const bit<8>  Planter_4     = 0x34;   // '4'\n"
                      "const bit<8>  Planter_VER   = 0x01;   // v0.1\n\n" )

        headers.write("header ethernet_h {\n"
                      "    bit<48> dstAddr;\n"
                      "    bit<48> srcAddr;\n"
                      "    bit<16> etherType;\n"
                      "}\n\n" )

def common_metadata(fname, config):
    with open(fname, 'a') as headers:
        for f in range(0, config['num_features']):
            headers.write("    bit<32> feature" + str(f) + ";\n")
        headers.write("    bit<32> result;\n")
        headers.write("    bit<8> flag ;\n")



def common_headers(fname, config, xsa_architecture=False):
    # xsa_architecture is used because this does not support using lookahead
    with open(fname, 'a') as headers:
        # write result header
        if xsa_architecture:
            headers.write("header Planter_prefix_h{\n")
        else:
            headers.write("header Planter_h{\n")

        headers.write("    bit<8> p;\n"
                      "    bit<8> four;\n"
                      "    bit<8> ver;\n"
                      "    bit<8> typ;\n")
        
        if xsa_architecture:
            headers.write(
                "}\n\n"
                "header Planter_h{\n"
            )
                
        for f in range(0, config['num_features']):
            headers.write("    bit<32> feature" + str(f) + ";\n")
        headers.write("    bit<32> result;\n")


        headers.write("}\n\n")

        # write the headers' structure
        headers.write("struct header_t {\n"
                      "    ethernet_h   ethernet;\n")
        if xsa_architecture:
            headers.write("    Planter_prefix_h Planter_prefix;\n") 
        headers.write("    Planter_h    Planter;\n"
                      "}\n\n")


def common_parser(fname, config, xsa_architecture=False):
    with open(fname, 'a') as parser:
        parser.write("    state parse_ethernet {\n"
                     "        pkt.extract(hdr.ethernet);\n" 
                     "        transition select(hdr.ethernet.etherType) {\n" 
                     "        ETHERTYPE_Planter : check_planter_version;\n" 
                     "        default           : accept;\n" 
                     "        }\n" 
                     "    }\n\n" 
                     "    state check_planter_version {\n")
        if xsa_architecture:
            parser.write("        pkt.extract(hdr.Planter_prefix);\n"
                    "        transition select(hdr.Planter_prefix.p,\n"
                    "                           hdr.Planter_prefix.four,\n"
                    "                           hdr.Planter_prefix.ver) {\n")
        else:
            parser.write("        transition select(pkt.lookahead<Planter_h>().p,\n" 
                     "                          pkt.lookahead<Planter_h>().four,\n" 
                     "                          pkt.lookahead<Planter_h>().ver) {\n")
        parser.write("        (Planter_P, Planter_4, Planter_VER) : parse_planter;\n" 
                     "        default                             : accept;\n" 
                     "        }\n" 
                     "    }\n\n" 
                     "    state parse_planter {\n" 
                     "        pkt.extract(hdr.Planter);\n")
        if not xsa_architecture:
            for f in range(0, config['num_features']):
                parser.write("        meta.feature" + str(f) + " = hdr.Planter.feature" + str(f) + ";\n")
            parser.write("        meta.flag = 1 ;\n")

        parser.write("        transition accept;\n" 
                     "    }\n")


def common_logics(fname, config, xsa_architecture=False):
    with open(fname, 'a') as ingress:
        model_type = 'classification'
        try:
            model_type = config['model_type']
        except Exception as e:
            pass
        if model_type == 'classification' and not xsa_architecture:
            ingress.write("        hdr.Planter.result = meta.result;\n")
        elif not xsa_architecture:
            for ax in range(0, config['num_axis']):
                ingress.write("        hdr.Planter.feature" + str(ax) + " = meta.feature" + str(ax) + ";\n")
        ingress.write("        bit<48> tmp;\n"
                      "        /* Swap the MAC addresses */\n"
                      "        tmp = hdr.ethernet.dstAddr;\n"
                      "        hdr.ethernet.dstAddr = hdr.ethernet.srcAddr;\n"
                      "        hdr.ethernet.srcAddr = tmp;\n")
        if not xsa_architecture:
            ingress.write("        send(ig_intr_md.ingress_port);\n")
