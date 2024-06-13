#!/bin/bash
in_size=$(wc -c <"packets_in.pcap")
out_size=$(wc -c <"packets_out.pcap")

if [ $out_size == $in_size ]; then
    exit 0;
else
    echo "ERROR: Mismatch in number of packet records contained in input/output PCAP files. Expect all packets to be accepted."
    exit 1;
fi

