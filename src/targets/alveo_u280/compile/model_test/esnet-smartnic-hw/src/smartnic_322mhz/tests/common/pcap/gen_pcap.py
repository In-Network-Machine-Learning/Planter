#!/usr/bin/python
import string
import random

from scapy.all import *

#----------------------------------------------------------------
l2 = Ether(dst="01:02:03:04:05:06", src="07:08:09:0A:0B:0C")
l3 = IP(dst='lbl.gov/27',src='es.net/28') # 512 pkts
l4 = TCP(sport=1024,dport=2048)

payload = ''
for i in range(10): payload += random.choice(string.ascii_lowercase) # 64B pkt

pkts = []
pkts += l2/l3/l4/Raw(load=payload)
wrpcap("512x64B_pkts.pcap", pkts)


#----------------------------------------------------------------
l2 = Ether(dst="01:02:03:04:05:06", src="07:08:09:0A:0B:0C")
l3 = IP(dst='lbl.gov/28',src='es.net/28') # 256 pkts
l4 = TCP(sport=1024,dport=2048)

payload = ''
for i in range(512): payload += random.choice(string.ascii_lowercase) # 566B pkt

pkts = []
pkts += l2/l3/l4/Raw(load=payload)
wrpcap("256x566B_pkts.pcap", pkts)


#----------------------------------------------------------------
l2 = Ether(dst="01:02:03:04:05:06", src="07:08:09:0A:0B:0C")
l3 = IP(dst='lbl.gov/29',src='es.net/28') # 128 pkts
l4 = TCP(sport=1024,dport=2048)

payload = ''
for i in range(1464): payload += random.choice(string.ascii_lowercase) # 1518B pkt

pkts = []
pkts += l2/l3/l4/Raw(load=payload)

wrpcap("128x1518B_pkts.pcap", pkts)


#----------------------------------------------------------------
l2 = Ether(dst="01:02:03:04:05:06", src="07:08:09:0A:0B:0C")
l3 = IP(dst='lbl.gov/29',src='es.net/28') # 128 pkts
l4 = TCP(sport=1024,dport=2048)

payload = ''
for i in range(1364): payload += random.choice(string.ascii_lowercase) # 1418B pkt

pkts = []
pkts += l2/l3/l4/Raw(load=payload)

wrpcap("128x1418B_pkts.pcap", pkts)


#----------------------------------------------------------------
l2 = Ether(dst="01:02:03:04:05:06", src="07:08:09:0A:0B:0C")
l3 = IP(dst='lbl.gov/29',src='es.net/28') # 128 pkts
l4 = TCP(sport=1024,dport=2048)

payload = ''
for i in range(1264): payload += random.choice(string.ascii_lowercase) # 1318B pkt

pkts = []
pkts += l2/l3/l4/Raw(load=payload)

wrpcap("128x1318B_pkts.pcap", pkts)


#----------------------------------------------------------------
l2 = Ether(dst="01:02:03:04:05:06", src="07:08:09:0A:0B:0C")
l3 = IP(dst='lbl.gov/29',src='es.net/28') # 128 pkts
l4 = TCP(sport=1024,dport=2048)

payload = ''
for i in range(1164): payload += random.choice(string.ascii_lowercase) # 1218B pkt

pkts = []
pkts += l2/l3/l4/Raw(load=payload)

wrpcap("128x1218B_pkts.pcap", pkts)


#----------------------------------------------------------------
l2 = Ether(dst="01:02:03:04:05:06", src="07:08:09:0A:0B:0C")
l3 = IP(dst='lbl.gov/30',src='es.net/29') # 32 pkts
l4 = TCP(sport=1024,dport=2048)

payload = ''
for i in range(9046): payload += random.choice(string.ascii_lowercase) # 9000B pkt

pkts = []
pkts += l2/l3/l4/Raw(load=payload)

wrpcap("32x9100B_pkts.pcap", pkts)


#----------------------------------------------------------------
l2 = Ether(dst="01:02:03:04:05:06", src="07:08:09:0A:0B:0C")
l3 = IP(dst='lbl.gov/28',src='es.net/28') # 256 pkts
l4 = TCP(sport=1024,dport=2048)

payload = ''

pkts = []
pkts += l2/l3/l4/Raw(load=payload)

wrpcap("256x54B_pkts.pcap", pkts)


