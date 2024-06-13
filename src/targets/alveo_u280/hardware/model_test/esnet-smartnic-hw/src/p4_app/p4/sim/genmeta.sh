#! /bin/sh
#
# Quick script to generate a metadata file for p4bm-sdnet.
#
# Invoke as:
#   % ./genmeta.sh 100 > packets_in.meta
#

count=$1

meta=smartnic_metadata

for i in `seq $count`; do
    echo "${meta}.ingress_global_timestamp=`printf %04x ${i}` ${meta}.egress_spec=0000 ${meta}.processed=01 ${meta}.packet_length=00a6 ;"
done
