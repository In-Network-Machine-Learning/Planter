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
# Functions: This file is the p4 generator (Standard P4) for psa architecture.
#            Please refer to ./Docs/Planter_User_Document.pdf or further information.

import sys, getopt
import os
import json
import binascii
import numpy as np
from dedicated_p4 import *
from common_p4 import *
from src.functions.add_license import *





def create_headers(fname, config):
    with open(fname, 'a') as headers:
        headers.write("/*************************************************************************\n"
                     "*********************** headers and metadata******************************\n"
                     "*************************************************************************/\n\n")
    common_basic_headers(fname, config)
    common_headers(fname, config)
    separate_metadata(fname, config)



###################################################
# Create a parser file to be used
# input: parser file name, configuration
# output: none
###################################################

# This code currently does not support skipping columns. This is to be added once the basic functionality is tested
def create_parser(fname, config):

    with open(fname, 'a') as parser:

        parser.write("/*************************************************************************\n"
                     "*********************** Ingress Parser ***********************************\n"
                     "*************************************************************************/\n\n")



        parser.write(
            "parser SwitchIngressParser(\n"
            "    packet_in pkt,\n"
            "    out header_t hdr,\n"
            "    inout metadata_t meta,\n"
            "    in psa_ingress_parser_input_metadata_t ig_intr_md) {\n\n")

        parser.write("    state start {\n"
                     "        transition parse_ethernet;\n"
                     "    }\n\n")

    common_parser(fname, config)
    with open(fname, 'a') as parser:
        parser.write("}\n\n")
        parser.write("/*************************************************************************\n"
                     "*********************** Ingress Deparser *********************************\n"
                     "**************************************************************************/\n\n")

        parser.write("control SwitchIngressDeparser(\n"
                     "    packet_out pkt,\n"
                     "    inout header_t hdr,\n" 
                     "    in metadata_t meta,\n"
                     "    in psa_ingress_output_metadata_t ig_out_md) {\n"
                     "    apply {\n")

        parser.write("        pkt.emit(hdr);\n    }\n}\n\n")


        # ==============================================================================================

        parser.write("/*************************************************************************\n"
                     "*********************** Egress Parser ***********************************\n"
                     "*************************************************************************/\n\n")

        parser.write(
            "parser SwitchEgressParser(\n"
            "    packet_in pkt,\n"
            "    out header_t hdr,\n"
            "    inout metadata_t meta,\n"
            "    in psa_egress_parser_input_metadata_t eg_intr_md) {\n")
            # "    CommonParser() common_parser;\n")

        parser.write("    state start {\n"
                     # "        pkt.extract(eg_intr_md);\n"
                     # "        common_parser.apply(pkt,hdr);\n"
                     "        transition accept;\n"
                     "        }\n\n"
                     "}\n\n")

        parser.write("/*************************************************************************\n"
                     "*********************** Egress Deparser *********************************\n"
                     "**************************************************************************/\n\n")

        parser.write("control SwitchEgressDeparser(\n"
                     "    packet_out pkt,\n"
                     "    inout header_t hdr,\n"
                     "    in metadata_t eg_md,\n"
                     "    in psa_egress_output_metadata_t eg_dprsr_md,\n"
                     "    in psa_egress_deparser_input_metadata_t psa_egress_deparser_input_metadata){\n"
                     "    apply {\n"
                     "        pkt.emit(hdr);\n"
                     "    }\n"
                     "}\n\n")


###################################################
# Create an ingress control file
# input: ingress_control file name, configuration
# output: none
###################################################

