set module_name clk_wiz_1

create_ip -name clk_wiz -vendor xilinx.com -library ip -module_name $module_name -dir . -force

set_property -dict [list \
    CONFIG.PRIMITIVE {Auto} \
    CONFIG.PRIM_SOURCE {No_buffer} \
    CONFIG.PRIM_IN_FREQ {125.000} \
    CONFIG.CLKOUT2_USED {true} \
    CONFIG.CLK_OUT1_PORT {clk_100mhz} \
    CONFIG.CLK_OUT2_PORT {hbm_ref_clk} \
] [get_ips $module_name]
