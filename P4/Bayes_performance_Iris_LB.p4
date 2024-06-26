########################################################################
# THIS FILE IS PART OF Planter PROJECT
# Copyright (c) Changgang Zheng and Computing Infrastructure Group
# Department of Engineering Science, University of Oxford
# All rights reserved.
# E-mail: changgang.zheng@eng.ox.ac.uk or changgangzheng@qq.com
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at :
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#########################################################################
# This file was autogenerated

/*
 * Planter
 *
 * This program implements a simple protocol. It can be carried over Ethernet
 * (Ethertype 0x1234).
 *
 * The Protocol header looks like this:
 *
 *        0                1                  2              3
 * +----------------+----------------+----------------+---------------+
 * |      P         |       4        |     Version    |     Type      |
 * +----------------+----------------+----------------+---------------+
 * |                              feature0                            |
 * +----------------+----------------+----------------+---------------+
 * |                              feature1                            |
 * +----------------+----------------+----------------+---------------+
 * |                              feature2                            |
 * +----------------+----------------+----------------+---------------+
 * |                              feature3                            |
 * +----------------+----------------+----------------+---------------+
 * |                              Result                              |
 * +----------------+----------------+----------------+---------------+
 *
 * P is an ASCII Letter 'P' (0x50)
 * 4 is an ASCII Letter '4' (0x34)
 * Version is currently 1 (0x01)
 * Type is currently 1 (0x01)
 *
 * The device receives a packet, do the classification, fills in the
 * result and sends the packet back out of the same port it came in on, while
 * swapping the source and destination addresses.
 *
 * If an unknown operation is specified or the header is not valid, the packet
 * is dropped
 */

#include <core.p4>
#include <tna.p4>

/*************************************************************************
*********************** headers and metadata******************************
*************************************************************************/

const bit<16> ETHERTYPE_Planter = 0x1234;
const bit<8>  Planter_P     = 0x50;   // 'P'
const bit<8>  Planter_4     = 0x34;   // '4'
const bit<8>  Planter_VER   = 0x01;   // v0.1

header ethernet_h {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}

header Planter_h{
    bit<8> p;
    bit<8> four;
    bit<8> ver;
    bit<8> typ;
    bit<32> feature0;
    bit<32> feature1;
    bit<32> feature2;
    bit<32> feature3;
    bit<32> result;
}

struct header_t {
    ethernet_h   ethernet;
    Planter_h    Planter;
}

struct metadata_t {
    bit<32> prob_c0;
    bit<32> prob_c1;
    bit<32> prob_c2;
    bit<32> compare0_1;
    bit<32> compare0_2;
    bit<32> compare1_2;
    bit<32> feature0;
    bit<32> feature1;
    bit<32> feature2;
    bit<32> feature3;
    bit<32> result;
    bit<8> flag ;
}

/*************************************************************************
*********************** Ingress Parser ***********************************
*************************************************************************/

parser SwitchIngressParser(
    packet_in pkt,
    out header_t hdr,
    out metadata_t meta,
    out ingress_intrinsic_metadata_t ig_intr_md) {

    state start {
        pkt.extract(ig_intr_md);
        pkt.advance(PORT_METADATA_SIZE);
        transition parse_ethernet;
    }

    state parse_ethernet {
        pkt.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
        ETHERTYPE_Planter : check_planter_version;
        default           : accept;
        }
    }

    state check_planter_version {
        transition select(pkt.lookahead<Planter_h>().p,
                          pkt.lookahead<Planter_h>().four,
                          pkt.lookahead<Planter_h>().ver) {
        (Planter_P, Planter_4, Planter_VER) : parse_planter;
        default                             : accept;
        }
    }

    state parse_planter {
        pkt.extract(hdr.Planter);
        meta.feature0 = hdr.Planter.feature0;
        meta.feature1 = hdr.Planter.feature1;
        meta.feature2 = hdr.Planter.feature2;
        meta.feature3 = hdr.Planter.feature3;
        meta.flag = 1 ;
        transition accept;
    }
}

/*************************************************************************
*********************** Ingress Deparser *********************************
**************************************************************************/

control SwitchIngressDeparser(
    packet_out pkt,
    inout header_t hdr,
    in metadata_t ig_md,
    in ingress_intrinsic_metadata_for_deparser_t ig_dprsr_md) {
    apply {
        pkt.emit(hdr);
    }
}

/*************************************************************************
*********************** Egress Parser ***********************************
*************************************************************************/

parser SwitchEgressParser(
    packet_in pkt,
    out header_t hdr,
    out metadata_t meta,
    out egress_intrinsic_metadata_t eg_intr_md) {
    state start {
        pkt.extract(eg_intr_md);
        transition accept;
        }

}

/*************************************************************************
*********************** Egress Deparser *********************************
**************************************************************************/

control SwitchEgressDeparser(
    packet_out pkt,
    inout header_t hdr,
    in metadata_t eg_md,
    in egress_intrinsic_metadata_for_deparser_t eg_dprsr_md) {
    apply {
        pkt.emit(hdr);
    }
}

