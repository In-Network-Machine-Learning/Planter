Setting up the Runtime Environment
==================================

The smartnic runtime environment also requires `docker` and `docker compose` as described in README.md at the top of this repo.

Set up Xilinx Labtools
----------------------

In order to load a smartnic FPGA bitfile into the Xilinx U280 card, we need to make use of the Xilinx Labtools.  The instructions for setting up labtools can be found in a separate repository.  That repository will provide us with a docker container populated with the xilinx labtools.  That docker container will be used to program the FPGA bitfile.

Running the firmware
--------------------

The firmware artifact produced by the build (see README.md at the top of this repo) should be transferred to the runtime system that hosts an FPGA card.

```
unzip artifacts.esnet-smartnic-fw.package_focal.user.001.zip
cd sn-stack
cp example.env .env
# edit the .env file to provide sane values for
#    FPGA_PCIE_DEV=0000:d8:00
# and IFF you have more than one JTAG you also need a line like this
#    HW_TARGET_SERIAL=21760204S029A
docker compose build
docker compose up -d
```

Verify that the stack is running like this

```
docker compose ps
```

Verifying the bitfile download
------------------------------

```
docker compose logs smartnic-hw
```

Writing the bitfile to the FPGA card persistent flash (Optional)
----------------------------------------------------------------

Ensure that any running `sn-stack` instances have been stopped so that they don't interfere with the flash programming operation.

```
docker compose down -v
```

Start up the separate flash-programming service like this

```
docker compose -f docker-compose-flash.yml run --rm smartnic-flash
```

This will:
* Use JTAG to write a small flash-programing helper bitfile into the FPGA
* Use JTAG to write the current version of the bitfile into the U280 card's flash
  * Only the "user" partition of the flash is overwritten by this step
  * The "gold" partition is left untouched

**Note:** the flash programming sequence takes about 19 minutes to complete.

Inspecting registers and interacting with the firmware
------------------------------------------------------

The firmware runtime environment exists inside of the `smartnic-fw` container.  Here, we exec a shell inside of that container and have a look around.

```
docker compose exec smartnic-fw bash
sn-cli dev version
regio syscfg
```

Using the sn-cli tool
---------------------

The sn-cli tool provides subcommands to help you accomplish many common tasks for inspecting and configuring the smartnic platform components.

All commands described below are expected to be executed within the `smartnic-fw` container environment.  Use this command to enter the appropriate environment.
```
docker compose exec smartnic-fw bash
```

The `sn-cli` tool will automatically look for an environment variable called `SN_CLI_SLOTADDR` which can be set to the PCIe BDF address of the device that you would like to interract with.  In the `smartnic-fw` container, this value will already be set for you.

# Displaying device information with the "dev" subcommand

This will show information about the device such as the build version, build date/time and temperature.

```
root@smartnic-fw:/# sn-cli dev version
Device Version Info
	USR_ACCESS:    0x00006a14 (27156)
	BUILD_STATUS:  0x08300532

root@smartnic-fw:/# sn-cli dev temp
Temperature Monitors
	FPGA SLR0:    45.551 (deg C)
```
The `USR_ACCESS` value is typically the unique build pipeline number that produced the embedded FPGA bitfile.
The `BUILD_STATUS` value holds an encoded date/time (Aug 30 at 05:32am) which is when the embedded FPGA bitfile build was started.

# Inspecting and Configuring the CMAC (100G) Interfaces with the "cmac" subcommand

Enable/Disable one or more (or all by default) 100G MAC interfaces using these commands:

```
sn-cli cmac enable
sn-cli cmac disable

sn-cli cmac -p 0 enable
sn-cli cmac -p 1 disable
```
Enabling a CMAC interface allows frames to pass (Rx/Tx) at the MAC layer.  These commands **do not affect** whether the underlying physical layer (PHY) is operational.