# This code currently does not support skipping columns. This is to be added once the basic functionality is tested
def create_ingress_control(fname, config):

    with open(fname, 'a') as ingress:

        ingress.write("/*************************************************************************\n"
                      "*********************** Ingress Processing********************************\n"
                      "**************************************************************************/\n\n")

        ingress.write("control SwitchIngress(\n"
                      "    inout header_t hdr,\n"
                      "    inout metadata_t meta,\n"
                      "    in    psa_ingress_input_metadata_t  ig_intr_md,\n"
                      "    inout psa_ingress_output_metadata_t ig_out_md){\n\n")


        ingress.write("    action send(PortId_t port) {\n"
                      "        ig_out_md.egress_port = port;\n"
                      "    }\n\n")

    # =================== Tables and actions =================

    separate_tables(fname, config)


    with open(fname, 'a') as ingress:
        ingress.write("    apply{\n")

    # =================== Logics =================
    separate_logics(fname, config)

    with open(fname, 'a') as ingress:
        ingress.write("    }\n" )
        ingress.write("}\n")


###################################################
# Create an egress control file
# input: egress_control file name, configuration
# output: none
###################################################

# This code currently does not support skipping columns. This is to be added once the basic functionality is tested
def create_egress_control(fname, config):

    with open(fname, 'a') as egress:
        egress.write("/*************************************************************************\n"
                     "*********************** egress Processing********************************\n"
                     "**************************************************************************/\n\n"
                     "control SwitchEgress(\n"
                     "    inout header_t hdr,\n"
                     "    inout metadata_t meta,\n"
                     "    in psa_egress_parser_input_metadata_t eg_intr_md,"
                     "    inout psa_egress_output_metadata_t eg_out_md) {\n\n")

        egress.write("    apply {\n"
                     )

        egress.write("    }\n}\n")


###################################################
# Create main function in p4 code
# input: table script file name, tables data json file name, configuration
# output: none
###################################################
def create_main(fname, config):
    with open(fname, 'a') as main:
        main.write("/*************************************************************************\n"
                     "***********************  S W I T C H  ************************************\n"
                     "*************************************************************************/\n\n"
                     "PSA_Switch(\n"
                     "    IngressPipeline(\n"
                     "        SwitchIngressParser(),\n"
                     "        SwitchIngress(),\n"
                     "        SwitchIngressDeparser()\n"
                     "    ),\n"
                     "    PacketReplicationEngine(),\n"
                     "    EgressPipeline(\n"
                     "        SwitchEgressParser(),\n"
                     "        SwitchEgress(),\n"
                     "        SwitchEgressDeparser()\n"
                     "    ),\n"
                     "    BufferingQueueingEngine()\n"
                     ") main;")


###################################################
# Create includes in code
# input: table script file name, tables data json file name, configuration
# output: none
###################################################

def create_include(fname, config):
    with open(fname, 'a') as main:
        main.write("#include <core.p4>\n")
        main.write("#include <psa.p4>\n\n")

###################################################
# Load the configuration from the config file
# input: config file name
# output: structure of config parameters
###################################################





##################################################
# Main function
# Parse input, set file name and call functions
##################################################

def main():
    # The list of files being manipulated
    config_file = 'Planter_config.json'
    # load configuration from file
    config, Planter_config = load_config(config_file)

    ##################################################
    # print('Generate p4 files')
    file_name = Planter_config['model config']['model']+'_'+Planter_config['target config']['use case']+'_'+Planter_config['data config']['dataset']
    p4_file = Planter_config['directory config']['work'] + '/P4/' + file_name+'.p4'
    tables_json = Planter_config['p4 config']['table name']

    ##################################################
    print('Generating p4 files and load data file...',end=" ")
    add_license(p4_file)

    add_model_intro(p4_file, config)

    # create include file
    create_include(p4_file, config)
    # create headers file
    create_headers(p4_file, config)
    # create ingress parser
    create_parser(p4_file, config)
    # create ingress control
    create_ingress_control(p4_file, config)
    # create egress control
    create_egress_control(p4_file, config)
    # create main function
    create_main(p4_file, config)

    ##################################################
    load_data_file = Planter_config['directory config']['work'] + '/Tables/load_table.py'
    # create load tables script
    add_license(load_data_file)
    create_load_tables(load_data_file, tables_json, config, Planter_config, file_name)
    print("Done")


if __name__ == "__main__":
    main()