/*************************************************************************
*********************** Ingress Processing********************************
**************************************************************************/

control SwitchIngress(
    inout header_t hdr,
    inout metadata_t meta,
    in ingress_intrinsic_metadata_t ig_intr_md,
    in ingress_intrinsic_metadata_from_parser_t ig_prsr_md,
    inout ingress_intrinsic_metadata_for_deparser_t ig_dprsr_md,
    inout ingress_intrinsic_metadata_for_tm_t ig_tm_md) {

    action drop() {
        ig_dprsr_md.drop_ctl = 0x1;
    }

    action send(PortId_t port) {
        ig_tm_md.ucast_egress_port = port;
    }

    action extract_feature0(bit<32> f0c0, bit<32> f0c1, bit<32> f0c2){
        meta.prob_c0 = meta.prob_c0 + f0c0;
        meta.prob_c1 = meta.prob_c1 + f0c1;
        meta.prob_c2 = meta.prob_c2 + f0c2;
    }

    action extract_feature1(bit<32> f1c0, bit<32> f1c1, bit<32> f1c2){
        meta.prob_c0 = meta.prob_c0 + f1c0;
        meta.prob_c1 = meta.prob_c1 + f1c1;
        meta.prob_c2 = meta.prob_c2 + f1c2;
    }

    action extract_feature2(bit<32> f2c0, bit<32> f2c1, bit<32> f2c2){
        meta.prob_c0 = meta.prob_c0 + f2c0;
        meta.prob_c1 = meta.prob_c1 + f2c1;
        meta.prob_c2 = meta.prob_c2 + f2c2;
    }

    action extract_feature3(bit<32> f3c0, bit<32> f3c1, bit<32> f3c2){
        meta.prob_c0 = meta.prob_c0 + f3c0;
        meta.prob_c1 = meta.prob_c1 + f3c1;
        meta.prob_c2 = meta.prob_c2 + f3c2;
    }

    table lookup_feature0 {
        key = { hdr.Planter.feature0:exact; }
        actions = {
            extract_feature0();
            NoAction;
            }
        size = 81;
        default_action = NoAction;
    }

    table lookup_feature1 {
        key = { hdr.Planter.feature1:exact; }
        actions = {
            extract_feature1();
            NoAction;
            }
        size = 46;
        default_action = NoAction;
    }

    table lookup_feature2 {
        key = { hdr.Planter.feature2:exact; }
        actions = {
            extract_feature2();
            NoAction;
            }
        size = 71;
        default_action = NoAction;
    }

    table lookup_feature3 {
        key = { hdr.Planter.feature3:exact; }
        actions = {
            extract_feature3();
            NoAction;
            }
        size = 27;
        default_action = NoAction;
    }

    action read_class_prob(bit<32> p_c0, bit<32> p_c1, bit<32> p_c2){
        meta.prob_c0 = p_c0;
        meta.prob_c1 = p_c1;
        meta.prob_c2 = p_c2;
    }

    table class_prob {
        key = {hdr.Planter.ver:exact;}
        actions={read_class_prob; NoAction;}
        default_action = NoAction;
        size = 1;
    }

    action compare(){
        meta.compare0_1 = meta.prob_c0 - meta.prob_c1;
        meta.compare1_2 = meta.prob_c1 - meta.prob_c2;
        meta.compare0_2 = meta.prob_c0 - meta.prob_c2;
    }

    apply{
        class_prob.apply();
        lookup_feature0.apply();
        lookup_feature1.apply();
        lookup_feature2.apply();
        lookup_feature3.apply();
        compare();

        if(meta.compare0_1& 0b10000000000000000000000000000000!=0){
            if(meta.compare1_2& 0b10000000000000000000000000000000!=0){
                 hdr.Planter.result = 2;
             }
            else{
                 hdr.Planter.result = 1;
             }
        }
        else{
            if(meta.compare0_2& 0b10000000000000000000000000000000!=0){
                 hdr.Planter.result = 2;
             }
            else{
                 hdr.Planter.result = 0;
             }
        }
        send(ig_intr_md.ingress_port);
    }
}
/*************************************************************************
*********************** egress Processing********************************
**************************************************************************/

control SwitchEgress(inout header_t hdr,
    inout metadata_t meta,
    in egress_intrinsic_metadata_t eg_intr_md,
    in egress_intrinsic_metadata_from_parser_t eg_prsr_md,
    inout egress_intrinsic_metadata_for_deparser_t     eg_dprsr_md,
    inout egress_intrinsic_metadata_for_output_port_t  eg_oport_md) {

    action drop() {
        eg_dprsr_md.drop_ctl = 0x1;
    }

    apply {
    }
}
/*************************************************************************
***********************  S W I T C H  ************************************
*************************************************************************/

Pipeline(SwitchIngressParser(),
    SwitchIngress(),
    SwitchIngressDeparser(),
    SwitchEgressParser(),
    SwitchEgress(),
    SwitchEgressDeparser()) pipe;

Switch(pipe) main;