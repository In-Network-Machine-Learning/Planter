/*
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

*/
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
#include <xsa.p4>

/*************************************************************************
*********************** headers and metadata *****************************
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

header Planter_prefix_h{
    bit<8> p;
    bit<8> four;
    bit<8> ver;
    bit<8> typ;
}

header Planter_h{
    bit<32> feature0;
    bit<32> feature1;
    bit<32> feature2;
    bit<32> feature3;
    bit<32> result;
}

struct header_t {
    ethernet_h   ethernet;
    Planter_prefix_h Planter_prefix;
    Planter_h    Planter;
}

struct metadata_t {
   bit<64> timestamp_ns;
   bit<16> pid;
   bit<3> ingress_port;
   bit<3> egress_port;
   bit<1> truncate_enable;
   bit<16> truncate_length;
   bit<1> rss_enable;
   bit<12> rss_entropy;
   bit<4> drop_reason;
   bit<32> scratch;
}

/*************************************************************************
*********************** Ingress Parser ***********************************
*************************************************************************/

parser SwitchParser(
    packet_in pkt,
    out header_t hdr,
    inout metadata_t meta,
    inout standard_metadata_t ig_intr_md) {

    state start {
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
        pkt.extract(hdr.Planter_prefix);
        transition select(hdr.Planter_prefix.p,
                           hdr.Planter_prefix.four,
                           hdr.Planter_prefix.ver) {
        (Planter_P, Planter_4, Planter_VER) : parse_planter;
        default                             : accept;
        }
    }

    state parse_planter {
        pkt.extract(hdr.Planter);
        transition accept;
    }
}

/*************************************************************************
*********************** Egress Deparser *********************************
**************************************************************************/

control SwitchDeparser(
    packet_out pkt,
    in header_t hdr,
    inout metadata_t meta,
    inout standard_metadata_t ig_intr_md) {
    apply {
        pkt.emit(hdr);
    }
}

/*************************************************************************
*********************** Processing********************************
**************************************************************************/

control SwitchProcessing(
    inout header_t hdr,
    inout metadata_t meta,
    inout standard_metadata_t ig_intr_md) {

    bit<10> code_f0;
    bit<10> code_f1;
    bit<10> code_f2;
    bit<10> code_f3;
    bit<7> sum_prob;
    bit<16> flag = 1;
    action drop() {
        ig_intr_md.drop=1;
    }

    action extract_feature0(out bit<10> meta_code, bit<10> tree){
        meta_code = tree;
    }

    action extract_feature1(out bit<10> meta_code, bit<10> tree){
        meta_code = tree;
    }

    action extract_feature2(out bit<10> meta_code, bit<10> tree){
        meta_code = tree;
    }

    action extract_feature3(out bit<10> meta_code, bit<10> tree){
        meta_code = tree;
    }

    action read_lable(bit<32> label){
        hdr.Planter.result = label;
    }

    table lookup_feature0 {
        key = { hdr.Planter.feature0:exact; }
        actions = {
        extract_feature0(code_f0);
            NoAction;
            }
        size = 80;
        default_action = NoAction;
    }

    table lookup_feature1 {
        key = { hdr.Planter.feature1:exact; }
        actions = {
        extract_feature1(code_f1);
            NoAction;
            }
        size = 45;
        default_action = NoAction;
    }

    table lookup_feature2 {
        key = { hdr.Planter.feature2:exact; }
        actions = {
        extract_feature2(code_f2);
            NoAction;
            }
        size = 70;
        default_action = NoAction;
    }

    table lookup_feature3 {
        key = { hdr.Planter.feature3:exact; }
        actions = {
        extract_feature3(code_f3);
            NoAction;
            }
        size = 26;
        default_action = NoAction;
    }

    table decision {
        key = {
            code_f0:exact;
            code_f1:exact;
            code_f2:exact;
            code_f3:exact;
        }
        actions={read_lable;}
        size = 24;
    }

    apply{
        lookup_feature0.apply();
        lookup_feature1.apply();
        lookup_feature2.apply();
        lookup_feature3.apply();
        decision.apply();
        bit<48> tmp;
        /* Swap the MAC addresses */
        tmp = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = hdr.ethernet.srcAddr;
        hdr.ethernet.srcAddr = tmp;
    }
}
/*************************************************************************
***********************  S W I T C H  ************************************
*************************************************************************/

XilinxPipeline(
    SwitchParser(),
    SwitchProcessing(),
    SwitchDeparser()
) main;