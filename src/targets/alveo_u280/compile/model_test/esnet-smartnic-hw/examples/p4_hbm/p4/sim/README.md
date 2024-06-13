# P4 Behavioural Simulation

The execution of P4 behavioural simulations is driven by the Makefile
in the p4/sim/ directory.

This Makefile includes the variable assignments that specify how to run
a p4 behavioural simulation, as well as the list of testcases that should
be included in a full simulation run.

Each testcase is captured in a separate subdirectory, which contains the
input and output files for the specified test.  The testcase subdirectories
follow the naming pattern of `test-<NAME>`.

The Makefile includes execution targets to run (or clean) a single testcase
simulation, or simulation of the full testcase suite.

To simulate a single testcase, execute make with the `P4BM_DIR=` argument
set to the testcase subdirectory of interest.  For example:

     > make P4BM_DIR=test-fwd-p0

Or to simulate all test cases:

     > make sim-all

Note: the `sim-all` target is the default target when make is called without
arguments.

To clean all simulation output products from the p4 directory, type:

     > make clean


## Testcase Input Files

The input stimulus file set for each testcase includes three files:

`runsim.txt` - Command script to set table entries and initiate input
stimulus. Commands and syntax follow the Xilinx p4bm-vitisnet-cli.

`packets_in.pcap` - PCAP file containing the input packet stream.

`packets_in.meta` - Input packet metadata.  Each line corresponds
to a packet in the input PCAP file (in sequence).  The syntax of the metadata
is described in the Xilinx VitisnetP4 documentation.  Note: Each metadata record
must be terminated by a semicolon (;).


## Testcase Output Files

`packets_out.pcap` - PCAP file containing the output packet stream.

`packets_out.meta` - Output packet metadata.  Each line corresponds
to a packet in the output PCAP file (in sequence).  Same syntax as input
packet metadata.

Note: An expected/ directory is optionally included to capture the expected
output results of a testcase.  This expected output can be used for
automated regression testing.


## Testcases: p4_hbm

`test-fwd-p0` - The p4_hbm design includes a single example testcase called
test-fwd-p0.  This testcase programs a small number of table entries that
forward the specified packet flows to destination port 0.  The input
stimulus includes a single packet on each flow to validate that all packets
are forwarded to port 0.
