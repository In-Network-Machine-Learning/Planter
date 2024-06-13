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
# from target_related_p4 import *

def common_basic_headers(fname, config):
    with open(fname, 'a') as headers:

        headers.write("typedef bit<48> mac_addr_t;\n"
                      "typedef bit<32> ipv4_addr_t;\n"
                      "typedef bit<9> egressSpec_t;\n"
                      "const bit<16> ETHERTYPE_TPID = 0x8100;\n"
                      "const bit<16> ETHERTYPE_IPV4 = 0x0800;\n"
                      "const bit<16> ETHERTYPE_ARP = 0x0806;\n"
                      "typedef bit<8> ip_protocol_t;\n"
                      "const ip_protocol_t IP_PROTOCOLS_UDP = 17;\n"
                      "const bit<8> UDP_TYPE = 0x11;\n"
                      "const bit<8> TCP_TYPE = 0x06;\n"
                      "const int IPV4_HOST_TABLE_SIZE = 65536;\n"
                      "const bit<16> ETHERTYPE_Planter = 0x1234;\n"
                      "#define COLUMN_NUM 5\n\n" )

        headers.write("header ethernet_h {\n"
                      "    mac_addr_t dst_addr;\n"
                      "    mac_addr_t src_addr;\n"
                      "    bit<16> ether_type;\n"
                      "}\n\n" )

        headers.write("header ipv4_h {\n"
                      "    bit<4> version;\n"
                      "    bit<4> ihl;\n"
                      "    bit<8> diffserv;\n"
                      "    bit<16> totalLen;\n"
                      "    bit<16> identification;\n"
                      "    bit<3> flags;\n"
                      "    bit<13> frag_offset;\n"
                      "    bit<8> ttl;\n"
                      "    bit<8> protocol;\n"
                      "    bit<16> hdr_checksum;\n"
                      "    ipv4_addr_t src_addr;\n"
                      "    ipv4_addr_t dst_addr;\n"
                      "}\n\n" )

        headers.write("header udp_h{\n"
                      "    bit<16> srcPort;\n"
                      "    bit<16> dstPort;\n"
                      "    bit<16> hdr_length;\n"
                      "    bit<16> checksum;\n"
                      "}\n\n" )

        headers.write("header tcp_h{\n"
                      "    bit<16> srcPort;\n"
                      "    bit<16> dstPort;\n"
                      "    int<32> seqNo;\n"
                      "    int<32> ackNo;\n"
                      "    bit<4> data_offset;\n"
                      "    bit<4> res;\n"
                      "    bit<1> cwr;\n"
                      "    bit<1> ece;\n"
                      "    bit<1> urg;\n"
                      "    bit<1> ack;\n"
                      "    bit<1> psh;\n"
                      "    bit<1> rst;\n"
                      "    bit<1> syn;\n"
                      "    bit<1> fin;\n"
                      "    bit<16> window;\n"
                      "    bit<16> checksum;\n"
                      "    bit<16> urgentPtr;\n"
                      "}\n\n" )

        headers.write("header arp_h{\n"
                      "    bit<16> hwType;\n"
                      "    bit<16> protoType;\n"
                      "    bit<8> hwAddrLen;\n"
                      "    bit<8> protoAddrLen;\n"
                      "    bit<16> opcode;\n"
                      "    bit<48> hwSrcAddr;\n"
                      "    bit<32> protoSrcAddr;\n"
                      "    bit<48> hwDstAddr;\n"
                      "    bit<32> protoDstAddr;\n"
                      "}\n\n" )

        headers.write("header vlan_tag_h{\n"
                      "    bit<3> pcp;\n"
                      "    bit<1> dei;\n"
                      "    bit<12> vid;\n"
                      "    bit<16> ether_type;\n"
                      "    }\n\n")



def common_headers(fname, config):
    with open(fname, 'a') as headers:
        # write result header
        headers.write("header Planter_h{\n"
                      "    bit<8> p;\n"
                      "    bit<8> four;\n"
                      "    bit<8> ver;\n"
                      "    bit<8> typ;\n")

        for f in range(0, config['num_features']):
            headers.write("    bit<32> feature" + str(f) + ";\n")
        headers.write("    bit<32> result;\n")
        headers.write("}\n\n")

        headers.write("header extractData_h {\n"
                      "    bit < 32 > data; \n"
                      # "    bit < 8 > seperator;\n"
                      "}\n")

        headers.write("header result_h {\n"
                      "    bit < 32 > data; \n" 
                      "}\n")


        # write the headers' structure
        headers.write("struct header_t {\n"
                      "    ethernet_h   ethernet;\n"
                      "    vlan_tag_h   vlan_tag;\n"
                      "    ipv4_h       ipv4;\n"
                      "    arp_h        arp;\n" 
                      "    tcp_h        tcp;\n"
                      "    udp_h        udp;\n"
                      "    Planter_h    Planter;\n" 
                      "    extractData_h[COLUMN_NUM] extractData;\n"
                      "    result_h result;\n"
                      "}\n\n")




