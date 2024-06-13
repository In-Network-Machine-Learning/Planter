#include <core.p4>
#include <xsa.p4>

// ****************************************************************************** //
// *************************** H E A D E R S  *********************************** //
// ****************************************************************************** //

header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}

header vlan_t {
    bit<3>  pcp;
    bit<1>  cfi;
    bit<12> vid;
    bit<16> etherType;
}

header ipv4_t {
    bit<4>  version;
    bit<4>  ihl;
    bit<8>  diffserv;
    bit<16> totalLen;
    bit<16> identification;
    bit<3>  flags;
    bit<13> fragOffset;
    bit<8>  ttl;
    bit<8>  protocol;
    bit<16> hdrChecksum;
    bit<32> srcAddr;
    bit<32> dstAddr;
}

header ipv6_t {
    bit<4>   version;
    bit<8>   trafficClass;
    bit<20>  flowLabel;
    bit<16>  payloadLen;
    bit<8>   nextHdr;
    bit<8>   hopLimit;
    bit<128> srcAddr;
    bit<128> dstAddr;
}

// ****************************************************************************** //
// ************************* S T R U C T U R E S  ******************************* //
// ****************************************************************************** //

struct headers {
    ethernet_t       ethernet;
    vlan_t           vlan_0;
    vlan_t           vlan_1;
    ipv4_t           ipv4;
    ipv6_t           ipv6;
}

struct smartnic_metadata {
    bit<64> timestamp_ns;    // 64b timestamp (in nanoseconds). Set at packet arrival time.
    bit<16> pid;             // 16b packet id used by platform (READ ONLY - DO NOT EDIT).
    bit<3>  ingress_port;    // 3b ingress port (0:CMAC0, 1:CMAC1, 2:HOST0, 3:HOST1).
    bit<3>  egress_port;     // 3b egress port  (0:CMAC0, 1:CMAC1, 2:HOST0, 3:HOST1).
    bit<1>  truncate_enable; // reserved (tied to 0).
    bit<16> truncate_length; // reserved (tied to 0).
    bit<1>  rss_enable;      // reserved (tied to 0).
    bit<12> rss_entropy;     // reserved (tied to 0).
    bit<4>  drop_reason;     // reserved (tied to 0).
    bit<32> scratch;         // reserved (tied to 0).
}

struct filter_key_t {
    bit      ipv6;
    bit<128> dstAddr;
}

// User-defined errors 
error {
    InvalidIPpacket
    
}

// ****************************************************************************** //
// *************************** P A R S E R  ************************************* //
// ****************************************************************************** //

parser ParserImpl( packet_in packet,
                   out headers hdr,
                   inout smartnic_metadata   sn_meta,
                   inout standard_metadata_t smeta) {
    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            16w0x8100: parse_vlan_0; // 802.1q C-tag
            16w0x88a8: parse_vlan_0; // 802.1ad S-tag for Q-in-Q
            16w0x9100: parse_vlan_0; // 802.1q double-tagging
            16w0x9200: parse_vlan_0;
            16w0x9300: parse_vlan_0;
            16w0x800: parse_ipv4;
            16w0x86dd: parse_ipv6;
            default: accept;
        }
    }

    state parse_vlan_0 {
        packet.extract(hdr.vlan_0);
        transition select(hdr.vlan_0.etherType) {
            16w0x8100: parse_vlan_1;
            16w0x9100: parse_vlan_1;
            16w0x9200: parse_vlan_1;
            16w0x9300: parse_vlan_1;
            16w0x800: parse_ipv4;
            16w0x86dd: parse_ipv6;
            default: accept;
        }
    }

    state parse_vlan_1 {
        packet.extract(hdr.vlan_1);
        transition select(hdr.vlan_1.etherType) {
            16w0x800: parse_ipv4;
            16w0x86dd: parse_ipv6;
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
	verify(hdr.ipv4.version == 4 && hdr.ipv4.ihl >= 5, error.InvalidIPpacket);
        transition accept;
    }

    state parse_ipv6 {
        packet.extract(hdr.ipv6);
        verify(hdr.ipv6.version == 6, error.InvalidIPpacket);
        transition accept;
    }
}

// ****************************************************************************** //
// **************************  P R O C E S S I N G   **************************** //
// ****************************************************************************** //

control MatchActionImpl( inout headers hdr,
                         inout smartnic_metadata   sn_meta,
                         inout standard_metadata_t smeta) {

    // Data structures
    filter_key_t filter_key;

    action forwardPacket(bit<3> dest_port) {
        sn_meta.egress_port = dest_port;
    }
    
    action dropPacket() {
        smeta.drop = 1;
    }

    table filter {
        key     = { filter_key.ipv6 : exact; filter_key.dstAddr : exact;}
        actions = { forwardPacket; 
                    dropPacket;
                    NoAction; }
        size    = 1048576;
        default_action = NoAction;
    }

    apply {
        if (smeta.parser_error != error.NoError) {
            dropPacket();
            return;
        }
        
        if (hdr.ethernet.isValid() && (hdr.ipv4.isValid() || hdr.ipv6.isValid())) {
            filter_key.ipv6 = 0;
            filter_key.dstAddr = 0;
            if (hdr.ipv4.isValid()) {
                filter_key.dstAddr = 96w0 ++ hdr.ipv4.dstAddr;
            }
            else if (hdr.ipv6.isValid()) {
                filter_key.ipv6 = 1;
                filter_key.dstAddr = hdr.ipv6.dstAddr;
            }
            filter.apply();
        }
        // Default ACTION is ACCEPT (forward to port specified by input metadata)
    }
}

// ****************************************************************************** //
// ***************************  D E P A R S E R  ******************************** //
// ****************************************************************************** //

control DeparserImpl( packet_out packet,
                      in headers hdr,
                      inout smartnic_metadata   sn_meta,
                      inout standard_metadata_t smeta) {
    apply {
        packet.emit(hdr);
    }
}

// ****************************************************************************** //
// *******************************  M A I N  ************************************ //
// ****************************************************************************** //

XilinxPipeline(
    ParserImpl(), 
    MatchActionImpl(), 
    DeparserImpl()
) main;