#----------------------------------------------------------------
l2 = Ether(dst="01:02:03:04:05:06", src="07:08:09:0A:0B:0C")
l3 = IP(dst='lbl.gov',src='es.net')
l4 = TCP(sport=1024,dport=2048)

payload_size=10

pkts = []
for i in range(256):
    payload = ''
    for j in range(payload_size+i): payload += random.choice(string.ascii_lowercase)
    pkts += l2/l3/l4/Raw(load=payload)

wrpcap("64B_to_319B_pkts.pcap", pkts)


#----------------------------------------------------------------
l2 = Ether(dst="01:02:03:04:05:06", src="07:08:09:0A:0B:0C")
l3 = IP(dst='lbl.gov',src='es.net')
l4 = TCP(sport=1024,dport=2048)

payload_size=10

pkts = []
for i in range(10):
    payload = ''
    for j in range(payload_size+i*64): payload += random.choice(string.ascii_lowercase)
    pkts += l2/l3/l4/Raw(load=payload)

wrpcap("64B_multiples_10pkts.pcap", pkts)


#----------------------------------------------------------------
l2 = Ether(dst="01:02:03:04:05:06", src="07:08:09:0A:0B:0C")
l3 = IP(dst='lbl.gov',src='es.net')
l4 = TCP(sport=1024,dport=2048)

pkts = []
for i in range(10):
    payload_size = random.randrange(10,1464)
    payload = ''
    for j in range(payload_size): payload += random.choice(string.ascii_lowercase)
    pkts += l2/l3/l4/Raw(load=payload)

wrpcap("10xrandom_pkts.pcap", pkts)


#----------------------------------------------------------------
l2 = Ether(dst="01:02:03:04:05:06", src="07:08:09:0A:0B:0C")
l3 = IP(dst='lbl.gov',src='es.net')
l4 = TCP(sport=1024,dport=2048)

pkts = []
for i in range(20):
    payload_size = random.randrange(10,1464)
    payload = ''
    for j in range(payload_size): payload += random.choice(string.ascii_lowercase)
    pkts += l2/l3/l4/Raw(load=payload)

wrpcap("20xrandom_pkts.pcap", pkts)


#----------------------------------------------------------------
l2 = Ether(dst="01:02:03:04:05:06", src="07:08:09:0A:0B:0C")
l3 = IP(dst='lbl.gov',src='es.net')
l4 = TCP(sport=1024,dport=2048)

pkts = []
for i in range(30):
    payload_size = random.randrange(10,1464)
    payload = ''
    for j in range(payload_size): payload += random.choice(string.ascii_lowercase)
    pkts += l2/l3/l4/Raw(load=payload)

wrpcap("30xrandom_pkts.pcap", pkts)


#----------------------------------------------------------------
l2 = Ether(dst="01:02:03:04:05:06", src="07:08:09:0A:0B:0C")
l3 = IP(dst='lbl.gov',src='es.net')
l4 = TCP(sport=1024,dport=2048)

pkts = []
for i in range(40):
    payload_size = random.randrange(10,1464)
    payload = ''
    for j in range(payload_size): payload += random.choice(string.ascii_lowercase)
    pkts += l2/l3/l4/Raw(load=payload)

wrpcap("40xrandom_pkts.pcap", pkts)


#----------------------------------------------------------------
l2 = Ether(dst="01:02:03:04:05:06", src="07:08:09:0A:0B:0C")
l3 = IP(dst='lbl.gov',src='es.net')
l4 = TCP(sport=1024,dport=2048)

pkts = []
for i in range(50):
    payload_size = random.randrange(10,1464)
    payload = ''
    for j in range(payload_size): payload += random.choice(string.ascii_lowercase)
    pkts += l2/l3/l4/Raw(load=payload)

wrpcap("50xrandom_pkts.pcap", pkts)


#----------------------------------------------------------------
l2 = Ether(dst="01:02:03:04:05:06", src="07:08:09:0A:0B:0C")
l3 = IP(dst='lbl.gov',src='es.net')
l4 = TCP(sport=1024,dport=2048)

pkts = []
for i in range(100):
    payload_size = random.randrange(10,1464)
    payload = ''
    for j in range(payload_size): payload += random.choice(string.ascii_lowercase)
    pkts += l2/l3/l4/Raw(load=payload)

wrpcap("100xrandom_pkts.pcap", pkts)
