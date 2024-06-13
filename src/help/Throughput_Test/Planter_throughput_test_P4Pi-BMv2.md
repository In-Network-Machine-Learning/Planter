# Planter throughput test: P4Pi-BMv2

<p align="center">
  <img src="https://raw.githubusercontent.com/p4lang/p4pi/master/docs/images/logo.png" width="200">
</p>
<aside>
💡 A guide to set up Planter on P4Pi-enabled BMv2. Heavily refer to the P4Pi wiki: https://github.com/p4lang/p4pi

</aside>



# ****Equipment****

## P4Pi

Configure P4Pi on the Raspberry Pi Platform with the [equipment](https://github.com/p4lang/p4pi/wiki/Required-Equipment) and [steps](https://github.com/p4lang/p4pi/wiki/Installing-P4Pi)  

1. Raspberry Pi 4 Model B - 4GB/8GB
2. Raspberry Pi 4 USB-C Power Supply
3. Micro SD Card 16GB/32GB

## Throughput test

1. Raspberry Pi/Laptop as client/server
2. Ethernet cables & USB to Gigabit Ethernet adapter for wired connection

# Basic setup

P4Pi [1] supports both T4P4S and BMv2 targets. We take BMv2 setup here as an example, Stoyanov. *et al.* [2] give the BMv2 architecture in P4Pi. Based on this architecture, the wired connection is set up as the Figure below. 

- Ethernet port of RPi (eth0 of P4Pi) connects to the Internet for SSH
- USB port with Ethernet adapter (eth1/eth2) connects to an RPi/laptop as server/client

* Note that, RPi and laptop are used as a sample server/client, they can be changed to other end devices. 
<p align="center">
  <img src="https://github.com/Changgang-Zheng/Planter-Working-Directory/blob/main/mingyuan/Planter%20throughput%20test%20P4Pi-BMv2/basicsetup.png" width="500"/>
</p>

# Basic connection & forwarding

- Setup static IP of 2 end devices (client/server) in the same subnet

Server: `ifconfig eth1 169.254.249.110 netmask 255.255.0.0`

Client: `ifconfig eth2 169.254.249.3 netmask 255.255.0.0`

- Setup static ARP in 2 end devices (`arp -s <ip> <mac>`)

Server: `arp -s 169.254.249.3 xx:xx:xx:xx:86:a3`

Client: `arp -s 169.254.249.110 xx:xx:xx:xx:9a:85`

- Setup static IP on P4Pi eth1/eth2 as gateways & configure the static routes

`ifconfig eth1 169.254.249.1 netmask 255.255.0.0`

`ifconfig eth2 169.254.249.11 netmask 255.255.0.0`

`route add -host 169.254.249.3/32 dev eth1`

`route add -host 169.254.249.110/32 dev eth2`

The routing table should have the two static rules: 

<p align="center">
  <img src="https://github.com/Changgang-Zheng/Planter-Working-Directory/blob/main/mingyuan/Planter%20throughput%20test%20P4Pi-BMv2/routes.png" width="500"/>
</p>

- Check if P4Pi can ping two end devices individually
- Run the JSON file after compiling the P4 program. The JSON file should be run with p4runtime thrift-port enabled

`root@p4pi:# simple_switch -i 0@eth1 -i 1@eth2 basic_forwarding.json`

or

`root@p4pi:/home/pi/bmv2/targets/simple_switch# ./simple_switch -i 0@eth1 -i 1@eth2 ~/basic_forwarding.json --thrift-port 9090`

- Open a new P4Pi SSH terminal and run runtime CLI with root (.py directly copy from bmv2 repo
/tools/runtime_CLI.py )

`root@p4pi:~# python3 runtime_CLI.py --thrift-port 9090`

or

`root@p4pi:/home/pi/bmv2/targets# simple_switch_CLI`

- Add two forward rules from runtime terminal:

`table_add MyIngress.ipv4_lpm MyIngress.ipv4_forward 169.254.249.3/32 => xx:xx:xx:xx:86:a3 0`

`table_add MyIngress.ipv4_lpm MyIngress.ipv4_forward 169.254.249.110/32 => xx:xx:xx:xx:9a:85 1`

# Planter configuration

## Performance mode

The performance mode is configured for a better performance of BMv2 target by following the [BMv2 guideline](https://github.com/p4lang/behavioral-model/blob/main/docs/performance.md) and [P4Pi-BMv2 guideline](https://github.com/p4lang/p4pi/tree/master/bmv2): 

BMv2 is not meant to be a production-grade software switch. So to get the best performance (highest throughput and lowest latency), do a fresh clone of bmv2 and run `./configure`
 with the following flags:

```bash
git clone https://github.com/p4lang/behavioral-model.git bmv2
cd bmv2
./install_deps.sh
./autogen.sh
./configure 'CXXFLAGS=-g -O3' 'CFLAGS=-g -O3' --disable-logging-macros --disable-elogger
make -j8
cd mininet
python stress_test_ipv4.py
```

* Note that it's "O" not 0 (zero) in CFLAGS
## Run Planter

Planter supports BMv2 target and provides the autogenerated P4 code for in-network ML model mapping. By selecting the BMv2 target and doing the compilation of autogenerated P4, a JSON file with the mapped ML model can be found in `./build` folder (e.g. `basic.json`), the M/A table rules can be found in `s1-commands.txt`

Run the Planter model from the data plane: 

`root@p4pi:/home/pi/bmv2/targets/simple_switch# ./simple_switch -i 0@eth1 -i 1@eth2 ~/basic.json --thrift-port 9090`

Run the following command in a new terminal to insert the table rules from the control plane:

`root@p4pi:/home/pi/bmv2/targets/simple_switch# ./simple_switch_CLI < ~/s1-commands.txt` 

## Throughput test

By referring to the [test script](https://github.com/p4lang/behavioral-model/blob/main/mininet/stress_test_ipv4.py.in), the throughput tests can be set by: 

Run iperf server on RPi (169.254.249.110):

`iperf -s`

Run iperf client on laptop (169.254.249.3):

`iperf -f m -c 169.254.249.110 -t 30`

# References

[1] Sándor Laki, Radostin Stoyanov, Dávid Kis, Robert Soulé, Péter Vörös, and Noa Zilberman. 2021. P4Pi: P4 on Raspberry Pi for networking education. *SIGCOMM Comput. Commun. Rev.* 51, 3 (July 2021), 17–21. DOI:[https://doi.org/10.1145/3477482.3477486](https://doi.org/10.1145/3477482.3477486)

[2] Radostin Stoyanov, Adam Wolnikowski, Robert Soulé, Sándor Laki, and Noa Zilberman. 2021. Building an Internet Router with P4Pi. In *Proceedings of the Symposium on Architectures for Networking and Communications Systems* (*ANCS '21*). Association for Computing Machinery, New York, NY, USA, 151–156. DOI:[https://doi.org/10.1145/3493425.3502762](https://doi.org/10.1145/3493425.3502762)