Display the current MAC and PHY status of one or more (or all by default) 100G MAC interfaces using these commands:
```
root@smartnic-fw:/# sn-cli cmac status
CMAC0
  Tx (MAC ENABLED/PHY UP)
  Rx (MAC ENABLED/PHY UP)

CMAC1
  Tx (MAC ENABLED/PHY UP)
  Rx (MAC ENABLED/PHY DOWN)
```
In the example output above, CMAC0 PHY layer is **UP** in both the Tx and Rx directions.  The MAC is fully enabled.  This link is operational and should be passing packets normally.

In the example output above, CMAC1 PHY layer is **DOWN** in the Rx (receive) direction.  Possible causes for this are:
* No QSFP28 plugged into 100G port 0 the U280 card
* Wrong type of QSFP28 module plugged into 100G port 0
  * 100G QSFP28 SR4 or LR4 modules are supported
  * Some 100G AOC or DACs are known to work
  * QSFP+ 40G modules **are not supported**
  * QSFP 5G modules **are not supported**
* QSFP28 card improperly seated in the U280 card
  * Check if the QSFP28 module is inserted upside down and physically blocked from being fully inserted
  * Unplug/replug the module, ensuring that it is properly oriented and firmly seated
* Fiber not properly inserted
  * Unplug/replug the fiber connection at each end
* Far end is operating in 4x25G or 2x50G split mode
  * The smartnic platform **does not support** 4x25G or 2x50G mode
  * Only 100G mode is supported on each of the U280 100G interfaces
  * Configure far end in 100G mode
* Far end has RS-FEC (Reed-Solomon Forward Error Correction) enabled
  * The smartnic platform **does not support** RS-FEC
  * Disable RS-FEC on the far end equipment

A more detailed status can also be displayed using the `--verbose` option.  Note that the `--verbose` option is a global option and thus must be positioned **before** the `cmac` subcommand.
```
root@smartnic-fw:/# sn-cli --verbose cmac -p 1 status
CMAC1
  Tx (MAC ENABLED/PHY UP)
	           tx_local_fault 0
  Rx (MAC ENABLED/PHY DOWN)
	         rx_got_signal_os 0
	               rx_bad_sfd 0
	          rx_bad_preamble 0
	 rx_test_pattern_mismatch 0
	  rx_received_local_fault 0
	  rx_internal_local_fault 1
	           rx_local_fault 1
	          rx_remote_fault 0
	                rx_hi_ber 0
	           rx_aligned_err 0
	            rx_misaligned 0
	               rx_aligned 0
	                rx_status 0
```

Display summary statistics for packets Rx'd and Tx'd from CMAC ports
```
root@smartnic-fw:/# sn-cli cmac stats
CMAC0: TX      0 RX      0 RX-DISC      0 RX-ERR      0
CMAC1: TX      0 RX      0 RX-DISC      0 RX-ERR      0
```
Note: The CMAC counters are only cleared/reset when the FPGA is reprogrammed.

# Inspecting and Configuring the PCIe Queue DMA (QDMA) block with the "qdma" subcommand

The QDMA block is responsible for managing all DMA queues used for transferring packets and/or events bidirectionally between the U280 card and the Host CPU over the PCIe bus.  In order for any DMA transfers to be allowed on either of the PCIe Physical Functions (PF), an appropriate number of DMA Queue IDs must be provisioned.  This can be done using the `qdma` subcommand.

Configure the number of queues allocated to each of the PCIe Physical Functions
```
sn-cli qdma setqs 1 1
```
This assigns 1 QID to PF0 and 1 QIDs to PF1.  The `setqs` subcommand also takes care of configuring the RSS entropy -> QID map with an equal weighted distribution of all allocated queues.  If you're unsure of how many QIDs to allocate, using `1 1` here is your best choice.

Inspect the configuration of the QDMA block
```
sn-cli qdma status
```

Packet, byte and error counters are tracked for packets heading between the QDMA engine and the user application.  You can display them with this command:
```
sn-cli qdma stats
```
Refer to the `open-nic-shell` documentation for an explanation of exactly where in the FPGA design these statistics are measured.


# Inspecting packet counters in the smartnic platform with the "probe" subcommand

