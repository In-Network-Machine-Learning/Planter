module smartnic_322mhz_timestamp
//    import smartnic_322mhz_pkg::*;
#() (
    input  logic        clk,
    input  logic        rstn,
    output logic [63:0] timestamp,

    smartnic_322mhz_reg_intf.peripheral  smartnic_322mhz_regs    
);

    // Signals
    logic [32:0] timestamp_lsbs,  freerun_lsbs;
    logic [91:0] timestamp_cntr,  freerun_cntr;
    logic [63:0] timestamp_latch, freerun_latch;
    logic        timestamp_rd_latch_wr_evt_d1;

    // Timestamp counter and access logic.
    always @(posedge clk) begin
       if (!rstn) begin
          timestamp_lsbs <= '0; timestamp_cntr <= '0;
          freerun_lsbs   <= '0; freerun_cntr   <= '0;

       end else if (smartnic_322mhz_regs.timestamp_wr_lower_wr_evt) begin
          timestamp_lsbs <= '0;
          timestamp_cntr <= { smartnic_322mhz_regs.timestamp_wr_upper, 
                              smartnic_322mhz_regs.timestamp_wr_lower, 
                              28'd0 };
          freerun_lsbs   <= '0;
          freerun_cntr   <= { smartnic_322mhz_regs.timestamp_wr_upper,
                              smartnic_322mhz_regs.timestamp_wr_lower,
                              28'd0 };
       end else begin
          timestamp_lsbs <= {1'b0, timestamp_lsbs[31:0]} + {1'd0, smartnic_322mhz_regs.timestamp_incr};
          timestamp_cntr[31:0]  <= timestamp_lsbs[31:0];
          timestamp_cntr[91:32] <= timestamp_cntr[91:32] + {59'd0, timestamp_lsbs[32]};

          freerun_lsbs <= {1'b0, freerun_lsbs[31:0]} + {1'd0, smartnic_322mhz_reg_pkg::INIT_TIMESTAMP_INCR};
          freerun_cntr[31:0]  <= freerun_lsbs[31:0];
          freerun_cntr[91:32] <= freerun_cntr[91:32] + { 59'd0, freerun_lsbs[32] };
       end
    end

    assign timestamp = timestamp_cntr[91:28];

    always @(posedge clk)
       if (smartnic_322mhz_regs.timestamp_rd_latch_wr_evt) begin
          timestamp_latch <= timestamp;
          freerun_latch   <= freerun_cntr[91:28];
       end
   
    assign smartnic_322mhz_regs.timestamp_rd_upper_nxt   = timestamp_latch[63:32];
    assign smartnic_322mhz_regs.timestamp_rd_lower_nxt   = timestamp_latch[31:0];
 
    assign smartnic_322mhz_regs.freerun_rd_upper_nxt     = freerun_latch[63:32];
    assign smartnic_322mhz_regs.freerun_rd_lower_nxt     = freerun_latch[31:0];

    always @(posedge clk) timestamp_rd_latch_wr_evt_d1  <= smartnic_322mhz_regs.timestamp_rd_latch_wr_evt;

    assign smartnic_322mhz_regs.timestamp_rd_upper_nxt_v = timestamp_rd_latch_wr_evt_d1;
    assign smartnic_322mhz_regs.timestamp_rd_lower_nxt_v = timestamp_rd_latch_wr_evt_d1;

    assign smartnic_322mhz_regs.freerun_rd_upper_nxt_v   = timestamp_rd_latch_wr_evt_d1;
    assign smartnic_322mhz_regs.freerun_rd_lower_nxt_v   = timestamp_rd_latch_wr_evt_d1;

endmodule // smartnic_322mhz_timestamp
