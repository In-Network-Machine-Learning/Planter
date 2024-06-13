#!/usr/bin/python
import random

from scapy.all import *

#----------------------------------------------------------------
l2 = Ether(dst="00:80:C2:00:00:00", src="00:80:C2:FF:FF:FF")

payload = ''
for i in range(498): payload += chr(random.randrange(0,256)) # 512B pkt

pkts = []
pkts += l2/Raw(payload)

l2 = Ether(dst="00:80:C2:00:00:01", src="00:80:C2:FF:FF:FF")
pkts += l2/Raw(payload)

l2 = Ether(dst="00:80:C2:00:00:02", src="00:80:C2:FF:FF:FF")
pkts += l2/Raw(payload)

l2 = Ether(dst="00:80:C2:00:00:03", src="00:80:C2:FF:FF:FF")
pkts += l2/Raw(payload)

wrpcap("packets_in.pcap", pkts)  # pcap with 4x512B pkts, each differing only by Ethernet dstAddr.

#----------------------------------------------------------------
