#!/bin/bash
in_size=$(wc -c <"packets_in.pcap")
out_size=$(wc -c <"packets_out.pcap")

if [ $out_size == 24 ]; then
    exit 0;
else
    echo "ERROR: Output file contains one or more packet records; expected all packets to be dropped."
    exit 1;
fi

