`timescale 1ns/1ps

module p2p #(
) (
   input logic        core_clk,
   input logic        core_rstn,
   input logic [63:0] timestamp,

   axi4l_intf.peripheral axil_if,
   axi4l_intf.peripheral axil_to_sdnet,

   axi4s_intf.tx axis_to_switch_0,
   axi4s_intf.rx axis_from_switch_0,
   axi4s_intf.tx axis_to_switch_1,
   axi4s_intf.rx axis_from_switch_1
);

   // ----------------------------------------------------------------
   //  Register map block and decoder instantiations
   // ----------------------------------------------------------------

   axi4l_intf  axil_to_p2p_regs ();
   axi4l_intf  axil_to_sdnet_regs ();
   axi4l_intf  axil_to_sdnet_regs__core_clk ();
   
   p2p_reg_intf  p2p_regs();
   p2p_reg_intf  sdnet_regs();

   // p2p register decoder
   p2p_decoder p2p_decoder (
      .axil_if       (axil_if),
      .p2p_axil_if   (axil_to_p2p_regs)
   );

   // sdnet register decoder
   p2p_decoder sdnet_decoder (
      .axil_if       (axil_to_sdnet),
      .p2p_axil_if   (axil_to_sdnet_regs)
   );
   
   // p2p register block
   p2p_reg_blk p2p_reg_blk
   (
    .axil_if    (axil_to_p2p_regs),
    .reg_blk_if (p2p_regs)
   );

   // sdnet register block
   axi4l_intf_cdc axil_to_sdnet_cdc (
      .axi4l_if_from_controller  ( axil_to_sdnet_regs ),
      .clk_to_peripheral         ( core_clk ),
      .axi4l_if_to_peripheral    ( axil_to_sdnet_regs__core_clk )
   );

   p2p_reg_blk sdnet_reg_blk 
   (
    .axil_if    (axil_to_sdnet_regs__core_clk),
    .reg_blk_if (sdnet_regs)
   );

   // ----------------------------------------------------------------
   //  Timestamp to regmap connections (for test purposes)
   // ----------------------------------------------------------------

   logic [63:0] timestamp_latch;
   logic        timestamp_rd_latch_wr_evt_d1;

   always @(posedge core_clk) if (sdnet_regs.timestamp_rd_latch_wr_evt) timestamp_latch <= timestamp;

   assign sdnet_regs.status_upper_nxt = timestamp_latch[63:32];
   assign sdnet_regs.status_lower_nxt = timestamp_latch[31:0];

   always @(posedge core_clk) timestamp_rd_latch_wr_evt_d1  <= sdnet_regs.timestamp_rd_latch_wr_evt;

   assign sdnet_regs.status_upper_nxt_v = timestamp_rd_latch_wr_evt_d1;
   assign sdnet_regs.status_lower_nxt_v = timestamp_rd_latch_wr_evt_d1;

   // ----------------------------------------------------------------
   //  Datpath pass-through connections (hard-wired bypass)
   // ----------------------------------------------------------------
   
   assign axis_to_switch_0.tvalid = axis_from_switch_0.tvalid && !p2p_regs.tpause;
   assign axis_to_switch_0.tdata  = axis_from_switch_0.tdata;
   assign axis_to_switch_0.tkeep  = axis_from_switch_0.tkeep;
   assign axis_to_switch_0.tlast  = axis_from_switch_0.tlast;
   assign axis_to_switch_0.tid    = axis_from_switch_0.tid;
   assign axis_to_switch_0.tdest  = {'0, axis_from_switch_0.tdest};
   assign axis_to_switch_0.tuser  = axis_from_switch_0.tuser;

   assign axis_from_switch_0.tready = axis_to_switch_0.tready && !p2p_regs.tpause;


   assign axis_to_switch_1.tvalid = axis_from_switch_1.tvalid;
   assign axis_to_switch_1.tdata  = axis_from_switch_1.tdata;
   assign axis_to_switch_1.tkeep  = axis_from_switch_1.tkeep;
   assign axis_to_switch_1.tlast  = axis_from_switch_1.tlast;
   assign axis_to_switch_1.tid    = axis_from_switch_1.tid;
   assign axis_to_switch_1.tdest  = {'0, axis_from_switch_1.tdest};
   assign axis_to_switch_1.tuser  = axis_from_switch_1.tuser;

   assign axis_from_switch_1.tready = axis_to_switch_1.tready;


endmodule: p2p
