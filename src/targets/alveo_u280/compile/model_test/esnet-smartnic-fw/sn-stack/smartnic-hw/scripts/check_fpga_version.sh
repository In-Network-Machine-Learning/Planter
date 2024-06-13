#!/bin/bash

HW_SERVER_URL=$1
HW_TARGET_SERIAL=$2
BITFILE_PATH=$3

# Set up our vivado runtime env
source /opt/Xilinx/Vivado_Lab/${VIVADO_VERSION}/settings64.sh

# Collect all of the JTAG register values for the currently loaded FPGA device
/opt/Xilinx/Vivado_Lab/${VIVADO_VERSION}/bin/vivado_lab \
    -nolog \
    -nojournal \
    -tempDir /tmp/ \
    -mode batch \
    -notrace \
    -quiet \
    -source /scripts/read_jtag_registers.tcl \
    -tclargs "$HW_SERVER_URL" "$HW_TARGET_SERIAL" /tmp/u280.jtag.registers.json

# Grab the USERCODE register value (ie. which FPGA is *currently* loaded)
USERCODE=$(cat /tmp/u280.jtag.registers.json | jq -r '.["REGISTER.USERCODE.SLR0"]')
echo "Found JTAG USERCODE=${USERCODE}"

# Read the UserID field out of the header in the new target bit file
USERID=$(file -b $BITFILE_PATH | sed -re 's/^.*(;UserID=)(0[Xx])?([0-9A-Fa-f]+).*$/0x\3/g' | tr 'A-Z' 'a-z')
echo "Found Target UserID=${USERID}"

# Compare the current with the target FPGA versions
if [ "x$USERCODE" = "x$USERID" ] ; then
    # Running and target versions match
    exit 0
else
    # Running version does not match target version
    exit 1
fi
