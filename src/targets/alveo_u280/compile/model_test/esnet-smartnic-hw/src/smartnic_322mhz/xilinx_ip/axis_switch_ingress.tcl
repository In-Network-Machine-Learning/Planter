set module_name axis_switch_ingress

create_ip -name axis_switch -vendor xilinx.com -library ip -module_name $module_name -dir . -force

set_property -dict [list \
    CONFIG.NUM_SI {4} \
    CONFIG.NUM_MI {3} \
    CONFIG.TDATA_NUM_BYTES {64} \
    CONFIG.HAS_TKEEP {1} \
    CONFIG.HAS_TLAST {1} \
    CONFIG.TID_WIDTH {2} \
    CONFIG.TDEST_WIDTH {2} \
    CONFIG.ARB_ON_MAX_XFERS {0} \
    CONFIG.ARB_ON_TLAST {1} \
    CONFIG.DECODER_REG {1} \
    CONFIG.M02_AXIS_HIGHTDEST {0x00000003} \
] [get_ips $module_name]
