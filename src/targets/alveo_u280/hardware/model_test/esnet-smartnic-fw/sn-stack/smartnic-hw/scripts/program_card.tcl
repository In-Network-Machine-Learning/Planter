if { $argc != 3 } {
    puts "The script requires a path of the bitfile."
    puts "For example, vivado -mode batch -source program_card.tcl -tclargs /tmp/fpga.bit"
    puts "Please try again."
    exit 1
}

puts "About to flash the following bitfile: [lindex $argv 2]"
open_hw_manager -verbose
connect_hw_server -url [lindex $argv 0] -verbose
puts "Available Hardware Targets:"
foreach {target} [get_hw_targets] {
    puts "\t$target"
}
puts -nonewline "Selecting Hardware Target Serial: "
puts [lindex $argv 1]
current_hw_target -verbose [get_hw_targets -verbose [format "*/xilinx_tcf/Xilinx/%s" [lindex $argv 1]]]
puts -nonewline "Selected Hardware Target: "
puts [current_hw_target]
open_hw_target -verbose
puts -nonewline "Selected Hardware Device: "
puts [current_hw_device]

set_property PROGRAM.FILE [lindex $argv 2] [current_hw_device]
program_hw_device [current_hw_device]