The smartnic platform implements monitoring points in the datapath at various locations.  You an inspect these counters using this command:
```
sn-cli probe stats
```
Refer to the `esnet-smartnic-hw` documentation for an explanation of exactly where in the FPGA design these statistics are measured.

# Configuring the smartnic platform ingress/egress/bypass switch port remapping functions with the "sw" subcommand

The smartnic platform implements reconfigurable ingress and egress port remapping, connections and redirecting.  You can inspect and modify these configuration points using the "sw" subcommand.

Most of the `sw` subcommands take one or more port bindings as parameters.  The port bindings are of the form:
```
<port>:<port-connector>
```
Where:
* `<port>` is one of
  * cmac0  -- 100G port 0
  * cmac1  -- 100G port 1
  * host0  -- DMA over PCIe Physical Function 0 (PF0)
  * host1  -- DMA over PCIe Physical Function 1 (PF1)
* `<port-connector>` is context dependent and is one of
  * cmac0
  * cmac1
  * host0
  * host1
  * bypass -- a high bandwidth channel through the smartnic which does **NOT** pass through the user's application
  * app0   -- user application port 0 (typically a p4 program ingress)
  * app1   -- user application port 1 (only available when user implements it in verilog)
  * drop   -- infinite blackhole that discards all packets sent to it

## Display the current configuration status
```
sn-cli sw status
```

## Remap/rename physical input ports to logical input ports

The `in-port-rename` subcommand allows you to remap the identity of a smartnic platform physical ingress port to any logical port as seen by the user logic.  Once remapped (eg. from `a`->`b`), all following logic in the smartnic will perceive that the packet arrived on ingress port `b` even though it physically arrived on port `a`.  This can be useful for test injection scenarios but would typically be set to a straight-through mapping in production.
```
sn-cli sw in-port-rename a:b
```

To reset this mapping so each port maps to its usual identity:
```
sn-cli sw in-port-rename cmac0:cmac0 cmac1:cmac1 host0:host0 host1:host1
```

## Attach logical input ports to pipelines

The `in-port-connect` subcommand allows you to connect a logical input port to different processing pipelines within the smartnic.  This can be used to connect to a p4 program or to custom logic within the user application.  It can also be used to shunt all packets to a blackhole or to bypass packets around the user application entirely.

```
sn-cli sw in-port-connect cmac0:app0 cmac1:app0 host0:bypass host1:bypass
```

## Connect input ports to output ports in the bypass path

The `bypass-connect` subcommand allows you to connect input ports directly to output ports as they pass through the bypass path (ie. not through the user application).  This is useful for providing direct connectivity from host PCIe PFs to 100G CMAC interfaces for network testing.

```
sn-cli sw bypass-connect host0:cmac0 host1:cmac1 cmac0:host0 cmac1:host1
```

**NOTE** any packets that follow the bypass path will not be processed by the user's p4 program

## Override user application output port decisions and redirect to an alternate port

The `app0-port-redirect` and `app1-port-redirect` subcommands allow the user to override the forwarding decisions made by the user application and/or p4 program and redirect any given output port to a different output port.  This can be useful during development/debugging and in test fixtures.

**NOTE** there are separate overrides for the app0 outputs and the app1 outputs.

```
sn-cli sw app0-port-redirect cmac0:host0 cmac1:host1
sn-cli sw app1-port-redirect cmac0:host0 cmac1:host1
```

To reset this mapping so each output ports maps to its usual destination:
```
sn-cli sw app0-port-redirect cmac0:cmac0 cmac1:cmac1 host0:host0 host1:host1
sn-cli sw app1-port-redirect cmac0:cmac0 cmac1:cmac1 host0:host0 host1:host1
```

Using the sn-p4-cli tool
------------------------

The user's p4 application embedded within the smartnic design may have configurable lookup tables which are used during the wire-speed execution of the packet processing pipeline.  The sn-p4-cli tool provides subcommands to help you to manage the rules in all of the lookup tables defined in your p4 program.

All commands described below are expected to be executed within the `smartnic-fw` container environment.  Use this command to enter the appropriate environment.
```
docker compose exec smartnic-fw bash
```

