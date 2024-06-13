module tb;
    import tb_pkg::*;
    import smartnic_322mhz_pkg::*;

    // (Local) parameters
    localparam int AXIS_DATA_WID = 512;
    localparam int AXIS_DATA_BYTE_WID = AXIS_DATA_WID/8;

    //===================================
    // (Common) test environment
    //===================================
    tb_env env;

    //===================================
    // Device Under Test
    //===================================

    // Signals
    logic        clk;
    logic        rstn;

    logic [63:0] timestamp;

    axi4l_intf axil_if       ();
    axi4l_intf axil_to_sdnet ();

    axi4s_intf #(.DATA_BYTE_WID(AXIS_DATA_BYTE_WID), .TID_T(port_t), .TDEST_T(port_t)) axis_in_if ();
    axi4s_intf #(.DATA_BYTE_WID(AXIS_DATA_BYTE_WID), .TID_T(port_t), .TDEST_T(egr_tdest_t)) axis_out_if ();
    axi4s_intf #(.DATA_BYTE_WID(AXIS_DATA_BYTE_WID), .TID_T(port_t), .TDEST_T(egr_tdest_t)) axis_to_adpt ();
    axi4s_intf #(.DATA_BYTE_WID(AXIS_DATA_BYTE_WID), .TID_T(port_t), .TDEST_T(port_t)) axis_from_adpt ();

    axi3_intf  #(.DATA_BYTE_WID(32), .ADDR_WID(33), .ID_T(logic[5:0])) axi_to_hbm [16] ();

    // DUT instance
    p4_app DUT(
        .core_clk            ( clk ),
        .core_rstn           ( rstn ),
        .timestamp           ( timestamp ),
        .axil_if             ( axil_if ),
        .axil_to_sdnet       ( axil_to_sdnet ),
        .axis_from_switch_0  ( axis_in_if ),
        .axis_to_switch_0    ( axis_out_if ),
        .axis_to_switch_1    ( axis_to_adpt ),
        .axis_from_switch_1  ( axis_from_adpt ),
        .axi_to_hbm          ( axi_to_hbm )
    );

    hbm_bfm #(.PSEUDO_CHANNELS (16)) i_hbm_model (.axi3_if (axi_to_hbm));

    //===================================
    // Local signals
    //===================================
    logic rst;

    // Interfaces
    std_reset_intf #(.ACTIVE_LOW(1)) reset_if      (.clk(clk));
    std_reset_intf #(.ACTIVE_LOW(1)) mgmt_reset_if (.clk(axil_if.aclk));

    timestamp_if #() timestamp_if (.clk(clk), .srst(rst));

    // Generate datapath clock
    initial clk = 1'b0;
    always #1455ps clk = ~clk; // 343.75 MHz

    // Generate AXI management clock
    initial axil_if.aclk = 1'b0;
    always  #4ns axil_if.aclk = ~axil_if.aclk; // 125 MHz


    // Assign reset interfaces
    assign rstn = reset_if.reset;
    initial reset_if.ready = 1'b0;
    always @(posedge clk) reset_if.ready <= rstn;

    assign axil_if.aresetn = mgmt_reset_if.reset;
    initial mgmt_reset_if.ready = 1'b0;
    always @(posedge axil_if.aclk) mgmt_reset_if.ready <= axil_if.aresetn;

    assign rst = ~rstn;

    // SDNet AXI-L interface shares common AXI-L clock/reset
    assign axil_to_sdnet.aclk = axil_if.aclk;
    assign axil_to_sdnet.aresetn = axil_if.aresetn;

    // Timestamp
    assign timestamp = timestamp_if.timestamp;

    // Assign AXI-S input clock/reset
    assign axis_in_if.aclk = clk;
    assign axis_in_if.aresetn = rstn;

    assign axis_from_adpt.aclk = clk;
    assign axis_from_adpt.aresetn = rstn;

    //===================================
    // Build
    //===================================
    function void build();
        if (env == null) begin
            // Instantiate environment
            env = new("tb_env",0); // Configure for little-endian

            // Connect
            env.reset_vif = reset_if;
            env.mgmt_reset_vif = mgmt_reset_if;
            env.timestamp_vif = timestamp_if;
            env.axil_vif = axil_if;
            env.axil_sdnet_vif = axil_to_sdnet;
            env.axis_in_vif = axis_in_if;
            env.axis_out_vif = axis_out_if;
            env.axis_to_adpt_vif = axis_to_adpt;
            env.axis_from_adpt_vif = axis_from_adpt;

            env.axi_to_hbm_vif = axi_to_hbm;

            env.connect();
        end
    endfunction

    // Export AXI-L accessors to VitisNetP4 shared library
    export "DPI-C" task axi_lite_wr;
    task axi_lite_wr(input int address, input int data);
        env.sdnet_write(address, data);
    endtask

    export "DPI-C" task axi_lite_rd;
    task axi_lite_rd(input int address, inout int data);
        env.sdnet_read(address, data);
    endtask

endmodule : tb
