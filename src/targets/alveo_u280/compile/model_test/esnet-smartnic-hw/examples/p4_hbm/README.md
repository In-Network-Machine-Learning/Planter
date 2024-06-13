# Example Design: p4_hbm

The p4_hbm example design provides the P4 source code and a behavioural simulation testcase for a
P4 application core that leverages the integrated HBM (high-bandwidth memory) to implement a large (1M)
IPv4/IPv6 filter.

This example follows a pure P4 design flow and does NOT include any custom verilog hardware.  As such,
the user only provides the working P4 program file to build the custom SmartNIC hardware.



## Functional Specification

The p4_hbm design implements a simple table-based IPv4/IPv6 dest address filter.  It uses a single exact-match
table that takes the IP dest address (both v4 and v6 supported) as a key. The filter table is implemented in
HBM and can store up to 1M entries.

The table can be configured to either DROP packets that match in the filter table, or specify a FORWARD rule (selecting
a destination port). The default action (for packets that don't have an entry in the table, or non-IP packets) is to take no action,
and the packet will be forwarded as specified by its input metadata.

Packets with invalid and errored Ethernet headers are dropped.



## Development Flow

The sections below direct the user to:

1. Install the SmartNIC platform design repositories
2. Execute a P4 behavioural simulation (to verify P4 program correctness ahead of building hardware).
3. Build the P4-based custom SmartNIC hardware.


### Installing the SmartNIC Repositories

Refer to the `Getting Started` section of the `esnet-smartnic-hw/README.md` file:
https://github.com/esnet/esnet-smartnic-hw#readme


### Simulating the P4 program

Refer to instructions in the `esnet-smartnic-hw/examples/p4_only/p4/sim/README.md` file.


### Building the SmartNIC hardware design

Refer to the `Getting Started` section of the `esnet-smartnic-hw/README.md` file:
https://github.com/esnet/esnet-smartnic-hw#readme


**NOTE: See lower level README files for more details.**



# Known Issues

- None to date.
