if { $argc != 3 } {
    puts "The script requires a path of the mcsfile."
    puts "For example, vivado -mode batch -source program_card.tcl -tclargs /tmp/fpga.mcs"
    puts "Please try again."
    exit 1
}

# Set up the hw manager
puts "Connecting to hw_server at: [lindex $argv 0]"
open_hw_manager -verbose
connect_hw_server -url [lindex $argv 0] -verbose

# Let's see what's attached
puts "Available Hardware Targets:"
foreach {target} [get_hw_targets] {
    puts "\t$target"
}

# Select the specific device that the user wants us to use
puts -nonewline "Selecting Hardware Target Serial: "
puts [lindex $argv 1]
current_hw_target -verbose [get_hw_targets -verbose [format "*/xilinx_tcf/Xilinx/%s" [lindex $argv 1]]]
puts -nonewline "Selected Hardware Target: "
puts [current_hw_target]
open_hw_target -verbose
puts -nonewline "Selected Hardware Device: "
puts [current_hw_device]

# Find out how we booted to see if we should write the flash
puts "Boot status"
puts "             Prev(1)\tCurr(0)"
puts "  WRAP_ERROR [get_property {REGISTER.BOOT_STATUS.SLR0.BIT[14]_1_WRAP_ERROR} [current_hw_device]]\t\t[get_property {REGISTER.BOOT_STATUS.SLR0.BIT[06]_0_WRAP_ERROR} [current_hw_device]]"
puts "  CRC_ERROR  [get_property {REGISTER.BOOT_STATUS.SLR0.BIT[13]_1_CRC_ERROR} [current_hw_device]]\t\t[get_property {REGISTER.BOOT_STATUS.SLR0.BIT[05]_0_CRC_ERROR} [current_hw_device]]"
puts "  ID_ERROR   [get_property {REGISTER.BOOT_STATUS.SLR0.BIT[12]_1_ID_ERROR} [current_hw_device]]\t\t[get_property {REGISTER.BOOT_STATUS.SLR0.BIT[04]_0_ID_ERROR} [current_hw_device]]"
puts "  WTO_ERROR  [get_property {REGISTER.BOOT_STATUS.SLR0.BIT[11]_1_WATCHDOG_TIMEOUT_ERROR} [current_hw_device]]\t\t[get_property {REGISTER.BOOT_STATUS.SLR0.BIT[03]_0_WATCHDOG_TIMEOUT_ERROR} [current_hw_device]]"
puts "  IPROG      [get_property {REGISTER.BOOT_STATUS.SLR0.BIT[10]_1_INTERNAL_PROG} [current_hw_device]]\t\t[get_property {REGISTER.BOOT_STATUS.SLR0.BIT[02]_0_INTERNAL_PROG} [current_hw_device]]"
puts "  FALLBACK   [get_property {REGISTER.BOOT_STATUS.SLR0.BIT[09]_1_FALLBACK} [current_hw_device]]\t\t[get_property {REGISTER.BOOT_STATUS.SLR0.BIT[01]_0_FALLBACK} [current_hw_device]]"
puts "  VALID      [get_property {REGISTER.BOOT_STATUS.SLR0.BIT[08]_1_STATUS_VALID} [current_hw_device]]\t\t[get_property {REGISTER.BOOT_STATUS.SLR0.BIT[00]_0_STATUS_VALID} [current_hw_device]]"

#### Can't tell the difference btw flash boot of gold vs jtag boot

puts "About to flash the following bitfile: [lindex $argv 2]"

# create a hw_cfgmem object for the correct flash part for the u280
create_hw_cfgmem    -hw_device [current_hw_device] [lindex [get_cfgmem_parts {mt25qu01g-spi-x1_x2_x4}] 0]

# configure hw_cfgmem object to erase/program/verify flash
set_property PROGRAM.FILES                  [lindex $argv 2]  [current_hw_cfgmem]
set_property PROGRAM.ADDRESS_RANGE          {use_file}        [current_hw_cfgmem]
set_property PROGRAM.UNUSED_PIN_TERMINATION {pull-none}       [current_hw_cfgmem]
set_property PROGRAM.BLANK_CHECK            0                 [current_hw_cfgmem]
set_property PROGRAM.ERASE                  1                 [current_hw_cfgmem]
set_property PROGRAM.CFG_PROGRAM            1                 [current_hw_cfgmem]
set_property PROGRAM.VERIFY                 1                 [current_hw_cfgmem]
set_property PROGRAM.CHECKSUM               0                 [current_hw_cfgmem]
set_property PROGRAM.PRM_FILE               {}                [current_hw_cfgmem]

# write the flash-programming bitstream into the FPGA
create_hw_bitstream -hw_device [current_hw_device] [get_property PROGRAM.HW_CFGMEM_BITFILE [current_hw_device]]
program_hw_devices             [current_hw_device]
refresh_hw_device              [current_hw_device]

# write the flash
program_hw_cfgmem   -verbose -hw_cfgmem [current_hw_cfgmem]

# initialize the FPGA from the newly programmed flash
boot_hw_device                 [current_hw_device]
