#!/bin/bash

function usage() {
    echo ""
    echo "Usage: $(basename $0) <hw_server_url> <hw_target_serial> <bitfile_path> <pcie_device_addr> [FORCE]"
    echo "  hw_server_url: host:port for xilinx hw_server (e.g. xilinx-hwserver:3121)"
    echo "  hw_target_serial: serial number of serial JTAG device (e.g. 21770205K01Y)"
    echo "     can be discovered with: lsusb -v -d 0403:6011 | grep iSerial"
    echo "     can be set to '*' to select the first serial JTAG device that is found"
    echo "  bitfile_path: full path to the .bit file to be loaded into the fpga"
    echo "  pcie_device_addr: pcie domain:bus:device (e.g. 0000:81:00)"
    echo "  FORCE: optionally force a reload even if the USERCODE/UserID fields match"
    echo ""
}

# Make sure the caller has provided the required parameters
if [ "$#" -lt 4 ] ; then
    echo "ERROR: Missing required parameter(s)"
    usage
    exit 1
fi

# Grab URL pointing to the xilinx hw_server
echo "Using Xilinx hw_server URL: $1"
HW_SERVER_URL=$1
shift

# Grab the serial number for the USB-JTAG cable so that
# we can differentiate among them in case we have many
echo "Using USB-JTAG cable with serial: $1"
HW_TARGET_SERIAL=$1
shift

# Make sure the bitfile exists and is readable
if [ ! -e $1 ] ; then
    echo "ERROR: Bitfile does not exist: $1"
    exit 1
fi
if [ ! -r $1 ] ; then
    echo "ERROR: Bitfile at $1 is not readable"
    exit 1
fi

# Make sure the provided file looks like a xilinx bitfile
file -b $1 | grep 'Xilinx BIT data' 2>&1 > /dev/null
if [ $? -ne 0 ] ; then
    echo "ERROR: Provided file does not appear to be Xilinx BIT data"
    exit 1
fi

# Looks like we have a sane bitfile to work with
echo "Using target bitfile: $1"
echo "    $(file -b $1)"
BITFILE_PATH=$1
shift

# Grab the FPGA device address
echo "Expecting to reprogram PCIe device: $1"
FPGA_PCIE_DEV=$1
shift

# Check for the optional FORCE parameter
FORCE=0
if [ "$#" -ge 1 ] ; then
    if [ "x$1" = "xFORCE" ] ; then
	echo "NOTE: Using the FORCE.  FPGA will be reloaded even if USERCODE/UserID registers match."
	FORCE=1
	shift
    fi
fi

# Make note of any extra, ignored command line parameters
if [ "$#" -gt 0 ] ; then
    echo "WARNING: Ignoring extra command line parameters $@"
fi

# First, check if we are already running the correct FPGA version
/scripts/check_fpga_version.sh "$HW_SERVER_URL" "$HW_TARGET_SERIAL" "$BITFILE_PATH"
FPGA_VERSION_OK=$?

if [[ $FORCE -eq 0 && $FPGA_VERSION_OK -eq 0 ]] ; then
    echo "Running and Target FPGA versions match"
else
    if [ $FPGA_VERSION_OK -eq 0 ] ; then
	echo "Running versions match but an FPGA reprogramming was FORCE'd anyway"
    else
	echo "Running version does not match Target version, reprogramming"
    fi

    # Disconnect any devices from the kernel
    for i in $(lspci -Dmm -s $FPGA_PCIE_DEV | cut -d' ' -f 1) ; do
	echo 1 > /sys/bus/pci/devices/$i/remove
    done

    # Program the bitfile into the FPGA
    source /opt/Xilinx/Vivado_Lab/${VIVADO_VERSION}/settings64.sh
    /opt/Xilinx/Vivado_Lab/${VIVADO_VERSION}/bin/vivado_lab \
	-nolog \
	-nojournal \
	-tempDir /tmp/ \
	-mode batch \
	-notrace \
        -quiet \
	-source /scripts/program_card.tcl \
	-tclargs "$HW_SERVER_URL" "$HW_TARGET_SERIAL" "$BITFILE_PATH"
    if [ $? -ne 0 ] ; then
	echo "Failed to load FPGA, bailing out"
	exit 1
    fi

    # Re-check if we have all expected devices on the bus now
    /scripts/check_fpga_version.sh "$HW_SERVER_URL" "$HW_TARGET_SERIAL" "$BITFILE_PATH"
    FPGA_VERSION_OK=$?
    if [ $FPGA_VERSION_OK -eq 0 ] ; then
	echo "Running and Target FPGA versions match"
    else
	echo -n "Running version STILL does not match Target version.  "
	if [ $FORCE -eq 1 ] ; then
	    echo "Continuing anyway due to FORCE option."
	else
	    echo "Bailing out!"
	    exit 1
	fi
    fi
fi

# Always rescan the PCIe bus
echo 1 > /sys/bus/pci/rescan
