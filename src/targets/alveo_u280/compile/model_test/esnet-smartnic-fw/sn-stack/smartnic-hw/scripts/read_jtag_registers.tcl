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
#puts [get_property REGISTER.USERCODE.SLR0 [current_hw_device]]

proc property_list_to_json {chan alist} {
    set len [llength $alist]
    puts $chan "{"
    for {set i 0} {$i < $len} {incr i} {
	set k [lindex $alist $i]
	set v [get_property $k [current_hw_device]]
	puts -nonewline $chan "  \"$k\": \"$v\""
	if {$i < ($len - 1)} {
	    puts $chan ","
	} else {
	    puts $chan ""
	}
    }
    puts $chan "}"
}

set regfile [open [lindex $argv 2] w]
property_list_to_json $regfile [list_property [current_hw_device] REGISTER.*]
