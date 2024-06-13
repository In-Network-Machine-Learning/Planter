module smartnic_322mhz_app
#(
    parameter int AXI_HBM_NUM_IFS = 16
) (
    input  logic         core_clk,
    input  logic         core_rstn,
    input  logic         axil_aclk,
    input  logic [63:0]  timestamp,

    // AXI-L control interface
    // (synchronous to axil_aclk domain)
    // -- Reset
    input  logic         axil_aresetn,
    // -- Write address
    input  logic         axil_awvalid,
    output logic         axil_awready,
    input  logic [31:0]  axil_awaddr,
    input  logic [2:0]   axil_awprot,
    // -- Write data
    input  logic         axil_wvalid,
    output logic         axil_wready,
    input  logic [31:0]  axil_wdata,
    input  logic [3:0]   axil_wstrb,
    // -- Write response
    output logic         axil_bvalid,
    input  logic         axil_bready,
    output logic [1:0]   axil_bresp,
    // -- Read address
    input  logic         axil_arvalid,
    output logic         axil_arready,
    input  logic [31:0]  axil_araddr,
    input  logic [2:0]   axil_arprot,
    // -- Read data
    output logic         axil_rvalid,
    input  logic         axil_rready,
    output logic [31:0]  axil_rdata,
    output logic [1:0]   axil_rresp,

    // (SDNet) AXI-L control interface
    // (synchronous to axil_aclk domain)
    // -- Reset
    input  logic         axil_sdnet_aresetn,
    // -- Write address
    input  logic         axil_sdnet_awvalid,
    output logic         axil_sdnet_awready,
    input  logic [31:0]  axil_sdnet_awaddr,
    input  logic [2:0]   axil_sdnet_awprot,
    // -- Write data
    input  logic         axil_sdnet_wvalid,
    output logic         axil_sdnet_wready,
    input  logic [31:0]  axil_sdnet_wdata,
    input  logic [3:0]   axil_sdnet_wstrb,
    // -- Write response
    output logic         axil_sdnet_bvalid,
    input  logic         axil_sdnet_bready,
    output logic [1:0]   axil_sdnet_bresp,
    // -- Read address
    input  logic         axil_sdnet_arvalid,
    output logic         axil_sdnet_arready,
    input  logic [31:0]  axil_sdnet_araddr,
    input  logic [2:0]   axil_sdnet_arprot,
    // -- Read data
    output logic         axil_sdnet_rvalid,
    input  logic         axil_sdnet_rready,
    output logic [31:0]  axil_sdnet_rdata,
    output logic [1:0]   axil_sdnet_rresp,

    // AXI-S data interface (from switch)
    // (synchronous to core_clk domain)
    input  logic         axis_from_switch_0_tvalid,
    output logic         axis_from_switch_0_tready,
    input  logic [511:0] axis_from_switch_0_tdata,
    input  logic [63:0]  axis_from_switch_0_tkeep,
    input  logic         axis_from_switch_0_tlast,
    input  logic [1:0]   axis_from_switch_0_tid,
    input  logic [1:0]   axis_from_switch_0_tdest,
    input  logic [15:0]  axis_from_switch_0_tuser_pid,

    // AXI-S data interface (to switch)
    // (synchronous to core_clk domain)
    output logic         axis_to_switch_0_tvalid,
    input  logic         axis_to_switch_0_tready,
    output logic [511:0] axis_to_switch_0_tdata,
    output logic [63:0]  axis_to_switch_0_tkeep,
    output logic         axis_to_switch_0_tlast,
    output logic [1:0]   axis_to_switch_0_tid,
    output logic [2:0]   axis_to_switch_0_tdest,
    output logic [15:0]  axis_to_switch_0_tuser_pid,
    output logic         axis_to_switch_0_tuser_rss_enable,
    output logic [11:0]  axis_to_switch_0_tuser_rss_entropy,

    // AXI-S data interface (from host)
    // (synchronous to core_clk domain)
    input  logic         axis_from_switch_1_tvalid,
    output logic         axis_from_switch_1_tready,
    input  logic [511:0] axis_from_switch_1_tdata,
    input  logic [63:0]  axis_from_switch_1_tkeep,
    input  logic         axis_from_switch_1_tlast,
    input  logic [1:0]   axis_from_switch_1_tid,
    input  logic [1:0]   axis_from_switch_1_tdest,
    input  logic [15:0]  axis_from_switch_1_tuser_pid,

    // AXI-S data interface (to host)
    // (synchronous to core_clk domain)
    output logic         axis_to_switch_1_tvalid,
    input  logic         axis_to_switch_1_tready,
    output logic [511:0] axis_to_switch_1_tdata,
    output logic [63:0]  axis_to_switch_1_tkeep,
    output logic         axis_to_switch_1_tlast,
    output logic [1:0]   axis_to_switch_1_tid,
    output logic [2:0]   axis_to_switch_1_tdest,
    output logic [15:0]  axis_to_switch_1_tuser_pid,
    output logic         axis_to_switch_1_tuser_rss_enable,
    output logic [11:0]  axis_to_switch_1_tuser_rss_entropy,

    // flow control signals (one from each egress FIFO).
    input logic [3:0]    egr_flow_ctl,

    // AXI3 interfaces to HBM
    // (synchronous to core clock domain)
    output logic [(AXI_HBM_NUM_IFS*  1)-1:0] axi_to_hbm_aclk,
    output logic [(AXI_HBM_NUM_IFS*  1)-1:0] axi_to_hbm_aresetn,
    output logic [(AXI_HBM_NUM_IFS*  6)-1:0] axi_to_hbm_awid,
    output logic [(AXI_HBM_NUM_IFS* 33)-1:0] axi_to_hbm_awaddr,
    output logic [(AXI_HBM_NUM_IFS*  4)-1:0] axi_to_hbm_awlen,
    output logic [(AXI_HBM_NUM_IFS*  3)-1:0] axi_to_hbm_awsize,
    output logic [(AXI_HBM_NUM_IFS*  2)-1:0] axi_to_hbm_awburst,
    output logic [(AXI_HBM_NUM_IFS*  2)-1:0] axi_to_hbm_awlock,
    output logic [(AXI_HBM_NUM_IFS*  4)-1:0] axi_to_hbm_awcache,
    output logic [(AXI_HBM_NUM_IFS*  3)-1:0] axi_to_hbm_awprot,
    output logic [(AXI_HBM_NUM_IFS*  4)-1:0] axi_to_hbm_awqos,
    output logic [(AXI_HBM_NUM_IFS*  4)-1:0] axi_to_hbm_awregion,
    output logic [(AXI_HBM_NUM_IFS*  1)-1:0] axi_to_hbm_awvalid,
    input  logic [(AXI_HBM_NUM_IFS*  1)-1:0] axi_to_hbm_awready,
    output logic [(AXI_HBM_NUM_IFS*  6)-1:0] axi_to_hbm_wid,
    output logic [(AXI_HBM_NUM_IFS*256)-1:0] axi_to_hbm_wdata,
    output logic [(AXI_HBM_NUM_IFS* 32)-1:0] axi_to_hbm_wstrb,
    output logic [(AXI_HBM_NUM_IFS*  1)-1:0] axi_to_hbm_wlast,
    output logic [(AXI_HBM_NUM_IFS*  1)-1:0] axi_to_hbm_wvalid,
    input  logic [(AXI_HBM_NUM_IFS*  1)-1:0] axi_to_hbm_wready,
    input  logic [(AXI_HBM_NUM_IFS*  6)-1:0] axi_to_hbm_bid,
    input  logic [(AXI_HBM_NUM_IFS*  2)-1:0] axi_to_hbm_bresp,
    input  logic [(AXI_HBM_NUM_IFS*  1)-1:0] axi_to_hbm_bvalid,
    output logic [(AXI_HBM_NUM_IFS*  1)-1:0] axi_to_hbm_bready,
    output logic [(AXI_HBM_NUM_IFS*  6)-1:0] axi_to_hbm_arid,
    output logic [(AXI_HBM_NUM_IFS* 33)-1:0] axi_to_hbm_araddr,
    output logic [(AXI_HBM_NUM_IFS*  4)-1:0] axi_to_hbm_arlen,
    output logic [(AXI_HBM_NUM_IFS*  3)-1:0] axi_to_hbm_arsize,
    output logic [(AXI_HBM_NUM_IFS*  2)-1:0] axi_to_hbm_arburst,
    output logic [(AXI_HBM_NUM_IFS*  2)-1:0] axi_to_hbm_arlock,
    output logic [(AXI_HBM_NUM_IFS*  4)-1:0] axi_to_hbm_arcache,
    output logic [(AXI_HBM_NUM_IFS*  3)-1:0] axi_to_hbm_arprot,
    output logic [(AXI_HBM_NUM_IFS*  4)-1:0] axi_to_hbm_arqos,
    output logic [(AXI_HBM_NUM_IFS*  4)-1:0] axi_to_hbm_arregion,
    output logic [(AXI_HBM_NUM_IFS*  1)-1:0] axi_to_hbm_arvalid,
    input  logic [(AXI_HBM_NUM_IFS*  1)-1:0] axi_to_hbm_arready,
    input  logic [(AXI_HBM_NUM_IFS*  6)-1:0] axi_to_hbm_rid,
    input  logic [(AXI_HBM_NUM_IFS*256)-1:0] axi_to_hbm_rdata,
    input  logic [(AXI_HBM_NUM_IFS*  2)-1:0] axi_to_hbm_rresp,
    input  logic [(AXI_HBM_NUM_IFS*  1)-1:0] axi_to_hbm_rlast,
    input  logic [(AXI_HBM_NUM_IFS*  1)-1:0] axi_to_hbm_rvalid,
    output logic [(AXI_HBM_NUM_IFS*  1)-1:0] axi_to_hbm_rready
);
    import axi4s_pkg::*;

    // Parameters
    localparam int  AXIS_DATA_BYTE_WID = 64;

    localparam int  AXI_HBM_DATA_BYTE_WID = 32;
    localparam int  AXI_HBM_ADDR_WID = 33;
    localparam type AXI_HBM_ID_T = logic[5:0];

    // Typedefs
    typedef logic[1:0] port_t;
    typedef logic[2:0] egr_tdest_t;

    typedef struct packed {
        logic [15:0] pid;
        logic        rss_enable;
        logic [11:0] rss_entropy;
    } tuser_smartnic_meta_t;

    // Interfaces
    axi4l_intf #() axil_if       ();
    axi4l_intf #() axil_sdnet_if ();

    axi4s_intf #(.DATA_BYTE_WID(AXIS_DATA_BYTE_WID),
                 .TID_T(port_t), .TDEST_T(egr_tdest_t), .TUSER_T(tuser_smartnic_meta_t)) axis_to_switch [2] ();

    tuser_smartnic_meta_t  axis_to_switch_0_tuser;
    assign axis_to_switch_0_tuser_pid         = axis_to_switch_0_tuser.pid;
    assign axis_to_switch_0_tuser_rss_enable  = axis_to_switch_0_tuser.rss_enable;
    assign axis_to_switch_0_tuser_rss_entropy = axis_to_switch_0_tuser.rss_entropy;

    tuser_smartnic_meta_t  axis_to_switch_1_tuser;
    assign axis_to_switch_1_tuser_pid         = axis_to_switch_1_tuser.pid;
    assign axis_to_switch_1_tuser_rss_enable  = axis_to_switch_1_tuser.rss_enable;
    assign axis_to_switch_1_tuser_rss_entropy = axis_to_switch_1_tuser.rss_entropy;

    axi4s_intf #(.DATA_BYTE_WID(AXIS_DATA_BYTE_WID),
                 .TID_T(port_t), .TDEST_T(port_t), .TUSER_T(tuser_smartnic_meta_t)) axis_from_switch [2] ();

    tuser_smartnic_meta_t  axis_from_switch_0_tuser;
    assign axis_from_switch_0_tuser.pid         = axis_from_switch_0_tuser_pid;
    assign axis_from_switch_0_tuser.rss_enable  = '0;
    assign axis_from_switch_0_tuser.rss_entropy = '0;

    tuser_smartnic_meta_t  axis_from_switch_1_tuser;
    assign axis_from_switch_1_tuser.pid         = axis_from_switch_1_tuser_pid;
    assign axis_from_switch_1_tuser.rss_enable  = '0;
    assign axis_from_switch_1_tuser.rss_entropy = '0;

    axi3_intf  #(
        .DATA_BYTE_WID(AXI_HBM_DATA_BYTE_WID), .ADDR_WID(AXI_HBM_ADDR_WID), .ID_T(AXI_HBM_ID_T)
    ) axi_to_hbm [AXI_HBM_NUM_IFS] ();

    // -------------------------------------------------------------------------------------------------------
    // MAP FROM 'FLAT' SIGNAL REPRESENTATION TO INTERFACE REPRESENTATION (COMMON TO ALL APPLICATIONS)
    // -------------------------------------------------------------------------------------------------------
    // -- AXI-L interface
    axi4l_intf_from_signals i_axi4l_intf_from_signals (
        .aclk     ( axil_aclk ),
        .aresetn  ( axil_aresetn ),
        .awvalid  ( axil_awvalid ),
        .awready  ( axil_awready ),
        .awaddr   ( axil_awaddr ),
        .awprot   ( axil_awprot ),
        .wvalid   ( axil_wvalid ),
        .wready   ( axil_wready ),
        .wdata    ( axil_wdata ),
        .wstrb    ( axil_wstrb ),
        .bvalid   ( axil_bvalid ),
        .bready   ( axil_bready ),
        .bresp    ( axil_bresp ),
        .arvalid  ( axil_arvalid ),
        .arready  ( axil_arready ),
        .araddr   ( axil_araddr ),
        .arprot   ( axil_arprot ),
        .rvalid   ( axil_rvalid ),
        .rready   ( axil_rready ),
        .rdata    ( axil_rdata ),
        .rresp    ( axil_rresp ),
        .axi4l_if ( axil_if )
    );
    // -- AXI-L interface to SDNet
    axi4l_intf_from_signals i_axi4l_intf_from_signals_sdnet (
        .aclk     ( axil_aclk ),
        .aresetn  ( axil_sdnet_aresetn ),
        .awvalid  ( axil_sdnet_awvalid ),
        .awready  ( axil_sdnet_awready ),
        .awaddr   ( axil_sdnet_awaddr ),
        .awprot   ( axil_sdnet_awprot ),
        .wvalid   ( axil_sdnet_wvalid ),
        .wready   ( axil_sdnet_wready ),
        .wdata    ( axil_sdnet_wdata ),
        .wstrb    ( axil_sdnet_wstrb ),
        .bvalid   ( axil_sdnet_bvalid ),
        .bready   ( axil_sdnet_bready ),
        .bresp    ( axil_sdnet_bresp ),
        .arvalid  ( axil_sdnet_arvalid ),
        .arready  ( axil_sdnet_arready ),
        .araddr   ( axil_sdnet_araddr ),
        .arprot   ( axil_sdnet_arprot ),
        .rvalid   ( axil_sdnet_rvalid ),
        .rready   ( axil_sdnet_rready ),
        .rdata    ( axil_sdnet_rdata ),
        .rresp    ( axil_sdnet_rresp ),
        .axi4l_if ( axil_sdnet_if )
    );
    // -- AXI-S interface from switch
    axi4s_intf_from_signals #(
        .DATA_BYTE_WID(AXIS_DATA_BYTE_WID), .TID_T(port_t), .TDEST_T(port_t), .TUSER_T(tuser_smartnic_meta_t)
    ) i_axi4s_intf_from_signals_from_switch_0 (
        .aclk    ( core_clk ),
        .aresetn ( core_rstn ),
        .tvalid  ( axis_from_switch_0_tvalid ),
        .tready  ( axis_from_switch_0_tready ),
        .tdata   ( axis_from_switch_0_tdata ),
        .tkeep   ( axis_from_switch_0_tkeep ),
        .tlast   ( axis_from_switch_0_tlast ),
        .tid     ( axis_from_switch_0_tid ),
        .tdest   ( axis_from_switch_0_tdest ),
        .tuser   ( axis_from_switch_0_tuser ),
        .axi4s_if( axis_from_switch[0] )
    );
    // -- AXI-S interface to switch
    axi4s_intf_to_signals #(
        .DATA_BYTE_WID(AXIS_DATA_BYTE_WID), .TID_T(port_t), .TDEST_T(egr_tdest_t), .TUSER_T(tuser_smartnic_meta_t)
    ) i_axi4s_to_signals_to_switch_0 (
        .aclk    ( ), // Output
        .aresetn ( ), // Output
        .tvalid  ( axis_to_switch_0_tvalid ),
        .tready  ( axis_to_switch_0_tready ),
        .tdata   ( axis_to_switch_0_tdata ),
        .tkeep   ( axis_to_switch_0_tkeep ),
        .tlast   ( axis_to_switch_0_tlast ),
        .tid     ( axis_to_switch_0_tid ),
        .tdest   ( axis_to_switch_0_tdest ),
        .tuser   ( axis_to_switch_0_tuser ),
        .axi4s_if( axis_to_switch[0] )
    );
    // -- AXI-S interface from host
    axi4s_intf_from_signals #(
        .DATA_BYTE_WID(AXIS_DATA_BYTE_WID), .TID_T(port_t), .TDEST_T(port_t), .TUSER_T(tuser_smartnic_meta_t)
    ) i_axi4s_from_signals_from_switch_1 (
        .aclk    ( core_clk ),
        .aresetn ( core_rstn ),
        .tvalid  ( axis_from_switch_1_tvalid ),
        .tready  ( axis_from_switch_1_tready ),
        .tdata   ( axis_from_switch_1_tdata ),
        .tkeep   ( axis_from_switch_1_tkeep ),
        .tlast   ( axis_from_switch_1_tlast ),
        .tid     ( axis_from_switch_1_tid ),
        .tdest   ( axis_from_switch_1_tdest ),
        .tuser   ( axis_from_switch_1_tuser ),
        .axi4s_if( axis_from_switch[1] )
    );
    // -- AXI-S interface to host
    axi4s_intf_to_signals #(
        .DATA_BYTE_WID(AXIS_DATA_BYTE_WID), .TID_T(port_t), .TDEST_T(egr_tdest_t), .TUSER_T(tuser_smartnic_meta_t)
    ) i_axi4s_to_signals_to_switch_1 (
        .aclk    ( ), // Output
        .aresetn ( ), // Output
        .tvalid  ( axis_to_switch_1_tvalid ),
        .tready  ( axis_to_switch_1_tready ),
        .tdata   ( axis_to_switch_1_tdata ),
        .tkeep   ( axis_to_switch_1_tkeep ),
        .tlast   ( axis_to_switch_1_tlast ),
        .tid     ( axis_to_switch_1_tid ),
        .tdest   ( axis_to_switch_1_tdest ),
        .tuser   ( axis_to_switch_1_tuser ),
        .axi4s_if( axis_to_switch[1] )
    );

    // -- AXI memory interfaces to HBM
    generate
        for (genvar g_hbm_if = 0; g_hbm_if < AXI_HBM_NUM_IFS; g_hbm_if++) begin : g__hbm_if
            axi3_intf_to_signals #(
                .DATA_BYTE_WID(AXI_HBM_DATA_BYTE_WID),
                .ADDR_WID     (AXI_HBM_ADDR_WID),
                .ID_T         (AXI_HBM_ID_T)
            ) i_axi3_intf_to_signals__hbm (
                .axi3_if  ( axi_to_hbm [g_hbm_if] ),
                .aclk     ( axi_to_hbm_aclk    [g_hbm_if*  1 +:   1] ),
                .aresetn  ( axi_to_hbm_aresetn [g_hbm_if*  1 +:   1] ),
                .awid     ( axi_to_hbm_awid    [g_hbm_if*  6 +:   6] ),
                .awaddr   ( axi_to_hbm_awaddr  [g_hbm_if* 33 +:  33] ),
                .awlen    ( axi_to_hbm_awlen   [g_hbm_if*  4 +:   4] ),
                .awsize   ( axi_to_hbm_awsize  [g_hbm_if*  3 +:   3] ),
                .awburst  ( axi_to_hbm_awburst [g_hbm_if*  2 +:   2] ),
                .awlock   ( axi_to_hbm_awlock  [g_hbm_if*  2 +:   2] ),
                .awcache  ( axi_to_hbm_awcache [g_hbm_if*  4 +:   4] ),
                .awprot   ( axi_to_hbm_awprot  [g_hbm_if*  3 +:   3] ),
                .awqos    ( axi_to_hbm_awqos   [g_hbm_if*  4 +:   4] ),
                .awregion ( axi_to_hbm_awregion[g_hbm_if*  4 +:   4] ),
                .awuser   (                                          ), // Unused
                .awvalid  ( axi_to_hbm_awvalid [g_hbm_if*  1 +:   1] ),
                .awready  ( axi_to_hbm_awready [g_hbm_if*  1 +:   1] ),
                .wid      ( axi_to_hbm_wid     [g_hbm_if*  6 +:   6] ),
                .wdata    ( axi_to_hbm_wdata   [g_hbm_if*256 +: 256] ),
                .wstrb    ( axi_to_hbm_wstrb   [g_hbm_if* 32 +:  32] ),
                .wlast    ( axi_to_hbm_wlast   [g_hbm_if*  1 +:   1] ),
                .wuser    (                                          ), // Unused
                .wvalid   ( axi_to_hbm_wvalid  [g_hbm_if*  1 +:   1] ),
                .wready   ( axi_to_hbm_wready  [g_hbm_if*  1 +:   1] ),
                .bid      ( axi_to_hbm_bid     [g_hbm_if*  6 +:   6] ),
                .bresp    ( axi_to_hbm_bresp   [g_hbm_if*  2 +:   2] ),
                .buser    ( '0                                       ), // Unused
                .bvalid   ( axi_to_hbm_bvalid  [g_hbm_if*  1 +:   1] ),
                .bready   ( axi_to_hbm_bready  [g_hbm_if*  1 +:   1] ),
                .arid     ( axi_to_hbm_arid    [g_hbm_if*  6 +:   6] ),
                .araddr   ( axi_to_hbm_araddr  [g_hbm_if* 33 +:  33] ),
                .arlen    ( axi_to_hbm_arlen   [g_hbm_if*  4 +:   4] ),
                .arsize   ( axi_to_hbm_arsize  [g_hbm_if*  3 +:   3] ),
                .arburst  ( axi_to_hbm_arburst [g_hbm_if*  2 +:   2] ),
                .arlock   ( axi_to_hbm_arlock  [g_hbm_if*  2 +:   2] ),
                .arcache  ( axi_to_hbm_arcache [g_hbm_if*  4 +:   4] ),
                .arprot   ( axi_to_hbm_arprot  [g_hbm_if*  3 +:   3] ),
                .arqos    ( axi_to_hbm_arqos   [g_hbm_if*  4 +:   4] ),
                .arregion ( axi_to_hbm_arregion[g_hbm_if*  4 +:   4] ),
                .aruser   (                                          ), // Unused
                .arvalid  ( axi_to_hbm_arvalid [g_hbm_if*  1 +:   1] ),
                .arready  ( axi_to_hbm_arready [g_hbm_if*  1 +:   1] ),
                .rid      ( axi_to_hbm_rid     [g_hbm_if*  6 +:   6] ),
                .rdata    ( axi_to_hbm_rdata   [g_hbm_if*256 +: 256] ),
                .rresp    ( axi_to_hbm_rresp   [g_hbm_if*  2 +:   2] ),
                .rlast    ( axi_to_hbm_rlast   [g_hbm_if*  1 +:   1] ),
                .ruser    ( '0                                       ), // Unused
                .rvalid   ( axi_to_hbm_rvalid  [g_hbm_if*  1 +:   1] ),
                .rready   ( axi_to_hbm_rready  [g_hbm_if*  1 +:   1] )
            );
        end : g__hbm_if
    endgenerate

    // -------------------------------------------------------------------------------------------------------
    // APPLICATION-SPECIFIC CONNECTIVITY
    // -------------------------------------------------------------------------------------------------------
    p4_and_verilog p4_and_verilog_0
    (
        .core_clk      ( core_clk ),
        .core_rstn     ( core_rstn ),
        .timestamp     ( timestamp ),

        .axil_if       ( axil_if ),
        .axil_to_sdnet ( axil_sdnet_if ),

        .axis_to_switch_0    ( axis_to_switch[0] ),
        .axis_from_switch_0  ( axis_from_switch[0] ),
        .axis_to_switch_1    ( axis_to_switch[1] ),
        .axis_from_switch_1  ( axis_from_switch[1] )
    );

    // Terminate AXI HBM interfaces (unused)
    generate
        for (genvar g_hbm_if = 0; g_hbm_if < AXI_HBM_NUM_IFS; g_hbm_if++) begin : g__axi_if_tieoff
            axi3_intf_controller_term i_axi3_controller_term (
                .axi3_if ( axi_to_hbm[g_hbm_if] )
            );
        end : g__axi_if_tieoff
    endgenerate

endmodule: smartnic_322mhz_app