The `sn-p4-cli` tool will automatically look for an environment variable called `SN_P4_CLI_SERVER` which can be set to the hostname of the `sn-p4-agent` that will perform all of the requested actions on the real hardware.  In the `smartnic-fw` container, this value will already be set for you.

# Inspecting the pipeline structure with the "info" subcommand

The `info` subcommand is used to display the pipeline structure, including table names, match fields (and their types), action names and the list of parameters for each action.  This information can be used to formulate new rule definitions for the other subcommands.

```
sn-p4-cli info
```

# Inserting a new rule into a table

The `table-insert` subcommand allows you to insert a new rule into a specified table.

```
sn-p4-cli table-insert <table-name> <action-name> --match <match-expr> [--param <param-expr>] [--priority <prio-val>]
```
Where:
* `<table-name>` is the name of the table to be operated on
* `<action-name>` is the action that you would like to activate when this rule matches
* `<match-expr>` is one or more match expressions which collectively define when this rule should match a given packet
  * The number and type of the match fields depends on the p4 definition of the table
  * The `--match` option may be specified multiple times and all `match-expr`s will be concatenated
* `<param-expr>` is one or more parameter values which will be returned as a result when this rule matches a given packet
  * The number and type of the action parameters depends on the p4 definition of the action within the table
  * Some actions require zero parameters.  In this case, omit the optional `--param` option entirely.
* `<prio-val>` is the priority to be used to resolve scenarios where multiple matches could occur
  * The `--priority` option is *required* for tables with CAM/TCAM type matches (prefix/range/ternary)
  * The `--priority` option is *prohibited* for tables without CAM/TCAM type mathes

**NOTE**: You can find details about your pipeline structure and valid names by running the `info` subcommand.

# Updating an existing rule within a table

The `table-update` subcommand allows you to update the action and parameters for an existing rule within a table

```
sn-p4-cli table-update <table-name> <new-action-name> --match <match-expr> [--param <new-param-expr>]
```
Where:
* `<table-name>` is the table containing the rule to be updated
* `<new-action-name>` is the new action that should be applied when this rule matches
* `<match-expr>` is the exact original `<match-expr>` used when the original rule was inserted
* `<new-param-expr>` is the set of new parameters to be returned when this rule matches
  * **NOTE**: the new parameters must be consistent with the new action

# Removing previously inserted rules

The `clear-all` and `table-clear` and `table-delete` subcommands allow you to remove rules from tables with varying precision.

Clear all rules from *all tables* in the pipeline.
```
sn-p4-cli clear-all`
```

Clear all rules from a *single* specified table.
```
sn-p4-cli table-clear <table-name>
```

Remove a specific rule from a specific table.
```
table-delete <table-name> --match <match-expr>
```

# Bulk changes of rules using a p4bm simulator rules file

Using the the `p4bm-apply` subcommand, a list of pipeline modifications can be applied from a file.  A subset of the full p4bm simulator file format is supported by the `sn-p4-cli` command.

```
sn-p4-cli p4bm-apply <filename>
```

Supported actions within the p4bm file are:
* `table_insert <table-name> <action-name> <match-expr> => <param-expr> [priority]`
  * Insert a rule
* `clear_all`
  * Clear all rules from all tables
* `table_clear <table-name>`
  * Clear all rules from a specified table

All comment characters `#` and text following them up to the end of the line are ignored.

Stopping the runtime environment
--------------------------------

When we're finished using the smartnic runtime environment, we can stop and remove our docker containers.

```
docker compose down -v
```

Using the smartnic-dpdk container
=================================

The `sn-stack` environment can be started in a mode where the FPGA can be controlled by a DPDK application.  Running in this mode requires a few carefully ordered steps.

Broadly speaking, the steps required to bring up a DPDK application are as follows:
* Bind the `vfio-pci` kernel driver to each FPGA PCIe physical function (PF)
  * This is handled automatically by the sn-stack when `COMPOSE_PROFILES=smartnic-dpdk` is set in the `.env` file.
