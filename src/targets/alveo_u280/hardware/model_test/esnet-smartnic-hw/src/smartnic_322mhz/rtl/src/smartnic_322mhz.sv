`define getbit(width, index, offset)    ((index)*(width) + (offset))
`define getvec(width, index)            ((index)*(width)) +: (width)

`timescale 1ns/1ps

module smartnic_322mhz
#(
  parameter int NUM_CMAC = 2,
  parameter int MAX_PKT_LEN = 9100,
`ifdef SIMULATION
  parameter bit INCLUDE_HBM0 = 1'b1,
  parameter bit INCLUDE_HBM1 = 1'b1
`else
  parameter bit INCLUDE_HBM0 = smartnic_322mhz_app_pkg::INCLUDE_HBM, // Application-specific HBM controller include/exclude
                                     // HBM0 controller is connected to application logic
                                     // (can be excluded for non-HBM applications to optimize resources/complexity)
  parameter bit INCLUDE_HBM1 = 1'b0  // HBM1 is connected to platform logic
                                     // (it is excluded by default because HBM is not currently used to implement any platform functions)
`endif
) (
  input                       s_axil_awvalid,
  input [31:0]                s_axil_awaddr,
  output                      s_axil_awready,
  input                       s_axil_wvalid,
  input [31:0]                s_axil_wdata,
  output                      s_axil_wready,
  output                      s_axil_bvalid,
  output [1:0]                s_axil_bresp,
  input                       s_axil_bready,
  input                       s_axil_arvalid,
  input [31:0]                s_axil_araddr,
  output                      s_axil_arready,
  output                      s_axil_rvalid,
  output [31:0]               s_axil_rdata,
  output [1:0]                s_axil_rresp,
  input                       s_axil_rready,

  input [NUM_CMAC-1:0]        s_axis_adpt_tx_322mhz_tvalid,
  input [(512*NUM_CMAC)-1:0]  s_axis_adpt_tx_322mhz_tdata,
  input [(64*NUM_CMAC)-1:0]   s_axis_adpt_tx_322mhz_tkeep,
  input [NUM_CMAC-1:0]        s_axis_adpt_tx_322mhz_tlast,
  input [(2*NUM_CMAC)-1:0]    s_axis_adpt_tx_322mhz_tdest,
  input [NUM_CMAC-1:0]        s_axis_adpt_tx_322mhz_tuser_err,
  output [NUM_CMAC-1:0]       s_axis_adpt_tx_322mhz_tready,

  output [NUM_CMAC-1:0]       m_axis_adpt_rx_322mhz_tvalid,
  output [(512*NUM_CMAC)-1:0] m_axis_adpt_rx_322mhz_tdata,
  output [(64*NUM_CMAC)-1:0]  m_axis_adpt_rx_322mhz_tkeep,
  output [NUM_CMAC-1:0]       m_axis_adpt_rx_322mhz_tlast,
  output [(2*NUM_CMAC)-1:0]   m_axis_adpt_rx_322mhz_tdest,
  output [NUM_CMAC-1:0]       m_axis_adpt_rx_322mhz_tuser_err,
  output [NUM_CMAC-1:0]       m_axis_adpt_rx_322mhz_tuser_rss_enable,
  output [(12*NUM_CMAC)-1:0]  m_axis_adpt_rx_322mhz_tuser_rss_entropy,
  input [NUM_CMAC-1:0]        m_axis_adpt_rx_322mhz_tready,

  output [NUM_CMAC-1:0]       m_axis_cmac_tx_322mhz_tvalid,
  output [(512*NUM_CMAC)-1:0] m_axis_cmac_tx_322mhz_tdata,
  output [(64*NUM_CMAC)-1:0]  m_axis_cmac_tx_322mhz_tkeep,
  output [NUM_CMAC-1:0]       m_axis_cmac_tx_322mhz_tlast,
  output [(2*NUM_CMAC)-1:0]   m_axis_cmac_tx_322mhz_tdest,
  output [NUM_CMAC-1:0]       m_axis_cmac_tx_322mhz_tuser_err,
  input [NUM_CMAC-1:0]        m_axis_cmac_tx_322mhz_tready,

  input [NUM_CMAC-1:0]        s_axis_cmac_rx_322mhz_tvalid,
  input [(512*NUM_CMAC)-1:0]  s_axis_cmac_rx_322mhz_tdata,
  input [(64*NUM_CMAC)-1:0]   s_axis_cmac_rx_322mhz_tkeep,
  input [NUM_CMAC-1:0]        s_axis_cmac_rx_322mhz_tlast,
  input [(2*NUM_CMAC)-1:0]    s_axis_cmac_rx_322mhz_tdest,
  input [NUM_CMAC-1:0]        s_axis_cmac_rx_322mhz_tuser_err,
  output [NUM_CMAC-1:0]       s_axis_cmac_rx_322mhz_tready,

  input                       mod_rstn,
  output                      mod_rst_done,

  input                       axil_aclk,
  input                       axis_aclk,
  input [NUM_CMAC-1:0]        cmac_clk
);

   // Imports
  import smartnic_322mhz_pkg::*;
  import smartnic_322mhz_reg_pkg::*;
  import axi4s_pkg::*;

   // Signals
   wire                       axil_aresetn;
   wire [NUM_CMAC-1:0]        cmac_rstn;

   wire                       core_rstn;
   wire                       core_clk;

   wire                       clk_100mhz;
   wire                       hbm_ref_clk;

   tuser_smartnic_meta_t      m_axis_adpt_rx_322mhz_tuser [NUM_CMAC];

   logic [2*NUM_CMAC-1:0]     egr_flow_ctl, egr_flow_ctl_pipe[3];


  // Reset is clocked by the 125MHz AXI-Lite clock

  smartnic_322mhz_reset #(
    .NUM_CMAC (NUM_CMAC)
  ) reset_inst (
    .mod_rstn     (mod_rstn),
    .mod_rst_done (mod_rst_done),

    .axil_aresetn (axil_aresetn),
    .cmac_rstn    (cmac_rstn),
    .axil_aclk    (axil_aclk),
    .cmac_clk     (cmac_clk),

    .core_rstn    (core_rstn),
    .core_clk     (core_clk),

    .clk_100mhz   (clk_100mhz),
    .hbm_ref_clk  (hbm_ref_clk)
  );

   // ----------------------------------------------------------------
   //  axil interface instantiations and regmap logic
   // ----------------------------------------------------------------

   axi4l_intf   s_axil_if                   ();
   axi4l_intf   axil_to_regs                ();
   axi4l_intf   axil_to_endian_check        ();
   axi4l_intf   axil_to_hbm_0               ();
   axi4l_intf   axil_to_hbm_1               ();
   axi4l_intf   axil_to_app_decoder__demarc ();
   axi4l_intf   axil_to_app_decoder         ();
   axi4l_intf   axil_to_app                 ();
   axi4l_intf   axil_to_sdnet               ();
   axi4l_intf   axil_to_split_join          ();

   axi4l_intf   axil_to_probe_from_cmac [NUM_CMAC] ();
   axi4l_intf   axil_to_ovfl_from_cmac  [NUM_CMAC] ();
   axi4l_intf   axil_to_err_from_cmac   [NUM_CMAC] ();
   axi4l_intf   axil_to_probe_from_host [NUM_CMAC] ();
   axi4l_intf   axil_to_ovfl_from_host  [NUM_CMAC] ();

   axi4l_intf   axil_to_probe_to_cmac   [NUM_CMAC] ();
   axi4l_intf   axil_to_ovfl_to_cmac    [NUM_CMAC] ();
   axi4l_intf   axil_to_probe_to_host   [NUM_CMAC] ();
   axi4l_intf   axil_to_ovfl_to_host    [NUM_CMAC] ();

   axi4l_intf   axil_to_fifo_to_cmac    [NUM_CMAC] ();
   axi4l_intf   axil_to_fifo_from_cmac  [NUM_CMAC] ();
   axi4l_intf   axil_to_fifo_to_host    [NUM_CMAC] ();
   axi4l_intf   axil_to_fifo_from_host  [NUM_CMAC] ();

   axi4l_intf   axil_to_core_to_app [2]            ();
   axi4l_intf   axil_to_app_to_core [2]            ();

   axi4l_intf   axil_to_probe_to_bypass            ();
   axi4l_intf   axil_to_ovfl_to_bypass             ();
   axi4l_intf   axil_to_fifo_to_bypass             ();

   axi4l_intf   axil_to_drops_from_igr_sw          ();
   axi4l_intf   axil_to_drops_from_bypass          ();
   axi4l_intf   axil_to_drops_from_app0            ();

   smartnic_322mhz_reg_intf   smartnic_322mhz_regs ();


   // Convert Xilinx AXI-L signals to interface format
   axi4l_intf_from_signals s_axil_from_signals_0 (
      // Signals (from controller)
      .aclk     (axil_aclk),
      .aresetn  (axil_aresetn),
      .awaddr   (s_axil_awaddr),
      .awprot   (3'b000),
      .awvalid  (s_axil_awvalid),
      .awready  (s_axil_awready),
      .wdata    (s_axil_wdata),
      .wstrb    (4'b1111),
      .wvalid   (s_axil_wvalid),
      .wready   (s_axil_wready),
      .bresp    (s_axil_bresp),
      .bvalid   (s_axil_bvalid),
      .bready   (s_axil_bready),
      .araddr   (s_axil_araddr),
      .arprot   (3'b000),
      .arvalid  (s_axil_arvalid),
      .arready  (s_axil_arready),
      .rdata    (s_axil_rdata),
      .rresp    (s_axil_rresp),
      .rvalid   (s_axil_rvalid),
      .rready   (s_axil_rready),

      // Interface (to peripheral)
      .axi4l_if (s_axil_if)
   );

   // smartnic_322mhz top-level decoder
   smartnic_322mhz_decoder smartnic_322mhz_axil_decoder_0 (
      .axil_if                         (s_axil_if),
      .smartnic_322mhz_regs_axil_if    (axil_to_regs),
      .endian_check_axil_if            (axil_to_endian_check),
      .probe_from_cmac_0_axil_if       (axil_to_probe_from_cmac[0]),
      .drops_ovfl_from_cmac_0_axil_if  (axil_to_ovfl_from_cmac[0]),
      .drops_err_from_cmac_0_axil_if   (axil_to_err_from_cmac[0]),
      .probe_from_cmac_1_axil_if       (axil_to_probe_from_cmac[1]),
      .drops_ovfl_from_cmac_1_axil_if  (axil_to_ovfl_from_cmac[1]),
      .drops_err_from_cmac_1_axil_if   (axil_to_err_from_cmac[1]),
      .probe_from_host_0_axil_if       (axil_to_probe_from_host[0]),
      .probe_from_host_1_axil_if       (axil_to_probe_from_host[1]),
      .probe_core_to_app0_axil_if      (axil_to_core_to_app[0]),
      .probe_core_to_app1_axil_if      (axil_to_core_to_app[1]),
      .probe_app0_to_core_axil_if      (axil_to_app_to_core[0]),
      .probe_app1_to_core_axil_if      (axil_to_app_to_core[1]),
      .probe_to_cmac_0_axil_if         (axil_to_probe_to_cmac[0]),
      .drops_ovfl_to_cmac_0_axil_if    (axil_to_ovfl_to_cmac[0]),
      .probe_to_cmac_1_axil_if         (axil_to_probe_to_cmac[1]),
      .drops_ovfl_to_cmac_1_axil_if    (axil_to_ovfl_to_cmac[1]),
      .probe_to_host_0_axil_if         (axil_to_probe_to_host[0]),
      .drops_ovfl_to_host_0_axil_if    (axil_to_ovfl_to_host[0]),
      .probe_to_host_1_axil_if         (axil_to_probe_to_host[1]),
      .drops_ovfl_to_host_1_axil_if    (axil_to_ovfl_to_host[1]),
      .probe_to_bypass_axil_if         (axil_to_probe_to_bypass),
      .drops_from_igr_sw_axil_if       (axil_to_drops_from_igr_sw),
      .drops_from_bypass_axil_if       (axil_to_drops_from_bypass),
      .drops_from_app0_axil_if         (axil_to_drops_from_app0),
      .fifo_to_host_0_axil_if          (axil_to_fifo_to_host[0]),
      .hbm_0_axil_if                   (axil_to_hbm_0),
      .hbm_1_axil_if                   (axil_to_hbm_1),
      .axi4s_split_join_axil_if        (axil_to_split_join),
      .smartnic_322mhz_app_axil_if     (axil_to_app_decoder__demarc)
   );

   // AXI-L interface synchronizer
   axi4l_intf axil_to_regs__core_clk ();

   axi4l_intf_cdc axil_to_regs_cdc (
      .axi4l_if_from_controller  ( axil_to_regs ),
      .clk_to_peripheral         ( core_clk ),
      .axi4l_if_to_peripheral    ( axil_to_regs__core_clk )
   );

   // smartnic_322mhz register block
   smartnic_322mhz_reg_blk     smartnic_322mhz_reg_blk_0
   (
    .axil_if    (axil_to_regs__core_clk),
    .reg_blk_if (smartnic_322mhz_regs)
   );

   // Endian check reg block
   reg_endian_check reg_endian_check_0 (
       .axil_if (axil_to_endian_check)
   );

   // Timestamp counter and access logic
   logic [63:0] timestamp;

   smartnic_322mhz_timestamp  smartnic_322mhz_timestamp_0 (
     .clk               (core_clk),
     .rstn              (core_rstn),
     .timestamp         (timestamp),
     .smartnic_322mhz_regs (smartnic_322mhz_regs)
   );

   // axis_to_host_tpause synchronizers
   logic axis_to_host_tpause [NUM_CMAC];

   sync_level sync_level_0 (
      .lvl_in  ( smartnic_322mhz_regs.switch_config.axis_to_host_0_tpause ),
      .clk_out ( cmac_clk[0] ),
      .rst_out ( 1'b0 ),
      .lvl_out ( axis_to_host_tpause[0] )
   );

   sync_level sync_level_1 (
      .lvl_in  ( smartnic_322mhz_regs.switch_config.axis_to_host_1_tpause ),
      .clk_out ( cmac_clk[1] ),
      .rst_out ( 1'b0 ),
      .lvl_out ( axis_to_host_tpause[1] )
   );

   // ----------------------------------------------------------------
   //  HBM0 (Left stack, 4GB)
   //
   //  (Optionally) used by application
   // ----------------------------------------------------------------
   // Signals
   logic [15:0]        axi_app_to_hbm_aclk;
   logic [15:0]        axi_app_to_hbm_aresetn;
   logic [15:0][5:0]   axi_app_to_hbm_awid;
   logic [15:0][32:0]  axi_app_to_hbm_awaddr;
   logic [15:0][3:0]   axi_app_to_hbm_awlen;
   logic [15:0][2:0]   axi_app_to_hbm_awsize;
   logic [15:0][1:0]   axi_app_to_hbm_awburst;
   logic [15:0][1:0]   axi_app_to_hbm_awlock;
   logic [15:0][3:0]   axi_app_to_hbm_awcache;
   logic [15:0][2:0]   axi_app_to_hbm_awprot;
   logic [15:0][3:0]   axi_app_to_hbm_awqos;
   logic [15:0][3:0]   axi_app_to_hbm_awregion;
   logic [15:0]        axi_app_to_hbm_awuser;
   logic [15:0]        axi_app_to_hbm_awvalid;
   logic [15:0]        axi_app_to_hbm_awready;
   logic [15:0][5:0]   axi_app_to_hbm_wid;
   logic [15:0][255:0] axi_app_to_hbm_wdata;
   logic [15:0][31:0]  axi_app_to_hbm_wstrb;
   logic [15:0]        axi_app_to_hbm_wlast;
   logic [15:0]        axi_app_to_hbm_wuser;
   logic [15:0]        axi_app_to_hbm_wvalid;
   logic [15:0]        axi_app_to_hbm_wready;
   logic [15:0][5:0]   axi_app_to_hbm_bid;
   logic [15:0][1:0]   axi_app_to_hbm_bresp;
   logic [15:0]        axi_app_to_hbm_buser;
   logic [15:0]        axi_app_to_hbm_bvalid;
   logic [15:0]        axi_app_to_hbm_bready;
   logic [15:0][5:0]   axi_app_to_hbm_arid;
   logic [15:0][32:0]  axi_app_to_hbm_araddr;
   logic [15:0][3:0]   axi_app_to_hbm_arlen;
   logic [15:0][2:0]   axi_app_to_hbm_arsize;
   logic [15:0][1:0]   axi_app_to_hbm_arburst;
   logic [15:0][1:0]   axi_app_to_hbm_arlock;
   logic [15:0][3:0]   axi_app_to_hbm_arcache;
   logic [15:0][2:0]   axi_app_to_hbm_arprot;
   logic [15:0][3:0]   axi_app_to_hbm_arqos;
   logic [15:0][3:0]   axi_app_to_hbm_arregion;
   logic [15:0]        axi_app_to_hbm_aruser;
   logic [15:0]        axi_app_to_hbm_arvalid;
   logic [15:0]        axi_app_to_hbm_arready;
   logic [15:0][5:0]   axi_app_to_hbm_rid;
   logic [15:0][255:0] axi_app_to_hbm_rdata;
   logic [15:0][1:0]   axi_app_to_hbm_rresp;
   logic [15:0]        axi_app_to_hbm_rlast;
   logic [15:0]        axi_app_to_hbm_ruser;
   logic [15:0]        axi_app_to_hbm_rvalid;
   logic [15:0]        axi_app_to_hbm_rready;

   generate
       if (INCLUDE_HBM0) begin : g__hbm_0
           // Include memory controller for 'Left' HBM stack (4GB)

           // (Local) interfaces
           axi3_intf   #(.DATA_BYTE_WID(32), .ADDR_WID(33), .ID_T(logic[5:0])) axi_if_from_app [16] ();

           // HBM controller
           smartnic_322mhz_hbm #(
             .HBM_STACK   ( 0 )
           ) smartnic_322mhz_hbm_0 (
             .clk         ( core_clk ),
             .rstn        ( core_rstn ),
             .hbm_ref_clk ( hbm_ref_clk ),
             .clk_100mhz  ( clk_100mhz ),
             .axil_if     ( axil_to_hbm_0 ),
             .axi_if      ( axi_if_from_app )
           );

           //  Map HBM0 memory interface signals into interface representation
           for (genvar g_hbm_if = 0; g_hbm_if < 16; g_hbm_if++) begin : g__hbm_if
               // (Local) interfaces
               axi3_intf   #(.DATA_BYTE_WID(32), .ADDR_WID(33), .ID_T(logic[5:0])) axi_if_from_app__demarc ();

               axi3_intf_from_signals #(
                   .DATA_BYTE_WID(32),
                   .ADDR_WID     (33),
                   .ID_T         (logic[5:0])
               ) axi3_intf_from_signals__hbm (
                   .aclk     ( axi_app_to_hbm_aclk    [g_hbm_if] ),
                   .aresetn  ( axi_app_to_hbm_aresetn [g_hbm_if] ),
                   .awid     ( axi_app_to_hbm_awid    [g_hbm_if] ),
                   .awaddr   ( axi_app_to_hbm_awaddr  [g_hbm_if] ),
                   .awlen    ( axi_app_to_hbm_awlen   [g_hbm_if] ),
                   .awsize   ( axi_app_to_hbm_awsize  [g_hbm_if] ),
                   .awburst  ( axi_app_to_hbm_awburst [g_hbm_if] ),
                   .awlock   ( axi_app_to_hbm_awlock  [g_hbm_if] ),
                   .awcache  ( axi_app_to_hbm_awcache [g_hbm_if] ),
                   .awprot   ( axi_app_to_hbm_awprot  [g_hbm_if] ),
                   .awqos    ( axi_app_to_hbm_awqos   [g_hbm_if] ),
                   .awregion ( axi_app_to_hbm_awregion[g_hbm_if] ),
                   .awuser   ( axi_app_to_hbm_awuser  [g_hbm_if] ),
                   .awvalid  ( axi_app_to_hbm_awvalid [g_hbm_if] ),
                   .awready  ( axi_app_to_hbm_awready [g_hbm_if] ),
                   .wid      ( axi_app_to_hbm_wid     [g_hbm_if] ),
                   .wdata    ( axi_app_to_hbm_wdata   [g_hbm_if] ),
                   .wstrb    ( axi_app_to_hbm_wstrb   [g_hbm_if] ),
                   .wlast    ( axi_app_to_hbm_wlast   [g_hbm_if] ),
                   .wuser    ( axi_app_to_hbm_wuser   [g_hbm_if] ),
                   .wvalid   ( axi_app_to_hbm_wvalid  [g_hbm_if] ),
                   .wready   ( axi_app_to_hbm_wready  [g_hbm_if] ),
                   .bid      ( axi_app_to_hbm_bid     [g_hbm_if] ),
                   .bresp    ( axi_app_to_hbm_bresp   [g_hbm_if] ),
                   .buser    ( axi_app_to_hbm_buser   [g_hbm_if] ),
                   .bvalid   ( axi_app_to_hbm_bvalid  [g_hbm_if] ),
                   .bready   ( axi_app_to_hbm_bready  [g_hbm_if] ),
                   .arid     ( axi_app_to_hbm_arid    [g_hbm_if] ),
                   .araddr   ( axi_app_to_hbm_araddr  [g_hbm_if] ),
                   .arlen    ( axi_app_to_hbm_arlen   [g_hbm_if] ),
                   .arsize   ( axi_app_to_hbm_arsize  [g_hbm_if] ),
                   .arburst  ( axi_app_to_hbm_arburst [g_hbm_if] ),
                   .arlock   ( axi_app_to_hbm_arlock  [g_hbm_if] ),
                   .arcache  ( axi_app_to_hbm_arcache [g_hbm_if] ),
                   .arprot   ( axi_app_to_hbm_arprot  [g_hbm_if] ),
                   .arqos    ( axi_app_to_hbm_arqos   [g_hbm_if] ),
                   .arregion ( axi_app_to_hbm_arregion[g_hbm_if] ),
                   .aruser   ( axi_app_to_hbm_aruser  [g_hbm_if] ),
                   .arvalid  ( axi_app_to_hbm_arvalid [g_hbm_if] ),
                   .arready  ( axi_app_to_hbm_arready [g_hbm_if] ),
                   .rid      ( axi_app_to_hbm_rid     [g_hbm_if] ),
                   .rdata    ( axi_app_to_hbm_rdata   [g_hbm_if] ),
                   .rresp    ( axi_app_to_hbm_rresp   [g_hbm_if] ),
                   .rlast    ( axi_app_to_hbm_rlast   [g_hbm_if] ),
                   .ruser    ( axi_app_to_hbm_ruser   [g_hbm_if] ),
                   .rvalid   ( axi_app_to_hbm_rvalid  [g_hbm_if] ),
                   .rready   ( axi_app_to_hbm_rready  [g_hbm_if] ),
                   .axi3_if  ( axi_if_from_app__demarc )
               );

               assign axi_app_to_hbm_aclk[g_hbm_if] = core_clk;
               assign axi_app_to_hbm_aresetn[g_hbm_if] = core_rstn;

               // Inter-SLR pipelining
               axi3_reg_slice #(
                   .ADDR_WID      ( 33 ),
                   .DATA_BYTE_WID ( 32 ),
                   .ID_T          ( logic[5:0] ),
                   .CONFIG        ( xilinx_axi_pkg::XILINX_AXI_REG_SLICE_MULTI_SLR_CROSSING )
               ) axi3_reg_slice_inst (
                   .axi3_if_from_controller ( axi_if_from_app__demarc ),
                   .axi3_if_to_peripheral   ( axi_if_from_app[g_hbm_if] )
               );

           end : g__hbm_if
       end : g__hbm_0
       else begin : g__no_hbm_0
           // No HBM0 controller

           // Terminate AXI memory interfaces
           for (genvar g_hbm_if = 0; g_hbm_if < 16; g_hbm_if++) begin : g__hbm_if
               assign axi_app_to_hbm_awready[g_hbm_if] = 1'b0;
               assign axi_app_to_hbm_wready[g_hbm_if] = 1'b0;
               assign axi_app_to_hbm_bid[g_hbm_if] = '0;
               assign axi_app_to_hbm_bresp[g_hbm_if] = axi3_pkg::RESP_SLVERR;
               assign axi_app_to_hbm_buser[g_hbm_if] = '0;
               assign axi_app_to_hbm_bvalid[g_hbm_if] = 1'b0;
               assign axi_app_to_hbm_arready[g_hbm_if] = 1'b0;
               assign axi_app_to_hbm_rid[g_hbm_if] = '0;
               assign axi_app_to_hbm_rdata[g_hbm_if] = '0;
               assign axi_app_to_hbm_rresp[g_hbm_if] = axi3_pkg::RESP_SLVERR;
               assign axi_app_to_hbm_rlast[g_hbm_if] = 1'b0;
               assign axi_app_to_hbm_ruser[g_hbm_if] = '0;
               assign axi_app_to_hbm_rvalid[g_hbm_if] = 1'b0;
           end : g__hbm_if

           // Terminate AXI-L interface
           axi4l_intf_peripheral_term i_axi4l_peripheral_term (.axi4l_if (axil_to_hbm_0));
       end : g__no_hbm_0
   endgenerate

   // ----------------------------------------------------------------
   //  HBM1 (Right stack, 4GB)
   //
   //  (Optionally) used by platform
   // ----------------------------------------------------------------
   generate
       if (INCLUDE_HBM1) begin : g__hbm_1
           // Include memory controller for 'Right' HBM stack (4GB)

           // (Local) interfaces
           axi3_intf   #(.DATA_BYTE_WID(32), .ADDR_WID(33), .ID_T(logic[5:0])) axi_if[16] ();

           // HBM controller
           smartnic_322mhz_hbm #(
             .HBM_STACK   (1)
           ) smartnic_322mhz_hbm_1 (
             .clk         (core_clk),
             .rstn        (core_rstn),
             .hbm_ref_clk (hbm_ref_clk),
             .clk_100mhz  (clk_100mhz),
             .axil_if     (axil_to_hbm_1),
             .axi_if      (axi_if)
           );

           for (genvar g_hbm_if = 0; g_hbm_if < 16; g_hbm_if++) begin : g__hbm_if
               // For now, terminate HBM1 memory interfaces (unused)
               axi3_intf_controller_term axi_to_hbm_1_term (.axi3_if(axi_if[g_hbm_if]));
           end : g__hbm_if
       end : g__hbm_1
       else begin : g__no_hbm_1
           // No HBM 1 controller

           // Terminate AXI-L interface
           axi4l_intf_peripheral_term i_axi4l_peripheral_term (.axi4l_if (axil_to_hbm_1));
       end : g__no_hbm_1
   endgenerate

   // ----------------------------------------------------------------
   //  axi4s interface instantiations
   // ----------------------------------------------------------------

   axi4s_intf  #(.MODE(IGNORES_TREADY), .TUSER_MODE(PKT_ERROR),
                 .DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(port_t))         axis_from_cmac    [NUM_CMAC] ();
   axi4s_intf  #(.DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(port_t))         axis_from_host    [NUM_CMAC] ();
   axi4s_intf  #(.DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(port_t))         axis_cmac_to_core [NUM_CMAC] ();
   axi4s_intf  #(.DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(port_t))         axis_host_to_core [NUM_CMAC] ();

   logic axis_core_to_bypass_tready, axis_core_to_bypass_tvalid;

   axi4s_intf  #(.DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(port_t))         axis_core_to_bypass ();
   axi4s_intf  #(.DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(port_t))         axis_igr_sw_drop ();
   axi4s_intf  #(.DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(port_t))         axis_to_bypass_fifo ();
   axi4s_intf  #(.DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(port_t))         axis_from_bypass_fifo ();
   axi4s_intf  #(.DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(port_t))         axis_from_bypass_fifo_pipe ();
   axi4s_intf  #(.DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(port_t))         axis_to_bypass_drop ();
   axi4s_intf  #(.DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(port_t))         axis_bypass_to_core ();

   axi4s_intf  #(.TUSER_T(tuser_smartnic_meta_t),
                 .DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(egr_tdest_t))    axis_core_to_app [2] ();
   axi4s_intf  #(.TUSER_T(tuser_smartnic_meta_t),
                 .DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(port_t))         axis_to_app__demarc [2] ();
   axi4s_intf  #(.TUSER_T(tuser_smartnic_meta_t),
                 .DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(port_t))         axis_to_app [2] ();

   tuser_smartnic_meta_t axis_to_app_tuser [2];
   assign axis_to_app_tuser[0] = axis_to_app[0].tuser;
   assign axis_to_app_tuser[1] = axis_to_app[1].tuser;

   tuser_smartnic_meta_t axis_from_app_tuser [2];
   assign axis_from_app[0].tuser = axis_from_app_tuser[0];
   assign axis_from_app[1].tuser = axis_from_app_tuser[1];

   axi4s_intf  #(.TUSER_T(tuser_smartnic_meta_t),
                 .DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(egr_tdest_t))    axis_from_app [2] ();
   axi4s_intf  #(.TUSER_T(tuser_smartnic_meta_t),
                 .DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(egr_tdest_t))    axis_from_app__demarc [2] ();
   axi4s_intf  #(.TUSER_T(tuser_smartnic_meta_t),
                 .DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(egr_tdest_t))    axis_to_drop ();
   axi4s_intf  #(.TUSER_T(tuser_smartnic_meta_t),
                 .DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(egr_tdest_t))    __axis_app_to_core [2] ();
   axi4s_intf  #(.TUSER_T(tuser_smartnic_meta_t),
                 .DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(port_t))         axis_app_to_core [2] ();

   axi4s_intf  #(.MODE(IGNORES_TREADY), .TUSER_T(tuser_smartnic_meta_t),
                 .DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(port_t))         axis_core_to_host [NUM_CMAC] ();
   axi4s_intf  #(.TUSER_T(tuser_smartnic_meta_t),
                 .DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(port_t))         axis_to_host    [NUM_CMAC] ();

   axi4s_intf  #(.MODE(IGNORES_TREADY),
                 .DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(port_t))         axis_core_to_cmac [NUM_CMAC] ();
   axi4s_intf  #(.DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(port_t))         axis_to_pad       [NUM_CMAC] ();
   axi4s_intf  #(.DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(port_t))         axis_to_cmac      [NUM_CMAC] ();


   // ----------------------------------------------------------------
   // fifos to go from independent CMAC clock domains to a single
   // core clock domain
   // ----------------------------------------------------------------

   generate for (genvar i = 0; i < NUM_CMAC; i += 1) begin : g__fifo

      //------------------------ from cmac to core --------------
      axi4s_intf_from_signals #(
        .DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(port_t)
      ) axis_from_cmac_from_signals (
        .aclk     (cmac_clk[i]),
        .aresetn  (cmac_rstn[i]),
        .tvalid   (s_axis_cmac_rx_322mhz_tvalid[i]),
        .tready   (s_axis_cmac_rx_322mhz_tready[i]), // NOTE: tready signal is ignored by open-nic-shell.
        .tdata    (s_axis_cmac_rx_322mhz_tdata[`getvec(512, i)]),
        .tkeep    (s_axis_cmac_rx_322mhz_tkeep[`getvec(64, i)]),
        .tlast    (s_axis_cmac_rx_322mhz_tlast[i]),
        .tid      (smartnic_322mhz_regs.igr_sw_tid[i]),
        .tdest    (s_axis_cmac_rx_322mhz_tdest[`getvec(2, i)]),
        .tuser    (s_axis_cmac_rx_322mhz_tuser_err[i]),

        .axi4s_if (axis_from_cmac[i])
      );

      // axi4s_ila axi4s_ila_0 (.axis_in(axis_from_cmac[i]));

      axi4s_probe #( .MODE(ERRORS) ) axi4s_err_from_cmac (
            .axi4l_if  (axil_to_err_from_cmac[i]),
            .axi4s_if  (axis_from_cmac[i])
         );

      axi4s_pkt_fifo_async #(
        .FIFO_DEPTH     (1024),
        .MAX_PKT_LEN    (MAX_PKT_LEN)
      ) fifo_from_cmac (
        .axi4s_in       (axis_from_cmac[i]),
        .clk_out        (core_clk),
        .axi4s_out      (axis_cmac_to_core[i]),
        .axil_to_probe  (axil_to_probe_from_cmac[i]),
        .axil_to_ovfl   (axil_to_ovfl_from_cmac[i]),
        .axil_if        (axil_to_fifo_from_cmac[i])
      );

      // Terminate unused AXI-L interface
      axi4l_intf_controller_term axi4l_fifo_from_cmac_term (.axi4l_if (axil_to_fifo_from_cmac[i]));



      //------------------------ from core to cmac --------------
      axi4s_pkt_fifo_async #(
        .FIFO_DEPTH     (1024),
        .MAX_PKT_LEN    (MAX_PKT_LEN)
      ) fifo_to_cmac (
        .axi4s_in       (axis_core_to_cmac[i]),
        .clk_out        (cmac_clk[i]),
        .axi4s_out      (axis_to_pad[i]),
        .flow_ctl_thresh (smartnic_322mhz_regs.egr_fc_thresh[i][15:0]),
        .flow_ctl       (egr_flow_ctl[i]),
        .axil_to_probe  (axil_to_probe_to_cmac[i]),
        .axil_to_ovfl   (axil_to_ovfl_to_cmac[i]),
        .axil_if        (axil_to_fifo_to_cmac[i])
      );

      // axi4s pad instantiation.
      axi4s_pad axi4s_pad_0 (
        .axi4s_in    (axis_to_pad[i]),
        .axi4s_out   (axis_to_cmac[i])
      );

      // axi4s_ila axi4s_ila_1 (.axis_in(axis_core_to_cmac[i]));
      // axi4s_ila axi4s_ila_2 (.axis_in(axis_to_cmac[i]));

      // Terminate unused AXI-L interface
      axi4l_intf_controller_term axi4l_fifo_to_cmac_term (.axi4l_if (axil_to_fifo_to_cmac[i]));

      axi4s_intf_to_signals #(
        .DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(port_t)
      ) axis_to_cmac_to_signals (
        .aclk     (),
        .aresetn  (),
        .tvalid   (m_axis_cmac_tx_322mhz_tvalid[i]),
        .tready   (m_axis_cmac_tx_322mhz_tready[i]),
        .tdata    (m_axis_cmac_tx_322mhz_tdata[`getvec(512, i)]),
        .tkeep    (m_axis_cmac_tx_322mhz_tkeep[`getvec(64, i)]),
        .tlast    (m_axis_cmac_tx_322mhz_tlast[i]),
        .tid      (),
        .tdest    (m_axis_cmac_tx_322mhz_tdest[`getvec(2, i)]),
        .tuser    (m_axis_cmac_tx_322mhz_tuser_err[i]),

        .axi4s_if (axis_to_cmac[i])
      );


      //------------------------ from core to host --------------
      axi4s_pkt_fifo_async #(
        .FIFO_DEPTH     (1024),
        .MAX_PKT_LEN    (MAX_PKT_LEN)
      ) fifo_to_host (
        .axi4s_in       (axis_core_to_host[i]),
        .clk_out        (cmac_clk[i]),
        .axi4s_out      (axis_to_host[i]),
        .flow_ctl_thresh (smartnic_322mhz_regs.egr_fc_thresh[2+i][15:0]),
        .flow_ctl       (egr_flow_ctl[2+i]),
        .axil_to_probe  (axil_to_probe_to_host[i]),
        .axil_to_ovfl   (axil_to_ovfl_to_host[i]),
        .axil_if        (axil_to_fifo_to_host[i])
      );

      // axi4s_ila axi4s_ila_to_host (.axis_in(axis_to_host[i]));

      // Terminate unused AXI-L interface
      if (i != 0) axi4l_intf_controller_term axi4l_fifo_to_host_term (.axi4l_if (axil_to_fifo_to_host[i]));

      axi4s_intf_to_signals #(
        .DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(port_t), .TUSER_T(tuser_smartnic_meta_t)
      ) axis_to_host_to_signals (
        .aclk     (),
        .aresetn  (),
        .tvalid   (),  // see assignment below
        .tready   (m_axis_adpt_rx_322mhz_tready[i] && !axis_to_host_tpause[i]),
        .tdata    (m_axis_adpt_rx_322mhz_tdata[`getvec(512, i)]),
        .tkeep    (m_axis_adpt_rx_322mhz_tkeep[`getvec(64, i)]),
        .tlast    (m_axis_adpt_rx_322mhz_tlast[i]),
        .tid      (),
        .tdest    (m_axis_adpt_rx_322mhz_tdest[`getvec(2, i)]),
        .tuser    (m_axis_adpt_rx_322mhz_tuser[i]),

        .axi4s_if (axis_to_host[i])
      );

      assign m_axis_adpt_rx_322mhz_tvalid[i] = axis_to_host[i].tvalid && !axis_to_host_tpause[i];

      assign m_axis_adpt_rx_322mhz_tuser_err[i] = '0;
      assign m_axis_adpt_rx_322mhz_tuser_rss_enable[i] = m_axis_adpt_rx_322mhz_tuser[i].rss_enable;
      assign m_axis_adpt_rx_322mhz_tuser_rss_entropy[`getvec(12, i)] = m_axis_adpt_rx_322mhz_tuser[i].rss_entropy;


      //------------------------ from host to core --------------
      axi4s_intf_from_signals #(
        .DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(port_t)
      ) axis_from_host_from_signals (
        .aclk     (cmac_clk[i]),
        .aresetn  (cmac_rstn[i]),
        .tvalid   (s_axis_adpt_tx_322mhz_tvalid[i]),
        .tready   (s_axis_adpt_tx_322mhz_tready[i]),
        .tdata    (s_axis_adpt_tx_322mhz_tdata[`getvec(512, i)]),
        .tkeep    (s_axis_adpt_tx_322mhz_tkeep[`getvec(64, i)]),
        .tlast    (s_axis_adpt_tx_322mhz_tlast[i]),
        .tid      (smartnic_322mhz_regs.igr_sw_tid[2+i]),
        .tdest    (s_axis_adpt_tx_322mhz_tdest[`getvec(2, i)]),
        .tuser    (s_axis_adpt_tx_322mhz_tuser_err[i]),  // this is a deadend for now. no use in smartnic_322mhz.

        .axi4s_if (axis_from_host[i])
      );


      axi4s_pkt_fifo_async #(
        .FIFO_DEPTH     (128),
        .MAX_PKT_LEN    (MAX_PKT_LEN)
      ) fifo_from_host (
        .axi4s_in       (axis_from_host[i]),
        .clk_out        (core_clk),
        .axi4s_out      (axis_host_to_core[i]),
        .axil_to_probe  (axil_to_probe_from_host[i]),
        .axil_to_ovfl   (axil_to_ovfl_from_host[i]),
        .axil_if        (axil_to_fifo_from_host[i])
      );

      axi4l_intf_controller_term axi4l_ovfl_from_host_term (.axi4l_if (axil_to_ovfl_from_host[i]));
      axi4l_intf_controller_term axi4l_fifo_from_host_term (.axi4l_if (axil_to_fifo_from_host[i]));

   end : g__fifo

   endgenerate



   axis_switch_ingress axis_switch_ingress
   (
    .aclk    ( core_clk ),
    .aresetn ( core_rstn ),

    .m_axis_tdata  ({ axis_core_to_bypass.tdata  , axis_core_to_app[1].tdata  , axis_core_to_app[0].tdata  }),
    .m_axis_tkeep  ({ axis_core_to_bypass.tkeep  , axis_core_to_app[1].tkeep  , axis_core_to_app[0].tkeep  }),
    .m_axis_tlast  ({ axis_core_to_bypass.tlast  , axis_core_to_app[1].tlast  , axis_core_to_app[0].tlast  }),
    .m_axis_tid    ({ axis_core_to_bypass.tid    , axis_core_to_app[1].tid    , axis_core_to_app[0].tid    }),
    .m_axis_tdest  ({ axis_core_to_bypass.tdest  , axis_core_to_app[1].tdest[1:0] , axis_core_to_app[0].tdest[1:0] }),
    .m_axis_tready ({ axis_core_to_bypass_tready , axis_core_to_app[1].tready , axis_core_to_app[0].tready }),
    .m_axis_tvalid ({ axis_core_to_bypass_tvalid , axis_core_to_app[1].tvalid , axis_core_to_app[0].tvalid }),

    .s_axis_tdata  ({ axis_host_to_core[1].tdata  , axis_host_to_core[0].tdata  , axis_cmac_to_core[1].tdata  , axis_cmac_to_core[0].tdata  }),
    .s_axis_tkeep  ({ axis_host_to_core[1].tkeep  , axis_host_to_core[0].tkeep  , axis_cmac_to_core[1].tkeep  , axis_cmac_to_core[0].tkeep  }),
    .s_axis_tlast  ({ axis_host_to_core[1].tlast  , axis_host_to_core[0].tlast  , axis_cmac_to_core[1].tlast  , axis_cmac_to_core[0].tlast  }),
    .s_axis_tid    ({ axis_host_to_core[1].tid    , axis_host_to_core[0].tid    , axis_cmac_to_core[1].tid    , axis_cmac_to_core[0].tid    }),
    .s_axis_tdest  ({ smartnic_322mhz_regs.igr_sw_tdest[3],
                      smartnic_322mhz_regs.igr_sw_tdest[2],
                      smartnic_322mhz_regs.igr_sw_tdest[1],
                      smartnic_322mhz_regs.igr_sw_tdest[0] }),
    .s_axis_tready ({ axis_host_to_core[1].tready , axis_host_to_core[0].tready , axis_cmac_to_core[1].tready , axis_cmac_to_core[0].tready }),
    .s_axis_tvalid ({ axis_host_to_core[1].tvalid , axis_host_to_core[0].tvalid , axis_cmac_to_core[1].tvalid , axis_cmac_to_core[0].tvalid }),

    .s_decode_err  ()
   );

   assign axis_core_to_app[0].aclk = core_clk;
   assign axis_core_to_app[1].aclk = core_clk;
   assign axis_core_to_bypass.aclk = core_clk;

   assign axis_core_to_app[0].aresetn = core_rstn;
   assign axis_core_to_app[1].aresetn = core_rstn;
   assign axis_core_to_bypass.aresetn = core_rstn;

   assign axis_core_to_app[0].tuser = '0;
   assign axis_core_to_app[1].tuser = '0;
   assign axis_core_to_bypass.tuser = '0;

   assign axis_core_to_app[0].tdest[2] = '0;
   assign axis_core_to_app[1].tdest[2] = '0;

   // axi4s_split_join instantiation (separates and recombines packet headers).
   axi4s_split_join #(
     .BIGENDIAN(0)
   ) axi4s_split_join_0 (
     .axi4s_in      (axis_core_to_app[0]),
     .axi4s_out     (axis_to_drop),
     .axi4s_hdr_out (axis_to_app__demarc[0]),
     .axi4s_hdr_in  (axis_from_app__demarc[0]),
     .axil_if       (axil_to_split_join),
     .hdr_length    (smartnic_322mhz_regs.hdr_length[15:0])
   );

   // packet drop logic, which deletes:
   // zero-length packets (when vitisnetp4 core emits dropped headers), and
   // packets that have tdest == tid (to prevent switching loops).
   logic  zero_length, loop_detect, drop_pkt;

   assign zero_length = axis_to_drop.tvalid && axis_to_drop.sop && axis_to_drop.tlast &&
                        axis_to_drop.tkeep == '0;

   assign loop_detect = smartnic_322mhz_regs.switch_config.drop_pkt_loop && axis_to_drop.tvalid && axis_to_drop.sop &&
                        axis_to_drop.tdest == axis_to_drop.tid;

   assign drop_pkt = zero_length || loop_detect;

   // axi4s drop pkt instantiation.
   axi4s_drop axi4s_drop_0 (
      .axi4s_in    (axis_to_drop),
      .axi4s_out   (__axis_app_to_core[0]),
      .axil_if     (axil_to_drops_from_app0),
      .drop_pkt    (drop_pkt)
   );

   // axi4s_ila #(.PIPE_STAGES(2)) axi4s_ila_core_to_app  (.axis_in(axis_core_to_app[0]));
   // axi4s_ila #(.PIPE_STAGES(2)) axi4s_ila_app_to_core  (.axis_in(__axis_app_to_core[0]));
   // axi4s_ila #(.PIPE_STAGES(2)) axi4s_ila_hdr_to_app   (.axis_in(axis_to_app__demarc[0]));
   // axi4s_ila #(.PIPE_STAGES(2)) axi4s_ila_hdr_from_app (.axis_in(axis_from_app__demarc[0]));

   // tpause logic for ingress switch (for test purposes).
   assign axis_core_to_bypass.tvalid = axis_core_to_bypass_tvalid && !smartnic_322mhz_regs.switch_config.igr_sw_tpause;
   assign axis_core_to_bypass_tready = axis_core_to_bypass.tready && !smartnic_322mhz_regs.switch_config.igr_sw_tpause;

   // ingress switch drop pkt logic.  deletes packets that have tdest == 3 (igr_sw DROP code point).
   logic  igr_sw_drop_pkt;

   assign igr_sw_drop_pkt = axis_core_to_bypass.tvalid && axis_core_to_bypass.sop &&
                            axis_core_to_bypass.tdest.raw == 2'h3;

   // igr_sw_drop axi4s_drop instantiation.
   axi4s_drop igr_sw_drop_0 (
      .axi4s_in    (axis_core_to_bypass),
      .axi4s_out   (axis_igr_sw_drop),
      .axil_if     (axil_to_drops_from_igr_sw),
      .drop_pkt    (igr_sw_drop_pkt)
   );

   axi4s_intf_pipe to_bypass_pipe_0 (.axi4s_if_from_tx(axis_igr_sw_drop), .axi4s_if_to_rx(axis_to_bypass_fifo));

   axi4s_pkt_fifo_sync #(
     .FIFO_DEPTH     (256),
     .MAX_PKT_LEN    (MAX_PKT_LEN)
   ) bypass_fifo (
     .srst           (1'b0),
     .axi4s_in       (axis_to_bypass_fifo),
     .axi4s_out      (axis_from_bypass_fifo),
     .axil_to_probe  (axil_to_probe_to_bypass),
     .axil_to_ovfl   (axil_to_ovfl_to_bypass),
     .axil_if        (axil_to_fifo_to_bypass)
   );

   axi4l_intf_controller_term axi4l_to_ovfl_to_bypass_term  (.axi4l_if (axil_to_ovfl_to_bypass));
   axi4l_intf_controller_term axi4l_to_fifo_to_bypass_term  (.axi4l_if (axil_to_fifo_to_bypass));

   axi4s_intf_pipe from_bypass_pipe_0 (.axi4s_if_from_tx(axis_from_bypass_fifo), .axi4s_if_to_rx(axis_from_bypass_fifo_pipe));

   // Bypass path assignments.
   assign axis_from_bypass_fifo_pipe.tready = axis_to_bypass_drop.tready;

   assign axis_to_bypass_drop.aclk    = axis_from_bypass_fifo_pipe.aclk;
   assign axis_to_bypass_drop.aresetn = axis_from_bypass_fifo_pipe.aresetn;
   assign axis_to_bypass_drop.tvalid  = axis_from_bypass_fifo_pipe.tvalid;
   assign axis_to_bypass_drop.tdata   = axis_from_bypass_fifo_pipe.tdata;
   assign axis_to_bypass_drop.tkeep   = axis_from_bypass_fifo_pipe.tkeep;
   assign axis_to_bypass_drop.tlast   = axis_from_bypass_fifo_pipe.tlast;
   assign axis_to_bypass_drop.tid     = axis_from_bypass_fifo_pipe.tid;

   // muxing logic for bypass tid-to-tdest mapping.
   always_comb begin
      case (axis_from_bypass_fifo_pipe.tid)
         CMAC_PORT0 : axis_to_bypass_drop.tdest = smartnic_322mhz_regs.bypass_tdest[0];
         CMAC_PORT1 : axis_to_bypass_drop.tdest = smartnic_322mhz_regs.bypass_tdest[1];
         HOST_PORT0 : axis_to_bypass_drop.tdest = smartnic_322mhz_regs.bypass_tdest[2];
         HOST_PORT1 : axis_to_bypass_drop.tdest = smartnic_322mhz_regs.bypass_tdest[3];
      endcase
   end

   // bypass packet drop logic.  deletes packets that have tdest == tid (to prevent switching loops).
   logic  bypass_drop_pkt;

   assign bypass_drop_pkt = smartnic_322mhz_regs.switch_config.drop_pkt_loop &&
                            axis_to_bypass_drop.tvalid && axis_to_bypass_drop.sop &&
                            axis_to_bypass_drop.tdest == axis_to_bypass_drop.tid;

   // bypass drop pkt instantiation.
   axi4s_drop bypass_drop_0 (
      .axi4s_in    (axis_to_bypass_drop),
      .axi4s_out   (axis_bypass_to_core),
      .axil_if     (axil_to_drops_from_bypass),
      .drop_pkt    (bypass_drop_pkt)
   );



   axi4s_intf_pipe axis_core_to_app_pipe (.axi4s_if_from_tx(axis_core_to_app[1]),      .axi4s_if_to_rx(axis_to_app__demarc[1]));
   axi4s_intf_pipe axis_app_to_core_pipe (.axi4s_if_from_tx(axis_from_app__demarc[1]), .axi4s_if_to_rx(__axis_app_to_core[1]));


   // axis_app_to_core[0] assignments.
   assign axis_app_to_core[0].aclk    = __axis_app_to_core[0].aclk;
   assign axis_app_to_core[0].aresetn = __axis_app_to_core[0].aresetn;
   assign axis_app_to_core[0].tvalid  = __axis_app_to_core[0].tvalid;
   assign axis_app_to_core[0].tdata   = __axis_app_to_core[0].tdata;
   assign axis_app_to_core[0].tkeep   = __axis_app_to_core[0].tkeep;
   assign axis_app_to_core[0].tlast   = __axis_app_to_core[0].tlast;
   assign axis_app_to_core[0].tid     = __axis_app_to_core[0].tid;
   assign axis_app_to_core[0].tuser   = __axis_app_to_core[0].tuser;

   assign __axis_app_to_core[0].tready = axis_app_to_core[0].tready;

   port_t tdest_remap_mux_select[2];
   assign tdest_remap_mux_select[0] = (__axis_app_to_core[0].tdest == LOOPBACK) ? __axis_app_to_core[0].tid : __axis_app_to_core[0].tdest.raw[1:0];

   // muxing logic for app_to_core[0] tdest-to-tdest re-mapping.
   always_comb begin
      case (tdest_remap_mux_select[0])
         CMAC_PORT0 : axis_app_to_core[0].tdest = smartnic_322mhz_regs.app_0_tdest_remap[0];
         CMAC_PORT1 : axis_app_to_core[0].tdest = smartnic_322mhz_regs.app_0_tdest_remap[1];
         HOST_PORT0 : axis_app_to_core[0].tdest = smartnic_322mhz_regs.app_0_tdest_remap[2];
         HOST_PORT1 : axis_app_to_core[0].tdest = smartnic_322mhz_regs.app_0_tdest_remap[3];
      endcase
   end


   // axis_app_to_core[1] assignments.
   assign axis_app_to_core[1].aclk    = __axis_app_to_core[1].aclk;
   assign axis_app_to_core[1].aresetn = __axis_app_to_core[1].aresetn;
   assign axis_app_to_core[1].tvalid  = __axis_app_to_core[1].tvalid;
   assign axis_app_to_core[1].tdata   = __axis_app_to_core[1].tdata;
   assign axis_app_to_core[1].tkeep   = __axis_app_to_core[1].tkeep;
   assign axis_app_to_core[1].tlast   = __axis_app_to_core[1].tlast;
   assign axis_app_to_core[1].tid     = __axis_app_to_core[1].tid;
   assign axis_app_to_core[1].tuser   = __axis_app_to_core[1].tuser;

   assign __axis_app_to_core[1].tready = axis_app_to_core[1].tready;

   assign tdest_remap_mux_select[1] = (__axis_app_to_core[1].tdest == LOOPBACK) ? __axis_app_to_core[1].tid : __axis_app_to_core[1].tdest.raw[1:0];

   // muxing logic for app_to_core[1] tdest-to-tdest re-mapping.
   always_comb begin
      case (tdest_remap_mux_select[1])
         CMAC_PORT0 : axis_app_to_core[1].tdest = smartnic_322mhz_regs.app_1_tdest_remap[0];
         CMAC_PORT1 : axis_app_to_core[1].tdest = smartnic_322mhz_regs.app_1_tdest_remap[1];
         HOST_PORT0 : axis_app_to_core[1].tdest = smartnic_322mhz_regs.app_1_tdest_remap[2];
         HOST_PORT1 : axis_app_to_core[1].tdest = smartnic_322mhz_regs.app_1_tdest_remap[3];
      endcase
   end


   logic [12:0] axis_app_to_core_tuser [NUM_CMAC];
   assign axis_app_to_core_tuser[0] = {axis_app_to_core[0].tuser.rss_enable, axis_app_to_core[0].tuser.rss_entropy};
   assign axis_app_to_core_tuser[1] = {axis_app_to_core[1].tuser.rss_enable, axis_app_to_core[1].tuser.rss_entropy};

   logic [12:0] axis_core_to_host_tuser [NUM_CMAC];
   assign axis_core_to_host[0].tuser.pid         = '0;
   assign axis_core_to_host[0].tuser.rss_enable  = axis_core_to_host_tuser[0][12];
   assign axis_core_to_host[0].tuser.rss_entropy = axis_core_to_host_tuser[0][11:0];
   assign axis_core_to_host[0].tuser.hdr_tlast   = '0;
   assign axis_core_to_host[1].tuser.pid         = '0;
   assign axis_core_to_host[1].tuser.rss_enable  = axis_core_to_host_tuser[1][12];
   assign axis_core_to_host[1].tuser.rss_entropy = axis_core_to_host_tuser[1][11:0];
   assign axis_core_to_host[1].tuser.hdr_tlast   = '0;

   logic [12:0] axis_core_to_cmac_tuser [NUM_CMAC];
   assign axis_core_to_cmac[0].tuser = '0;
   assign axis_core_to_cmac[1].tuser = '0;

   axis_switch_egress axis_switch_egress
   (
    .aclk    ( core_clk ),
    .aresetn ( core_rstn ),

    .m_axis_tdata  ({ axis_core_to_host[1].tdata  , axis_core_to_host[0].tdata  , axis_core_to_cmac[1].tdata  , axis_core_to_cmac[0].tdata  }),
    .m_axis_tkeep  ({ axis_core_to_host[1].tkeep  , axis_core_to_host[0].tkeep  , axis_core_to_cmac[1].tkeep  , axis_core_to_cmac[0].tkeep  }),
    .m_axis_tlast  ({ axis_core_to_host[1].tlast  , axis_core_to_host[0].tlast  , axis_core_to_cmac[1].tlast  , axis_core_to_cmac[0].tlast  }),
    .m_axis_tid    ({ axis_core_to_host[1].tid    , axis_core_to_host[0].tid    , axis_core_to_cmac[1].tid    , axis_core_to_cmac[0].tid    }),
    .m_axis_tdest  ({ axis_core_to_host[1].tdest  , axis_core_to_host[0].tdest  , axis_core_to_cmac[1].tdest  , axis_core_to_cmac[0].tdest  }),
    .m_axis_tuser  ({ axis_core_to_host_tuser[1]  , axis_core_to_host_tuser[0]  , axis_core_to_cmac_tuser[1]  , axis_core_to_cmac_tuser[0]  }),
    .m_axis_tready ({ axis_core_to_host[1].tready , axis_core_to_host[0].tready , axis_core_to_cmac[1].tready , axis_core_to_cmac[0].tready }),
    .m_axis_tvalid ({ axis_core_to_host[1].tvalid , axis_core_to_host[0].tvalid , axis_core_to_cmac[1].tvalid , axis_core_to_cmac[0].tvalid }),

    .s_axis_tdata  ({ axis_bypass_to_core.tdata  , axis_app_to_core[1].tdata  , axis_app_to_core[0].tdata  }),
    .s_axis_tkeep  ({ axis_bypass_to_core.tkeep  , axis_app_to_core[1].tkeep  , axis_app_to_core[0].tkeep  }),
    .s_axis_tlast  ({ axis_bypass_to_core.tlast  , axis_app_to_core[1].tlast  , axis_app_to_core[0].tlast  }),
    .s_axis_tid    ({ axis_bypass_to_core.tid    , axis_app_to_core[1].tid    , axis_app_to_core[0].tid    }),
    .s_axis_tdest  ({ axis_bypass_to_core.tdest  , axis_app_to_core[1].tdest  , axis_app_to_core[0].tdest  }),
    .s_axis_tuser  ({                  13'h0000  , axis_app_to_core_tuser[1]  , axis_app_to_core_tuser[0]  }),
    .s_axis_tready ({ axis_bypass_to_core.tready , axis_app_to_core[1].tready , axis_app_to_core[0].tready }),
    .s_axis_tvalid ({ axis_bypass_to_core.tvalid , axis_app_to_core[1].tvalid , axis_app_to_core[0].tvalid }),

    .s_decode_err ()
   );

   assign axis_core_to_cmac[0].aclk = core_clk;
   assign axis_core_to_cmac[1].aclk = core_clk;
   assign axis_core_to_host[0].aclk = core_clk;
   assign axis_core_to_host[1].aclk = core_clk;

   assign axis_core_to_cmac[0].aresetn = core_rstn;
   assign axis_core_to_cmac[1].aresetn = core_rstn;
   assign axis_core_to_host[0].aresetn = core_rstn;
   assign axis_core_to_host[1].aresetn = core_rstn;


   // ----------------------------------------------------------------
   // AXI register slices
   // ----------------------------------------------------------------
   // - demarcate physical boundary between SmartNIC platform and application
   //   and support efficient pipelining between SLRs

   // AXI-L interface
   axi4l_reg_slice #(
       .CONFIG (xilinx_axi_pkg::XILINX_AXI_REG_SLICE_SLR_CROSSING)
   ) i_axi4l_reg_slice__core_to_app (
       .axi4l_if_from_controller ( axil_to_app_decoder__demarc ),
       .axi4l_if_to_peripheral   ( axil_to_app_decoder )
   );

   // AXI-S interfaces
   axi4s_reg_slice #(
       .DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(port_t), .TUSER_T(tuser_smartnic_meta_t),
       .CONFIG(xilinx_axis_pkg::XILINX_AXIS_REG_SLICE_SLR_CROSSING)
   ) i_axi4s_reg_slice__core_to_app_1 (
       .axi4s_from_tx (axis_to_app__demarc[1]),
       .axi4s_to_rx   (axis_to_app[1])
   );

   axi4s_reg_slice #(
       .DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(port_t), .TUSER_T(tuser_smartnic_meta_t),
       .CONFIG(xilinx_axis_pkg::XILINX_AXIS_REG_SLICE_SLR_CROSSING)
   ) i_axi4s_reg_slice__core_to_app_0 (
       .axi4s_from_tx (axis_to_app__demarc[0]),
       .axi4s_to_rx   (axis_to_app[0])
   );

   axi4s_reg_slice #(
       .DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(egr_tdest_t), .TUSER_T(tuser_smartnic_meta_t),
       .CONFIG(xilinx_axis_pkg::XILINX_AXIS_REG_SLICE_SLR_CROSSING)
   ) i_axi4s_reg_slice__app_to_core_1 (
       .axi4s_from_tx (axis_from_app[1]),
       .axi4s_to_rx   (axis_from_app__demarc[1])
   );

   axi4s_reg_slice #(
       .DATA_BYTE_WID(64), .TID_T(port_t), .TDEST_T(egr_tdest_t), .TUSER_T(tuser_smartnic_meta_t),
       .CONFIG(xilinx_axis_pkg::XILINX_AXIS_REG_SLICE_SLR_CROSSING)
   ) i_axi4s_reg_slice__app_to_core_0 (
       .axi4s_from_tx (axis_from_app[0]),
       .axi4s_to_rx   (axis_from_app__demarc[0])
   );

   // ----------------------------------------------------------------
   // Application Core
   // ----------------------------------------------------------------

   always @(posedge core_clk) begin
      if (!core_rstn) begin
         for (int i=0; i<3; i++) egr_flow_ctl_pipe[i] <= '0;
      end else begin
         egr_flow_ctl_pipe[2] <= egr_flow_ctl;
         for (int i=1; i<3; i++) egr_flow_ctl_pipe[i-1] <= egr_flow_ctl_pipe[i];
      end
   end

   // Provide dedicated AXI-L interfaces for app and sdnet control
   smartnic_322mhz_app_sdnet_decoder smartnic_322mhz_app_sdnet_decoder (
       .axil_if       (axil_to_app_decoder),
       .sdnet_axil_if (axil_to_sdnet),
       .app_axil_if   (axil_to_app)
   );

   smartnic_322mhz_app smartnic_322mhz_app
   (
    .core_clk     (core_clk),
    .core_rstn    (core_rstn),
    .axil_aclk    (axil_aclk),
    .timestamp    (timestamp),
    // AXI-L control interface
    .axil_aresetn (axil_to_app.aresetn),
    .axil_awvalid (axil_to_app.awvalid),
    .axil_awready (axil_to_app.awready),
    .axil_awaddr  (axil_to_app.awaddr),
    .axil_awprot  (axil_to_app.awprot),
    .axil_wvalid  (axil_to_app.wvalid),
    .axil_wready  (axil_to_app.wready),
    .axil_wdata   (axil_to_app.wdata),
    .axil_wstrb   (axil_to_app.wstrb),
    .axil_bvalid  (axil_to_app.bvalid),
    .axil_bready  (axil_to_app.bready),
    .axil_bresp   (axil_to_app.bresp),
    .axil_arvalid (axil_to_app.arvalid),
    .axil_arready (axil_to_app.arready),
    .axil_araddr  (axil_to_app.araddr),
    .axil_arprot  (axil_to_app.arprot),
    .axil_rvalid  (axil_to_app.rvalid),
    .axil_rready  (axil_to_app.rready),
    .axil_rdata   (axil_to_app.rdata),
    .axil_rresp   (axil_to_app.rresp),
    // (SDNet) AXI-L control interface
    .axil_sdnet_aresetn (axil_to_sdnet.aresetn),
    .axil_sdnet_awvalid (axil_to_sdnet.awvalid),
    .axil_sdnet_awready (axil_to_sdnet.awready),
    .axil_sdnet_awaddr  (axil_to_sdnet.awaddr),
    .axil_sdnet_awprot  (axil_to_sdnet.awprot),
    .axil_sdnet_wvalid  (axil_to_sdnet.wvalid),
    .axil_sdnet_wready  (axil_to_sdnet.wready),
    .axil_sdnet_wdata   (axil_to_sdnet.wdata),
    .axil_sdnet_wstrb   (axil_to_sdnet.wstrb),
    .axil_sdnet_bvalid  (axil_to_sdnet.bvalid),
    .axil_sdnet_bready  (axil_to_sdnet.bready),
    .axil_sdnet_bresp   (axil_to_sdnet.bresp),
    .axil_sdnet_arvalid (axil_to_sdnet.arvalid),
    .axil_sdnet_arready (axil_to_sdnet.arready),
    .axil_sdnet_araddr  (axil_to_sdnet.araddr),
    .axil_sdnet_arprot  (axil_to_sdnet.arprot),
    .axil_sdnet_rvalid  (axil_to_sdnet.rvalid),
    .axil_sdnet_rready  (axil_to_sdnet.rready),
    .axil_sdnet_rdata   (axil_to_sdnet.rdata),
    .axil_sdnet_rresp   (axil_to_sdnet.rresp),
    // AXI-S data interface (from switch output 0, to app)
    .axis_from_switch_0_tvalid ( axis_to_app[0].tvalid ),
    .axis_from_switch_0_tready ( axis_to_app[0].tready ),
    .axis_from_switch_0_tdata  ( axis_to_app[0].tdata ),
    .axis_from_switch_0_tkeep  ( axis_to_app[0].tkeep ),
    .axis_from_switch_0_tlast  ( axis_to_app[0].tlast ),
    .axis_from_switch_0_tid    ( axis_to_app[0].tid ),
    .axis_from_switch_0_tdest  ( axis_to_app[0].tdest ),
    .axis_from_switch_0_tuser_pid ( axis_to_app_tuser[0].pid ),
    // AXI-S data interface (from app, to switch input 0)
    .axis_to_switch_0_tvalid ( axis_from_app[0].tvalid ),
    .axis_to_switch_0_tready ( axis_from_app[0].tready ),
    .axis_to_switch_0_tdata  ( axis_from_app[0].tdata ),
    .axis_to_switch_0_tkeep  ( axis_from_app[0].tkeep ),
    .axis_to_switch_0_tlast  ( axis_from_app[0].tlast ),
    .axis_to_switch_0_tid    ( axis_from_app[0].tid ),
    .axis_to_switch_0_tdest  ( axis_from_app[0].tdest ),
    .axis_to_switch_0_tuser_pid ( axis_from_app_tuser[0].pid ),
    .axis_to_switch_0_tuser_rss_enable  ( axis_from_app_tuser[0].rss_enable ),
    .axis_to_switch_0_tuser_rss_entropy ( axis_from_app_tuser[0].rss_entropy ),
    // AXI-S data interface (from switch output 1, to app)
    .axis_from_switch_1_tvalid ( axis_to_app[1].tvalid ),
    .axis_from_switch_1_tready ( axis_to_app[1].tready ),
    .axis_from_switch_1_tdata  ( axis_to_app[1].tdata ),
    .axis_from_switch_1_tkeep  ( axis_to_app[1].tkeep ),
    .axis_from_switch_1_tlast  ( axis_to_app[1].tlast ),
    .axis_from_switch_1_tid    ( axis_to_app[1].tid ),
    .axis_from_switch_1_tdest  ( axis_to_app[1].tdest ),
    .axis_from_switch_1_tuser_pid ( axis_to_app_tuser[1].pid ),
    // AXI-S data interface (from app, to switch input 1)
    .axis_to_switch_1_tvalid ( axis_from_app[1].tvalid ),
    .axis_to_switch_1_tready ( axis_from_app[1].tready ),
    .axis_to_switch_1_tdata  ( axis_from_app[1].tdata ),
    .axis_to_switch_1_tkeep  ( axis_from_app[1].tkeep ),
    .axis_to_switch_1_tlast  ( axis_from_app[1].tlast ),
    .axis_to_switch_1_tid    ( axis_from_app[1].tid ),
    .axis_to_switch_1_tdest  ( axis_from_app[1].tdest ),
    .axis_to_switch_1_tuser_pid ( axis_from_app_tuser[1].pid ),
    .axis_to_switch_1_tuser_rss_enable  ( axis_from_app_tuser[1].rss_enable ),
    .axis_to_switch_1_tuser_rss_entropy ( axis_from_app_tuser[1].rss_entropy ),
    // egress flow control interface
    .egr_flow_ctl            ( egr_flow_ctl_pipe[0] ),
    // AXI3 interfaces to HBM
    // (synchronous to core clock domain)
    .axi_to_hbm_awid     ( axi_app_to_hbm_awid    ),
    .axi_to_hbm_awaddr   ( axi_app_to_hbm_awaddr  ),
    .axi_to_hbm_awlen    ( axi_app_to_hbm_awlen   ),
    .axi_to_hbm_awsize   ( axi_app_to_hbm_awsize  ),
    .axi_to_hbm_awburst  ( axi_app_to_hbm_awburst ),
    .axi_to_hbm_awlock   ( axi_app_to_hbm_awlock  ),
    .axi_to_hbm_awcache  ( axi_app_to_hbm_awcache ),
    .axi_to_hbm_awprot   ( axi_app_to_hbm_awprot  ),
    .axi_to_hbm_awqos    ( axi_app_to_hbm_awqos   ),
    .axi_to_hbm_awregion ( axi_app_to_hbm_awregion),
    .axi_to_hbm_awvalid  ( axi_app_to_hbm_awvalid ),
    .axi_to_hbm_awready  ( axi_app_to_hbm_awready ),
    .axi_to_hbm_wid      ( axi_app_to_hbm_wid     ),
    .axi_to_hbm_wdata    ( axi_app_to_hbm_wdata   ),
    .axi_to_hbm_wstrb    ( axi_app_to_hbm_wstrb   ),
    .axi_to_hbm_wlast    ( axi_app_to_hbm_wlast   ),
    .axi_to_hbm_wvalid   ( axi_app_to_hbm_wvalid  ),
    .axi_to_hbm_wready   ( axi_app_to_hbm_wready  ),
    .axi_to_hbm_bid      ( axi_app_to_hbm_bid     ),
    .axi_to_hbm_bresp    ( axi_app_to_hbm_bresp   ),
    .axi_to_hbm_bvalid   ( axi_app_to_hbm_bvalid  ),
    .axi_to_hbm_bready   ( axi_app_to_hbm_bready  ),
    .axi_to_hbm_arid     ( axi_app_to_hbm_arid    ),
    .axi_to_hbm_araddr   ( axi_app_to_hbm_araddr  ),
    .axi_to_hbm_arlen    ( axi_app_to_hbm_arlen   ),
    .axi_to_hbm_arsize   ( axi_app_to_hbm_arsize  ),
    .axi_to_hbm_arburst  ( axi_app_to_hbm_arburst ),
    .axi_to_hbm_arlock   ( axi_app_to_hbm_arlock  ),
    .axi_to_hbm_arcache  ( axi_app_to_hbm_arcache ),
    .axi_to_hbm_arprot   ( axi_app_to_hbm_arprot  ),
    .axi_to_hbm_arqos    ( axi_app_to_hbm_arqos   ),
    .axi_to_hbm_arregion ( axi_app_to_hbm_arregion),
    .axi_to_hbm_arvalid  ( axi_app_to_hbm_arvalid ),
    .axi_to_hbm_arready  ( axi_app_to_hbm_arready ),
    .axi_to_hbm_rid      ( axi_app_to_hbm_rid     ),
    .axi_to_hbm_rdata    ( axi_app_to_hbm_rdata   ),
    .axi_to_hbm_rresp    ( axi_app_to_hbm_rresp   ),
    .axi_to_hbm_rlast    ( axi_app_to_hbm_rlast   ),
    .axi_to_hbm_rvalid   ( axi_app_to_hbm_rvalid  ),
    .axi_to_hbm_rready   ( axi_app_to_hbm_rready  )
   );

   assign axis_from_app[0].aclk = core_clk;
   assign axis_from_app[1].aclk = core_clk;

   assign axis_from_app[0].aresetn = core_rstn;
   assign axis_from_app[1].aresetn = core_rstn;

   assign axis_from_app_tuser[0].hdr_tlast = '0;
   assign axis_from_app_tuser[1].hdr_tlast = '0;

   axi4s_probe axis_probe_app_to_core_0 (
      .axi4l_if  (axil_to_app_to_core[0]),
      .axi4s_if  (axis_app_to_core[0])
   );

   axi4s_probe axis_probe_core_to_app_0 (
      .axi4l_if  (axil_to_core_to_app[0]),
      .axi4s_if  (axis_core_to_app[0])
   );

   axi4s_probe axis_probe_app_to_core_1 (
      .axi4l_if  (axil_to_app_to_core[1]),
      .axi4s_if  (axis_app_to_core[1])
   );

   axi4s_probe axis_probe_core_to_app_1 (
      .axi4l_if  (axil_to_core_to_app[1]),
      .axi4s_if  (axis_core_to_app[1])
   );

endmodule: smartnic_322mhz
