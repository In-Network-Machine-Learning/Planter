#! /bin/bash

function usage() {
    echo ""
    echo "Usage: $(basename $0) <hw_server_url> <hw_target_serial> <mcsfile_path> <pcie_device_addr>"
    echo "  hw_server_url: host:port for xilinx hw_server (e.g. xilinx-hwserver:3121)"
    echo "  hw_target_serial: serial number of serial JTAG device (e.g. 21770205K01Y)"
    echo "     can be discovered with: lsusb -v -d 0403:6011 | grep iSerial"
    echo "     can be set to '*' to select the first serial JTAG device that is found"
    echo "  mcsfile_path: full path to the .mcs file to be loaded into the fpga flash"
    echo "  pcie_device_addr: pcie domain:bus:device (e.g. 0000:81:00)"
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

# Make sure the mcsfile exists and is readable
if [ ! -e $1 ] ; then
    echo "ERROR: mcsfile does not exist: $1"
    exit 1
fi
if [ ! -r $1 ] ; then
    echo "ERROR: mcsfile at $1 is not readable"
    exit 1
fi

# Assume we have a sane mcsfile
echo "Using target mcsfile: $1"
echo "    $(head -n 5 $1)"
MCSFILE_PATH=$1
shift

# Grab the FPGA device address
echo "Expecting to reprogram PCIe device: $1"
FPGA_PCIE_DEV=$1
shift

# Make note of any extra, ignored command line parameters
if [ "$#" -gt 0 ] ; then
    echo "WARNING: Ignoring extra command line parameters $@"
fi

# Disconnect any devices from the kernel
for i in $(lspci -Dmm -s $FPGA_PCIE_DEV | cut -d' ' -f 1) ; do
    echo 1 > /sys/bus/pci/devices/$i/remove
done

# Program the mcsfile into the FPGA flash
source /opt/Xilinx/Vivado_Lab/${VIVADO_VERSION}/settings64.sh
/opt/Xilinx/Vivado_Lab/${VIVADO_VERSION}/bin/vivado_lab \
    -nolog \
    -nojournal \
    -tempDir /tmp/ \
    -mode batch \
    -notrace \
    -quiet \
    -source /scripts/program_flash.tcl \
    -tclargs "$HW_SERVER_URL" "$HW_TARGET_SERIAL" "$MCSFILE_PATH"
if [ $? -ne 0 ] ; then
    echo "Failed to write FPGA flash, bailing out"
    exit 1
fi

# Always rescan the PCIe bus
echo 1 > /sys/bus/pci/rescan
