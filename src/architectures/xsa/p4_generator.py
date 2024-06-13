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
# Functions: This file is the p4 generator (Standard P4) for xsa architecture.
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
                     "*********************** headers and metadata *****************************\n"
                     "*************************************************************************/\n\n")

    common_basic_headers(fname, config)
    common_headers(fname, config, xsa_architecture=True)

    with open(fname, 'a') as headers:
        headers.write(
            "struct metadata_t {\n"
            "   bit<64> timestamp_ns;\n"
            "   bit<16> pid;\n"
            "   bit<3> ingress_port;\n"
            "   bit<3> egress_port;\n"
            "   bit<1> truncate_enable;\n"
            "   bit<16> truncate_length;\n"
            "   bit<1> rss_enable;\n"
            "   bit<12> rss_entropy;\n"
            "   bit<4> drop_reason;\n"
            "   bit<32> scratch;\n"
            "}\n\n") 
    # esnet-smartnic-hw repository requires this version of user metadata


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
            "parser SwitchParser(\n"
            "    packet_in pkt,\n"
            "    out header_t hdr,\n"
            "    inout metadata_t meta,\n"
            "    inout standard_metadata_t ig_intr_md) {\n\n")

        parser.write("    state start {\n"
                     "        transition parse_ethernet;\n"
                     "    }\n\n")

    common_parser(fname, config, xsa_architecture=True)

    with open(fname, 'a') as parser:
        parser.write("}\n\n")

        parser.write("/*************************************************************************\n"
                     "*********************** Egress Deparser *********************************\n"
                     "**************************************************************************/\n\n")

        parser.write("control SwitchDeparser(\n"
                     "    packet_out pkt,\n"
                     "    in header_t hdr,\n"
                     "    inout metadata_t meta,\n"
                     "    inout standard_metadata_t ig_intr_md) {\n"
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

# xsa architecture only supports a single processing block
def create_processing_control(fname, config):

    with open(fname, 'a') as processing:

        processing.write("/*************************************************************************\n"
                      "*********************** Processing********************************\n"
                      "**************************************************************************/\n\n")

        processing.write("control SwitchProcessing(\n    inout header_t hdr,\n"
                      "    inout metadata_t meta,\n"
                      "    inout standard_metadata_t ig_intr_md) {\n\n")
        
        

    separate_variables(fname, config)
    try:
        common_variables(fname, config)
    except Exception as e:
        pass


    with open(fname, 'a') as processing:
        processing.write("\n")
        processing.write("    action drop() {\n"
                      "        ig_intr_md.drop=1;\n"
                      "    }\n\n")

    # =================== Tables and actions =================
    try:
        common_tables(fname, config)
    except Exception as e:
        pass
    separate_tables(fname, config, xsa_architecture=True)


    with open(fname, 'a') as ingress:
        ingress.write("    apply{\n")

    # =================== Logics =================
    try:
        common_feature_extraction(fname, config)
    except Exception as e:
        pass
    separate_logics(fname, config)
    common_logics(fname, config, xsa_architecture=True)

    with open(fname, 'a') as ingress:
        ingress.write("    }\n" )
        ingress.write("}\n")


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
                     "XilinxPipeline(\n"
                     "    SwitchParser(),\n"
                     "    SwitchProcessing(),\n"
                     "    SwitchDeparser()\n"
                     ") main;")


###################################################
# Create includes in code
# input: table script file name, tables data json file name, configuration
# output: none
###################################################

def create_include(fname, config):
    with open(fname, 'a') as main:
        main.write("#include <core.p4>\n")
        main.write("#include <xsa.p4>\n\n")

###################################################
# Load the configuration from the config file
# input: config file name
# output: structure of config parameters
###################################################



###################################################
# create comments to comment out license file
###################################################
def add_open_comment(fname, config):
    with open(fname, 'a') as f:
        f.write("/*\n")

def add_close_comment(fname, config):
    with open(fname, 'a') as f:
        f.write("*/\n")

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

    add_license(p4_file, xsa_architecture=True)

    add_model_intro(p4_file, config)

    # create include file
    create_include(p4_file, config)
    # create headers file
    create_headers(p4_file, config)
    # create ingress parser
    create_parser(p4_file, config)
    # create processing control
    create_processing_control(p4_file, config)
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