def common_metadata(fname, config):
    with open(fname, 'a') as headers:
        for f in range(0, config['num_features']):
            headers.write("    bit<32> feature" + str(f) + ";\n")
        headers.write("    bit<32> srcip;\n"
                      "    bit<32> dstip;\n"
                      "    bit<32> result;\n"
                      "    bit<8> flag ;\n")

def common_parser(fname, config):
    with open(fname, 'a') as parser:
        parser.write("    state parse_ethernet {\n"
                     "        pkt.extract(hdr.ethernet);\n"
                     "        transition select(hdr.ethernet.ether_type) {\n"
                     "            ETHERTYPE_TPID:  parse_vlan_tag;\n"
                     "            ETHERTYPE_IPV4:  parse_ipv4;\n"
                     "            ETHERTYPE_ARP:  parse_arp;\n"
                     "            ETHERTYPE_Planter:  parse_Planter;\n"
                     "            default: accept;\n"
                     "        }\n"
                     "    }\n\n"
                     "    state parse_vlan_tag {\n"
                     "        pkt.extract(hdr.vlan_tag);\n"
                     "        transition select(hdr.vlan_tag.ether_type) {\n"
                     "            ETHERTYPE_IPV4:  parse_ipv4;\n"
                     "            default: accept;\n"
                     "        }\n"
                     "    }\n\n"                    
                     "    state parse_ipv4 {\n"
                     "        pkt.extract(hdr.ipv4);\n"
                     "        transition select(hdr.ipv4.protocol) {\n"
                     "            UDP_TYPE:  parse_udp;\n"
                     "            TCP_TYPE:  parse_tcp;\n"
                     "            default: accept;\n"
                     "        }\n"
                     "    }\n\n"
                     "    state parse_arp {\n"
                     "        pkt.extract(hdr.arp);\n"
                     "        transition accept;\n"
                     "    }\n\n" 
                     "    state parse_udp { \n"
                     "        pkt.extract(hdr.udp);\n"
                     "        transition parse_Planter;\n"
                     "    }\n\n"
                     "    state parse_tcp {\n"
                     "        pkt.extract(hdr.tcp);\n" 
                     "        transition accept;\n"
                     "    }\n\n"
                     "    state parse_Planter {\n"
                     "        pkt.extract(hdr.Planter);\n"
                     "        transition parse_payload_0;\n"
                     "    }\n\n"
                     )


        for i in range(0, config['num_features']-1):
            parser.write("	state parse_payload_" + str(i) + " {\n"
                         "		pkt.extract(hdr.extractData[" + str(i) + "]);\n"  
                         "        meta.feature" + str(i) + " = (bit<32>) hdr.extractData[" + str(i) + "].data;\n"
                         "        transition parse_payload_" + str(i+1) + ";\n"
                         "		}\n\n")
        i = config['num_features']-1
        parser.write("	state parse_payload_" + str(i) + " {\n"
                     "		pkt.extract(hdr.extractData[" + str(i) + "]);\n"
                     "        meta.feature" + str(i) + " = (bit<32>) hdr.extractData[" + str(i) + "].data;\n"
                     "        transition accept;\n"
                     "		}\n\n")





def common_tables(fname, config):
    
    with open(fname, 'a') as ingress:
        ingress.write("    action ipv4_forward(mac_addr_t dstAddr, egressSpec_t port) {\n"
                      "        send(port);\n"
                      "        hdr.ethernet.src_addr = hdr.ethernet.dst_addr;\n"
                      "        hdr.ethernet.dst_addr = dstAddr;\n"
                      "        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;\n"
                      "    }\n\n"
                      "    table decision_mitigation {\n"
                      "        key = {\n"
                      "            hdr.ipv4.dst_addr: lpm;\n"
                      "            meta.result: exact;\n"
                      "        }\n"
                      "        actions={\n"
                      "            ipv4_forward;\n"
                      "            drop;\n"
                      "        }\n"
                      "        size = 1024;\n"
                      "        default_action = drop();\n"
                      "    }\n\n")





def common_logics(fname, config):
    with open(fname, 'a') as ingress:
        model_type = 'classification'
        try:
            model_type = config['model_type']
        except Exception as e:
            pass
        if model_type == 'classification':
            ingress.write("        hdr.Planter.result = meta.result;\n")
        else:
            for ax in range(0, config['num_axis']):
                ingress.write("        hdr.Planter.feature" + str(ax) + " = meta.feature" + str(ax) + ";\n")
        ingress.write("        /* Swap the MAC addresses */\n"
                      "        bit<48> tmp_MAC;\n"
                      "        tmp_MAC = hdr.ethernet.dst_addr;\n"
                      "        hdr.ethernet.dst_addr = hdr.ethernet.src_addr;\n"
                      "        hdr.ethernet.src_addr = tmp_MAC;\n"
                      "        /* Swap the IP addresses */\n"
                      "        bit<32> tmp_IP;\n"
                      "        tmp_IP = hdr.ipv4.dst_addr;\n"
                      "        hdr.ipv4.dst_addr = hdr.ipv4.src_addr;\n"
                      "        hdr.ipv4.src_addr = tmp_IP;\n"
                      "        send(ig_intr_md.ingress_port);\n")