// =============================================================================
//  Notice: This computer software was prepared by The Regents of the
//  University of California through Lawrence Berkeley National Laboratory
//  and Jonathan Sewter hereinafter the Contractor, under Contract No.
//  DE-AC02-05CH11231 with the Department of Energy (DOE). All rights in the
//  computer software are reserved by DOE on behalf of the United States
//  Government and the Contractor as provided in the Contract. You are
//  authorized to use this computer software for Governmental purposes but it
//  is not to be released or distributed to the public.
//
//  NEITHER THE GOVERNMENT NOR THE CONTRACTOR MAKES ANY WARRANTY, EXPRESS OR
//  IMPLIED, OR ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.
//
//  This notice including this sentence must appear on any copies of this
//  computer software.
// =============================================================================

module smartnic_322mhz_hbm #(
    parameter bit HBM_STACK = 1'b0// 0: Left stack (4GB); 1: Right stack (4GB)
) (
    // Clock/reset
    input logic            clk,
    input logic            rstn,

    // HBM reference clock
    input logic            hbm_ref_clk,

    // 100MHz clock (for APB)
    input logic            clk_100mhz,

    // AXI-L control interface
    axi4l_intf.peripheral  axil_if,

    // AXI3 memory interfaces
    axi3_intf.peripheral   axi_if [16]
);

    // Signals
    logic       srst;
    logic       init_done;
    logic       dram_status_cattrip;
    logic [6:0] dram_status_temp;

    // -------------------------------------------
    // Interfaces
    // -------------------------------------------
    apb_intf   apb_if ();
    axi3_intf #(.DATA_BYTE_WID(32), .ADDR_WID(33), .ID_T(logic[5:0])) axi_if__ctrl [16] ();

    // ----------------------------------------------------------------
    // Reset synchronization
    // ----------------------------------------------------------------
    sync_reset i_sync_reset (
        .rst_in   ( rstn ),
        .clk_out  ( clk ),
        .srst_out ( srst )
    );
    // -------------------------------------------
    // Instantiations
    // -------------------------------------------
    xilinx_hbm_ctrl i_xilinx_hbm_ctrl (
        .apb_clk ( clk_100mhz ),
        .axi_if  ( axi_if__ctrl ),
        .*
    );

    // Terminate control interfaces
    generate
        for (genvar i = 0; i < 16; i++) begin : g__mc_ctrl
            axi3_intf_peripheral_term i_axi3_intf_peripheral_term__ctrl (.axi3_if(axi_if__ctrl[i]));
        end : g__mc_ctrl
    endgenerate

    // Xilinx HBM IP (single stack) ports
    // -----------------------------------------
    // Reference clock
    logic         HBM_REF_CLK_0;
    // Channel 0
    logic         AXI_00_ACLK;
    logic         AXI_00_ARESET_N;
    logic [32:0]  AXI_00_ARADDR;
    logic [1:0]   AXI_00_ARBURST;
    logic [5:0]   AXI_00_ARID;
    logic [3:0]   AXI_00_ARLEN;
    logic [2:0]   AXI_00_ARSIZE;
    logic         AXI_00_ARVALID;
    logic [32:0]  AXI_00_AWADDR;
    logic [1:0]   AXI_00_AWBURST;
    logic [5:0]   AXI_00_AWID;
    logic [3:0]   AXI_00_AWLEN;
    logic [2:0]   AXI_00_AWSIZE;
    logic         AXI_00_AWVALID;
    logic         AXI_00_RREADY;
    logic         AXI_00_BREADY;
    logic [255:0] AXI_00_WDATA;
    logic         AXI_00_WLAST;
    logic [31:0]  AXI_00_WSTRB;
    logic [31:0]  AXI_00_WDATA_PARITY;
    logic         AXI_00_WVALID;
    logic         AXI_00_ARREADY;
    logic         AXI_00_AWREADY;
    logic [31:0]  AXI_00_RDATA_PARITY;
    logic [255:0] AXI_00_RDATA;
    logic [5:0]   AXI_00_RID;
    logic         AXI_00_RLAST;
    logic [1:0]   AXI_00_RRESP;
    logic         AXI_00_RVALID;
    logic         AXI_00_WREADY;
    logic [5:0]   AXI_00_BID;
    logic [1:0]   AXI_00_BRESP;
    logic         AXI_00_BVALID;
    // Channel 1
    logic         AXI_01_ACLK;
    logic         AXI_01_ARESET_N;
    logic [32:0]  AXI_01_ARADDR;
    logic [1:0]   AXI_01_ARBURST;
    logic [5:0]   AXI_01_ARID;
    logic [3:0]   AXI_01_ARLEN;
    logic [2:0]   AXI_01_ARSIZE;
    logic         AXI_01_ARVALID;
    logic [32:0]  AXI_01_AWADDR;
    logic [1:0]   AXI_01_AWBURST;
    logic [5:0]   AXI_01_AWID;
    logic [3:0]   AXI_01_AWLEN;
    logic [2:0]   AXI_01_AWSIZE;
    logic         AXI_01_AWVALID;
    logic         AXI_01_RREADY;
    logic         AXI_01_BREADY;
    logic [255:0] AXI_01_WDATA;
    logic         AXI_01_WLAST;
    logic [31:0]  AXI_01_WSTRB;
    logic [31:0]  AXI_01_WDATA_PARITY;
    logic         AXI_01_WVALID;
    logic         AXI_01_ARREADY;
    logic         AXI_01_AWREADY;
    logic [31:0]  AXI_01_RDATA_PARITY;
    logic [255:0] AXI_01_RDATA;
    logic [5:0]   AXI_01_RID;
    logic         AXI_01_RLAST;
    logic [1:0]   AXI_01_RRESP;
    logic         AXI_01_RVALID;
    logic         AXI_01_WREADY;
    logic [5:0]   AXI_01_BID;
    logic [1:0]   AXI_01_BRESP;
    logic         AXI_01_BVALID;

    // Channel 2
    logic         AXI_02_ACLK;
    logic         AXI_02_ARESET_N;
    logic [32:0]  AXI_02_ARADDR;
    logic [1:0]   AXI_02_ARBURST;
    logic [5:0]   AXI_02_ARID;
    logic [3:0]   AXI_02_ARLEN;
    logic [2:0]   AXI_02_ARSIZE;
    logic         AXI_02_ARVALID;
    logic [32:0]  AXI_02_AWADDR;
    logic [1:0]   AXI_02_AWBURST;
    logic [5:0]   AXI_02_AWID;
    logic [3:0]   AXI_02_AWLEN;
    logic [2:0]   AXI_02_AWSIZE;
    logic         AXI_02_AWVALID;
    logic         AXI_02_RREADY;
    logic         AXI_02_BREADY;
    logic [255:0] AXI_02_WDATA;
    logic         AXI_02_WLAST;
    logic [31:0]  AXI_02_WSTRB;
    logic [31:0]  AXI_02_WDATA_PARITY;
    logic         AXI_02_WVALID;
    logic         AXI_02_ARREADY;
    logic         AXI_02_AWREADY;
    logic [31:0]  AXI_02_RDATA_PARITY;
    logic [255:0] AXI_02_RDATA;
    logic [5:0]   AXI_02_RID;
    logic         AXI_02_RLAST;
    logic [1:0]   AXI_02_RRESP;
    logic         AXI_02_RVALID;
    logic         AXI_02_WREADY;
    logic [5:0]   AXI_02_BID;
    logic [1:0]   AXI_02_BRESP;
    logic         AXI_02_BVALID;
    // Channel 3
    logic         AXI_03_ACLK;
    logic         AXI_03_ARESET_N;
    logic [32:0]  AXI_03_ARADDR;
    logic [1:0]   AXI_03_ARBURST;
    logic [5:0]   AXI_03_ARID;
    logic [3:0]   AXI_03_ARLEN;
    logic [2:0]   AXI_03_ARSIZE;
    logic         AXI_03_ARVALID;
    logic [32:0]  AXI_03_AWADDR;
    logic [1:0]   AXI_03_AWBURST;
    logic [5:0]   AXI_03_AWID;
    logic [3:0]   AXI_03_AWLEN;
    logic [2:0]   AXI_03_AWSIZE;
    logic         AXI_03_AWVALID;
    logic         AXI_03_RREADY;
    logic         AXI_03_BREADY;
    logic [255:0] AXI_03_WDATA;
    logic         AXI_03_WLAST;
    logic [31:0]  AXI_03_WSTRB;
    logic [31:0]  AXI_03_WDATA_PARITY;
    logic         AXI_03_WVALID;
    logic         AXI_03_ARREADY;
    logic         AXI_03_AWREADY;
    logic [31:0]  AXI_03_RDATA_PARITY;
    logic [255:0] AXI_03_RDATA;
    logic [5:0]   AXI_03_RID;
    logic         AXI_03_RLAST;
    logic [1:0]   AXI_03_RRESP;
    logic         AXI_03_RVALID;
    logic         AXI_03_WREADY;
    logic [5:0]   AXI_03_BID;
    logic [1:0]   AXI_03_BRESP;
    logic         AXI_03_BVALID;
   // Channel 4
    logic         AXI_04_ACLK;
    logic         AXI_04_ARESET_N;
    logic [32:0]  AXI_04_ARADDR;
    logic [1:0]   AXI_04_ARBURST;
    logic [5:0]   AXI_04_ARID;
    logic [3:0]   AXI_04_ARLEN;
    logic [2:0]   AXI_04_ARSIZE;
    logic         AXI_04_ARVALID;
    logic [32:0]  AXI_04_AWADDR;
    logic [1:0]   AXI_04_AWBURST;
    logic [5:0]   AXI_04_AWID;
    logic [3:0]   AXI_04_AWLEN;
    logic [2:0]   AXI_04_AWSIZE;
    logic         AXI_04_AWVALID;
    logic         AXI_04_RREADY;
    logic         AXI_04_BREADY;
    logic [255:0] AXI_04_WDATA;
    logic         AXI_04_WLAST;
    logic [31:0]  AXI_04_WSTRB;
    logic [31:0]  AXI_04_WDATA_PARITY;
    logic         AXI_04_WVALID;
    logic         AXI_04_ARREADY;
    logic         AXI_04_AWREADY;
    logic [31:0]  AXI_04_RDATA_PARITY;
    logic [255:0] AXI_04_RDATA;
    logic [5:0]   AXI_04_RID;
    logic         AXI_04_RLAST;
    logic [1:0]   AXI_04_RRESP;
    logic         AXI_04_RVALID;
    logic         AXI_04_WREADY;
    logic [5:0]   AXI_04_BID;
    logic [1:0]   AXI_04_BRESP;
    logic         AXI_04_BVALID;
   // Channel 5
    logic         AXI_05_ACLK;
    logic         AXI_05_ARESET_N;
    logic [32:0]  AXI_05_ARADDR;
    logic [1:0]   AXI_05_ARBURST;
    logic [5:0]   AXI_05_ARID;
    logic [3:0]   AXI_05_ARLEN;
    logic [2:0]   AXI_05_ARSIZE;
    logic         AXI_05_ARVALID;
    logic [32:0]  AXI_05_AWADDR;
    logic [1:0]   AXI_05_AWBURST;
    logic [5:0]   AXI_05_AWID;
    logic [3:0]   AXI_05_AWLEN;
    logic [2:0]   AXI_05_AWSIZE;
    logic         AXI_05_AWVALID;
    logic         AXI_05_RREADY;
    logic         AXI_05_BREADY;
    logic [255:0] AXI_05_WDATA;
    logic         AXI_05_WLAST;
    logic [31:0]  AXI_05_WSTRB;
    logic [31:0]  AXI_05_WDATA_PARITY;
    logic         AXI_05_WVALID;
    logic         AXI_05_ARREADY;
    logic         AXI_05_AWREADY;
    logic [31:0]  AXI_05_RDATA_PARITY;
    logic [255:0] AXI_05_RDATA;
    logic [5:0]   AXI_05_RID;
    logic         AXI_05_RLAST;
    logic [1:0]   AXI_05_RRESP;
    logic         AXI_05_RVALID;
    logic         AXI_05_WREADY;
    logic [5:0]   AXI_05_BID;
    logic [1:0]   AXI_05_BRESP;
    logic         AXI_05_BVALID;
   // Channel 6
    logic         AXI_06_ACLK;
    logic         AXI_06_ARESET_N;
    logic [32:0]  AXI_06_ARADDR;
    logic [1:0]   AXI_06_ARBURST;
    logic [5:0]   AXI_06_ARID;
    logic [3:0]   AXI_06_ARLEN;
    logic [2:0]   AXI_06_ARSIZE;
    logic         AXI_06_ARVALID;
    logic [32:0]  AXI_06_AWADDR;
    logic [1:0]   AXI_06_AWBURST;
    logic [5:0]   AXI_06_AWID;
    logic [3:0]   AXI_06_AWLEN;
    logic [2:0]   AXI_06_AWSIZE;
    logic         AXI_06_AWVALID;
    logic         AXI_06_RREADY;
    logic         AXI_06_BREADY;
    logic [255:0] AXI_06_WDATA;
    logic         AXI_06_WLAST;
    logic [31:0]  AXI_06_WSTRB;
    logic [31:0]  AXI_06_WDATA_PARITY;
    logic         AXI_06_WVALID;
    logic         AXI_06_ARREADY;
    logic         AXI_06_AWREADY;
    logic [31:0]  AXI_06_RDATA_PARITY;
    logic [255:0] AXI_06_RDATA;
    logic [5:0]   AXI_06_RID;
    logic         AXI_06_RLAST;
    logic [1:0]   AXI_06_RRESP;
    logic         AXI_06_RVALID;
    logic         AXI_06_WREADY;
    logic [5:0]   AXI_06_BID;
    logic [1:0]   AXI_06_BRESP;
    logic         AXI_06_BVALID;
   // Channel 7
    logic         AXI_07_ACLK;
    logic         AXI_07_ARESET_N;
    logic [32:0]  AXI_07_ARADDR;
    logic [1:0]   AXI_07_ARBURST;
    logic [5:0]   AXI_07_ARID;
    logic [3:0]   AXI_07_ARLEN;
    logic [2:0]   AXI_07_ARSIZE;
    logic         AXI_07_ARVALID;
    logic [32:0]  AXI_07_AWADDR;
    logic [1:0]   AXI_07_AWBURST;
    logic [5:0]   AXI_07_AWID;
    logic [3:0]   AXI_07_AWLEN;
    logic [2:0]   AXI_07_AWSIZE;
    logic         AXI_07_AWVALID;
    logic         AXI_07_RREADY;
    logic         AXI_07_BREADY;
    logic [255:0] AXI_07_WDATA;
    logic         AXI_07_WLAST;
    logic [31:0]  AXI_07_WSTRB;
    logic [31:0]  AXI_07_WDATA_PARITY;
    logic         AXI_07_WVALID;
    logic         AXI_07_ARREADY;
    logic         AXI_07_AWREADY;
    logic [31:0]  AXI_07_RDATA_PARITY;
    logic [255:0] AXI_07_RDATA;
    logic [5:0]   AXI_07_RID;
    logic         AXI_07_RLAST;
    logic [1:0]   AXI_07_RRESP;
    logic         AXI_07_RVALID;
    logic         AXI_07_WREADY;
    logic [5:0]   AXI_07_BID;
    logic [1:0]   AXI_07_BRESP;
    logic         AXI_07_BVALID;
   // Channel 8
    logic         AXI_08_ACLK;
    logic         AXI_08_ARESET_N;
    logic [32:0]  AXI_08_ARADDR;
    logic [1:0]   AXI_08_ARBURST;
    logic [5:0]   AXI_08_ARID;
    logic [3:0]   AXI_08_ARLEN;
    logic [2:0]   AXI_08_ARSIZE;
    logic         AXI_08_ARVALID;
    logic [32:0]  AXI_08_AWADDR;
    logic [1:0]   AXI_08_AWBURST;
    logic [5:0]   AXI_08_AWID;
    logic [3:0]   AXI_08_AWLEN;
    logic [2:0]   AXI_08_AWSIZE;
    logic         AXI_08_AWVALID;
    logic         AXI_08_RREADY;
    logic         AXI_08_BREADY;
    logic [255:0] AXI_08_WDATA;
    logic         AXI_08_WLAST;
    logic [31:0]  AXI_08_WSTRB;
    logic [31:0]  AXI_08_WDATA_PARITY;
    logic         AXI_08_WVALID;
    logic         AXI_08_ARREADY;
    logic         AXI_08_AWREADY;
    logic [31:0]  AXI_08_RDATA_PARITY;
    logic [255:0] AXI_08_RDATA;
    logic [5:0]   AXI_08_RID;
    logic         AXI_08_RLAST;
    logic [1:0]   AXI_08_RRESP;
    logic         AXI_08_RVALID;
    logic         AXI_08_WREADY;
    logic [5:0]   AXI_08_BID;
    logic [1:0]   AXI_08_BRESP;
    logic         AXI_08_BVALID;
   // Channel 9
    logic         AXI_09_ACLK;
    logic         AXI_09_ARESET_N;
    logic [32:0]  AXI_09_ARADDR;
    logic [1:0]   AXI_09_ARBURST;
    logic [5:0]   AXI_09_ARID;
    logic [3:0]   AXI_09_ARLEN;
    logic [2:0]   AXI_09_ARSIZE;
    logic         AXI_09_ARVALID;
    logic [32:0]  AXI_09_AWADDR;
    logic [1:0]   AXI_09_AWBURST;
    logic [5:0]   AXI_09_AWID;
    logic [3:0]   AXI_09_AWLEN;
    logic [2:0]   AXI_09_AWSIZE;
    logic         AXI_09_AWVALID;
    logic         AXI_09_RREADY;
    logic         AXI_09_BREADY;
    logic [255:0] AXI_09_WDATA;
    logic         AXI_09_WLAST;
    logic [31:0]  AXI_09_WSTRB;
    logic [31:0]  AXI_09_WDATA_PARITY;
    logic         AXI_09_WVALID;
    logic         AXI_09_ARREADY;
    logic         AXI_09_AWREADY;
    logic [31:0]  AXI_09_RDATA_PARITY;
    logic [255:0] AXI_09_RDATA;
    logic [5:0]   AXI_09_RID;
    logic         AXI_09_RLAST;
    logic [1:0]   AXI_09_RRESP;
    logic         AXI_09_RVALID;
    logic         AXI_09_WREADY;
    logic [5:0]   AXI_09_BID;
    logic [1:0]   AXI_09_BRESP;
    logic         AXI_09_BVALID;
   // Channel 10
    logic         AXI_10_ACLK;
    logic         AXI_10_ARESET_N;
    logic [32:0]  AXI_10_ARADDR;
    logic [1:0]   AXI_10_ARBURST;
    logic [5:0]   AXI_10_ARID;
    logic [3:0]   AXI_10_ARLEN;
    logic [2:0]   AXI_10_ARSIZE;
    logic         AXI_10_ARVALID;
    logic [32:0]  AXI_10_AWADDR;
    logic [1:0]   AXI_10_AWBURST;
    logic [5:0]   AXI_10_AWID;
    logic [3:0]   AXI_10_AWLEN;
    logic [2:0]   AXI_10_AWSIZE;
    logic         AXI_10_AWVALID;
    logic         AXI_10_RREADY;
    logic         AXI_10_BREADY;
    logic [255:0] AXI_10_WDATA;
    logic         AXI_10_WLAST;
    logic [31:0]  AXI_10_WSTRB;
    logic [31:0]  AXI_10_WDATA_PARITY;
    logic         AXI_10_WVALID;
    logic         AXI_10_ARREADY;
    logic         AXI_10_AWREADY;
    logic [31:0]  AXI_10_RDATA_PARITY;
    logic [255:0] AXI_10_RDATA;
    logic [5:0]   AXI_10_RID;
    logic         AXI_10_RLAST;
    logic [1:0]   AXI_10_RRESP;
    logic         AXI_10_RVALID;
    logic         AXI_10_WREADY;
    logic [5:0]   AXI_10_BID;
    logic [1:0]   AXI_10_BRESP;
    logic         AXI_10_BVALID;
   // Channel 11
    logic         AXI_11_ACLK;
    logic         AXI_11_ARESET_N;
    logic [32:0]  AXI_11_ARADDR;
    logic [1:0]   AXI_11_ARBURST;
    logic [5:0]   AXI_11_ARID;
    logic [3:0]   AXI_11_ARLEN;
    logic [2:0]   AXI_11_ARSIZE;
    logic         AXI_11_ARVALID;
    logic [32:0]  AXI_11_AWADDR;
    logic [1:0]   AXI_11_AWBURST;
    logic [5:0]   AXI_11_AWID;
    logic [3:0]   AXI_11_AWLEN;
    logic [2:0]   AXI_11_AWSIZE;
    logic         AXI_11_AWVALID;
    logic         AXI_11_RREADY;
    logic         AXI_11_BREADY;
    logic [255:0] AXI_11_WDATA;
    logic         AXI_11_WLAST;
    logic [31:0]  AXI_11_WSTRB;
    logic [31:0]  AXI_11_WDATA_PARITY;
    logic         AXI_11_WVALID;
    logic         AXI_11_ARREADY;
    logic         AXI_11_AWREADY;
    logic [31:0]  AXI_11_RDATA_PARITY;
    logic [255:0] AXI_11_RDATA;
    logic [5:0]   AXI_11_RID;
    logic         AXI_11_RLAST;
    logic [1:0]   AXI_11_RRESP;
    logic         AXI_11_RVALID;
    logic         AXI_11_WREADY;
    logic [5:0]   AXI_11_BID;
    logic [1:0]   AXI_11_BRESP;
    logic         AXI_11_BVALID;
   // Channel 12
    logic         AXI_12_ACLK;
    logic         AXI_12_ARESET_N;
    logic [32:0]  AXI_12_ARADDR;
    logic [1:0]   AXI_12_ARBURST;
    logic [5:0]   AXI_12_ARID;
    logic [3:0]   AXI_12_ARLEN;
    logic [2:0]   AXI_12_ARSIZE;
    logic         AXI_12_ARVALID;
    logic [32:0]  AXI_12_AWADDR;
    logic [1:0]   AXI_12_AWBURST;
    logic [5:0]   AXI_12_AWID;
    logic [3:0]   AXI_12_AWLEN;
    logic [2:0]   AXI_12_AWSIZE;
    logic         AXI_12_AWVALID;
    logic         AXI_12_RREADY;
    logic         AXI_12_BREADY;
    logic [255:0] AXI_12_WDATA;
    logic         AXI_12_WLAST;
    logic [31:0]  AXI_12_WSTRB;
    logic [31:0]  AXI_12_WDATA_PARITY;
    logic         AXI_12_WVALID;
    logic         AXI_12_ARREADY;
    logic         AXI_12_AWREADY;
    logic [31:0]  AXI_12_RDATA_PARITY;
    logic [255:0] AXI_12_RDATA;
    logic [5:0]   AXI_12_RID;
    logic         AXI_12_RLAST;
    logic [1:0]   AXI_12_RRESP;
    logic         AXI_12_RVALID;
    logic         AXI_12_WREADY;
    logic [5:0]   AXI_12_BID;
    logic [1:0]   AXI_12_BRESP;
    logic         AXI_12_BVALID;
   // Channel 13
    logic         AXI_13_ACLK;
    logic         AXI_13_ARESET_N;
    logic [32:0]  AXI_13_ARADDR;
    logic [1:0]   AXI_13_ARBURST;
    logic [5:0]   AXI_13_ARID;
    logic [3:0]   AXI_13_ARLEN;
    logic [2:0]   AXI_13_ARSIZE;
    logic         AXI_13_ARVALID;
    logic [32:0]  AXI_13_AWADDR;
    logic [1:0]   AXI_13_AWBURST;
    logic [5:0]   AXI_13_AWID;
    logic [3:0]   AXI_13_AWLEN;
    logic [2:0]   AXI_13_AWSIZE;
    logic         AXI_13_AWVALID;
    logic         AXI_13_RREADY;
    logic         AXI_13_BREADY;
    logic [255:0] AXI_13_WDATA;
    logic         AXI_13_WLAST;
    logic [31:0]  AXI_13_WSTRB;
    logic [31:0]  AXI_13_WDATA_PARITY;
    logic         AXI_13_WVALID;
    logic         AXI_13_ARREADY;
    logic         AXI_13_AWREADY;
    logic [31:0]  AXI_13_RDATA_PARITY;
    logic [255:0] AXI_13_RDATA;
    logic [5:0]   AXI_13_RID;
    logic         AXI_13_RLAST;
    logic [1:0]   AXI_13_RRESP;
    logic         AXI_13_RVALID;
    logic         AXI_13_WREADY;
    logic [5:0]   AXI_13_BID;
    logic [1:0]   AXI_13_BRESP;
    logic         AXI_13_BVALID;
   // Channel 14
    logic         AXI_14_ACLK;
    logic         AXI_14_ARESET_N;
    logic [32:0]  AXI_14_ARADDR;
    logic [1:0]   AXI_14_ARBURST;
    logic [5:0]   AXI_14_ARID;
    logic [3:0]   AXI_14_ARLEN;
    logic [2:0]   AXI_14_ARSIZE;
    logic         AXI_14_ARVALID;
    logic [32:0]  AXI_14_AWADDR;
    logic [1:0]   AXI_14_AWBURST;
    logic [5:0]   AXI_14_AWID;
    logic [3:0]   AXI_14_AWLEN;
    logic [2:0]   AXI_14_AWSIZE;
    logic         AXI_14_AWVALID;
    logic         AXI_14_RREADY;
    logic         AXI_14_BREADY;
    logic [255:0] AXI_14_WDATA;
    logic         AXI_14_WLAST;
    logic [31:0]  AXI_14_WSTRB;
    logic [31:0]  AXI_14_WDATA_PARITY;
    logic         AXI_14_WVALID;
    logic         AXI_14_ARREADY;
    logic         AXI_14_AWREADY;
    logic [31:0]  AXI_14_RDATA_PARITY;
    logic [255:0] AXI_14_RDATA;
    logic [5:0]   AXI_14_RID;
    logic         AXI_14_RLAST;
    logic [1:0]   AXI_14_RRESP;
    logic         AXI_14_RVALID;
    logic         AXI_14_WREADY;
    logic [5:0]   AXI_14_BID;
    logic [1:0]   AXI_14_BRESP;
    logic         AXI_14_BVALID;
    // Channel 15
    logic         AXI_15_ACLK;
    logic         AXI_15_ARESET_N;
    logic [32:0]  AXI_15_ARADDR;
    logic [1:0]   AXI_15_ARBURST;
    logic [5:0]   AXI_15_ARID;
    logic [3:0]   AXI_15_ARLEN;
    logic [2:0]   AXI_15_ARSIZE;
    logic         AXI_15_ARVALID;
    logic [32:0]  AXI_15_AWADDR;
    logic [1:0]   AXI_15_AWBURST;
    logic [5:0]   AXI_15_AWID;
    logic [3:0]   AXI_15_AWLEN;
    logic [2:0]   AXI_15_AWSIZE;
    logic         AXI_15_AWVALID;
    logic         AXI_15_RREADY;
    logic         AXI_15_BREADY;
    logic [255:0] AXI_15_WDATA;
    logic         AXI_15_WLAST;
    logic [31:0]  AXI_15_WSTRB;
    logic [31:0]  AXI_15_WDATA_PARITY;
    logic         AXI_15_WVALID;
    logic         AXI_15_ARREADY;
    logic         AXI_15_AWREADY;
    logic [31:0]  AXI_15_RDATA_PARITY;
    logic [255:0] AXI_15_RDATA;
    logic [5:0]   AXI_15_RID;
    logic         AXI_15_RLAST;
    logic [1:0]   AXI_15_RRESP;
    logic         AXI_15_RVALID;
    logic         AXI_15_WREADY;
    logic [5:0]   AXI_15_BID;
    logic [1:0]   AXI_15_BRESP;
    logic         AXI_15_BVALID;
    // APB interface
    logic [31:0]  APB_0_PWDATA;
    logic [21:0]  APB_0_PADDR;
    logic         APB_0_PCLK;
    logic         APB_0_PENABLE;
    logic         APB_0_PRESET_N;
    logic         APB_0_PSEL;
    logic         APB_0_PWRITE;
    logic [31:0]  APB_0_PRDATA;
    logic         APB_0_PREADY;
    logic         APB_0_PSLVERR;
    logic         apb_complete_0;
    // DRAM status
    logic         DRAM_0_STAT_CATTRIP;
    logic [6:0]   DRAM_0_STAT_TEMP;

    // Xilinx HBM controller wrapper interface
    xilinx_hbm_4g_if i_xilinx_hbm_4g_if (
        .*
    );
 
`ifdef SIMULATION
    
    // HBM simulations not supported in Vivado Simulator
    // (instantiate functional model instead)
    xilinx_hbm_4g_bfm i_hbm_4g_bfm (.*);

`else // SYNTHESIS
   
    // Xilinx HBM controller instantiation
    generate
        if (HBM_STACK == 1'b0) begin : g__hbm_left
            hbm_4g_left i_hbm_4g_left (.*);
        end : g__hbm_left
        else begin : g__hbm_right
            hbm_4g_right i_hbm_4g_right (.*);
        end : g__hbm_right
    endgenerate
`endif

endmodule : smartnic_322mhz_hbm