* Run a DPDK application with appropriate DPDK Environment Abstraction Layer (EAL) settings
  * Use `-a $SN_PCIE_DEV.0` to allow control of one or more specific FPGA PCIe PFs
  * Use `-d librte_net_qdma.so` to dynamically link the correct Userspace Polled-Mode Driver (PMD) for the smartnic QDMA engine
  * The EAL will
    * Open the PCIe PFs using the kernel's `vfio-pci` driver
	* Take the FPGA device out of reset
	* Open and map large memory regions for DMA using the kernel's `hugepages` driver
  * The application is responsible for assigning buffers to one or more of the FPGA's DMA queues
* Use the `sn-cli` tool to configure some of the low-level hardware components in the FPGA
  * Configure the set of valid DMA queues in the FPGA (must match what is set in the DPDK application)
  * Bring up the physical ethernet ports

In the examples below, we will be running the `pktgen-dpdk` application to control packet tx/rx via the FPGA's PCIe physical functions.  This can be very useful for injecting packets into a design for testing behaviour on real hardware.

For more information about DPDK in general, see:
* http://core.dpdk.org/doc/

For more information about the `pktgen-dpdk` application, see:
* https://pktgen-dpdk.readthedocs.io/en/latest/index.html

Before you bring up the `sn-stack`, please ensure that you have uncommented this line in your `.env` file
```
COMPOSE_PROFILES=smartnic-dpdk
```

If you changed this while the stack was already running, you'll need to restart the stack with down/up.

First, you'll need to start up the `pktgen` application to open the vfio-pci device for PF0 and PF1 and take the FPGA out of reset.
```
$ docker compose exec smartnic-dpdk bash
root@smartnic-dpdk:/# pktgen -a $SN_PCIE_DEV.0 -a $SN_PCIE_DEV.1 -l 4-8 -n 4 -d librte_net_qdma.so --file-prefix $SN_PCIE_DEV- -- -v -m [5:6].0 -m [7:8].1
Pktgen:/> help
```
NOTE: Leave this application running while doing the remaining setup steps.  The setup steps below must be re-run after each time you restart the pktgen application since the FPGA gets reset between runs.

Open a **separate** shell window which you will use for doing the low-level smartnic platform configuration.

Configure the Queue mappings for host PF0 and PF1 interfaces and bring up the physical ethernet ports using the `smartnic-fw` container.

```
$ docker compose exec smartnic-fw bash
root@smartnic-fw:/# sn-cli qdma setqs 1 1
root@smartnic-fw:/# sn-cli qdma status
root@smartnic-fw:/# sn-cli cmac enable
root@smartnic-fw:/# sn-cli cmac status
```
Setting up the queue mappings tells the smartnic platform which QDMA queues to use for h2c and c2h packets.  Enabling the CMACs allows Rx and Tx packets to flow (look for `MAC ENABLED/PHY UP`).

Advanced usage of the pktgen-dpdk application
=============================================

Example of streaming packets out of an interface from a pcap file rather than generating the packets within the UI.
Note the `-s <P>:file.pcap` option where `P` refers to the port number to bind the pcap file to.

```
root@smartnic-dpdk:/# pktgen -a $SN_PCIE_DEV.0 -a $SN_PCIE_DEV.1 -l 4-8 -n 4 -d librte_net_qdma.so --file-prefix $SN_PCIE_DEV- -- -v -m [5:6].0 -m [7:8].1 -s 1:your_custom.pcap
Pktgen:/> port 1
Pktgen:/> page pcap
Pktgen:/> page main
Pktgen:/> start 1
Pktgen:/> stop 1
Pktgen:/> clr
```

Example of running a particular test case via a script rather than typing at the UI

```
cat <<_EOF > /tmp/test.pkt
clr
set 1 size 1400
set 1 count 1000000
enable 0 capture
start 1
disable 0 capture
_EOF
```

```
root@smartnic-dpdk:/# pktgen -a $SN_PCIE_DEV.0 -a SN_PCIE_DEV.1 -l 4-8 -n 4 -d librte_net_qdma.so --file-prefix $SN_PCIE_DEV- -- -v -m [5:6].0 -m [7:8].1 -f /tmp/test.pkt
```
