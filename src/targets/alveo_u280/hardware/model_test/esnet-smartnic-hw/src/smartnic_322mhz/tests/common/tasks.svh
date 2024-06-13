//=======================================================================
// Global variables
//=======================================================================
localparam NUM_PORTS = 4;

import smartnic_322mhz_pkg::*;
port_t out_port_map [NUM_PORTS-1:0];  // vector specifies output port for each input stream.

string in_pcap  [NUM_PORTS-1:0];  // vector specifies the in_pcap file for each input stream.
string out_pcap [NUM_PORTS-1:0];  // vector specifies the out_pcap file for each input stream.

// variables for probe checks.
int tx_pkt_cnt  [NUM_PORTS-1:0];  // captures the tx pkt & byte counts from the pcap file for a given test.
int tx_byte_cnt [NUM_PORTS-1:0];
int rx_pkt_cnt  [NUM_PORTS-1:0];  // captures the rx pkt & byte counts from the pcap file for a given test.
int rx_byte_cnt [NUM_PORTS-1:0];
int rx_pkt_tot  = 0;
int rx_byte_tot = 0;
int exp_pkt_cnt [NUM_PORTS-1:0];  // vector specifies the expected number of pkts received for each stream.

typedef enum logic [31:0] {
    PROBE_FROM_CMAC_PORT0      = 'h8000,
    DROPS_OVFL_FROM_CMAC_PORT0 = 'h8400,
    DROPS_ERR_FROM_CMAC_PORT0  = 'h8800,
    PROBE_FROM_CMAC_PORT1      = 'h8c00,
    DROPS_OVFL_FROM_CMAC_PORT1 = 'h9000,
    DROPS_ERR_FROM_CMAC_PORT1  = 'h9400,
    PROBE_FROM_HOST_PORT0      = 'h9800,
    PROBE_FROM_HOST_PORT1      = 'h9c00,

    PROBE_CORE_TO_APP0         = 'ha000,
    PROBE_CORE_TO_APP1         = 'ha400,
    PROBE_APP0_TO_CORE         = 'ha800,
    PROBE_APP1_TO_CORE         = 'hac00,

    PROBE_TO_CMAC_PORT0        = 'hb000,
    DROPS_OVFL_TO_CMAC_PORT0   = 'hb400,
    PROBE_TO_CMAC_PORT1        = 'hb800,
    DROPS_OVFL_TO_CMAC_PORT1   = 'hbc00,
    PROBE_TO_HOST_PORT0        = 'hc000,
    DROPS_OVFL_TO_HOST_PORT0   = 'hc400,
    PROBE_TO_HOST_PORT1        = 'hc800,
    DROPS_OVFL_TO_HOST_PORT1   = 'hcc00,

    PROBE_TO_BYPASS            = 'hd000,

    DROPS_FROM_IGR_SW          = 'hd400,
    DROPS_FROM_BYPASS          = 'hd800,
    DROPS_FROM_APP0            = 'hdc00
    } cntr_addr_encoding_t;

typedef union packed {
    cntr_addr_encoding_t  encoded;
    logic [31:0]          raw;
} cntr_addr_t;

smartnic_322mhz_reg_pkg::reg_switch_config_t switch_config;


//=======================================================================
// Tasks
//=======================================================================

// Execute block reset (dataplane + control plane)
task reset();
    automatic bit reset_done;
    automatic string msg;
    env.reset();
    env.wait_reset_done(reset_done, msg);
    `FAIL_IF_LOG((reset_done == 0), msg);
endtask


// Force loopback
task force_loopback();
    `INFO("Forcing loopback from ingress switch to egress switch.");
    force tb.DUT.axis_switch_egress.s_axis_tvalid = tb.DUT.axis_switch_ingress.m_axis_tvalid;
    force tb.DUT.axis_switch_egress.s_axis_tdata  = tb.DUT.axis_switch_ingress.m_axis_tdata;
    force tb.DUT.axis_switch_egress.s_axis_tkeep  = tb.DUT.axis_switch_ingress.m_axis_tkeep;
    force tb.DUT.axis_switch_egress.s_axis_tlast  = tb.DUT.axis_switch_ingress.m_axis_tlast;
    force tb.DUT.axis_switch_egress.s_axis_tid    = tb.DUT.axis_switch_ingress.m_axis_tid;
    force tb.DUT.axis_switch_egress.s_axis_tdest  = tb.DUT.axis_switch_ingress.m_axis_tdest;

    force tb.DUT.axis_switch_ingress.m_axis_tready = tb.DUT.axis_switch_egress.s_axis_tready;
endtask // force_loopback


// Send packets described in PCAP file on AXI-S input interface
task send_pcap (
    input string  pcap_filename,
    input int     num_pkts=0, start_idx=0, twait=0,
    input port_t  id=0, dest=0,
    input bit     user=0 );

    env.axis_driver[id].send_from_pcap(pcap_filename, num_pkts, start_idx, twait, id, dest, user);
endtask


// Compare packets
task compare_pkts(input byte pkt1[$], pkt2[$]);
    automatic int byte_idx = 0;

    if ( pkt1.size() != pkt2.size() ) begin
       $display("pkt1:"); pcap_pkg::print_pkt_data(pkt1);
       $display("pkt2:"); pcap_pkg::print_pkt_data(pkt2);

      `FAIL_IF_LOG( pkt1.size() != pkt2.size(),
                    $sformatf("FAIL!!! Packet size mismatch. size1=%0d size2=%0d", pkt1.size(), pkt2.size()))
    end

    byte_idx = 0;
    while ( byte_idx < pkt1.size() ) begin
       //if (pkt1[byte_idx] == pkt2[byte_idx]) $display("Pass. Packet bytes match at byte_idx: %d", byte_idx);
       if (pkt1[byte_idx] != pkt2[byte_idx]) begin
          $display("pkt1:"); pcap_pkg::print_pkt_data(pkt1);
          $display("pkt2:"); pcap_pkg::print_pkt_data(pkt2);
	  
          `FAIL_IF_LOG( pkt1[byte_idx] != pkt2[byte_idx],
                        $sformatf("FAIL!!! Packet bytes mismatch at byte_idx: 0x%0h (d:%0d)", byte_idx, byte_idx) )
       end
       byte_idx++;
    end
endtask


task init_sw_config_regs();
   env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_IGR_SW_TID[0], 0 );
   env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_IGR_SW_TID[1], 1 );
   env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_IGR_SW_TID[2], 2 );
   env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_IGR_SW_TID[3], 3 );

   env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_IGR_SW_TDEST[0], 2 );
   env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_IGR_SW_TDEST[1], 2 );
   env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_IGR_SW_TDEST[2], 2 );
   env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_IGR_SW_TDEST[3], 2 );

   env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_BYPASS_TDEST[0], 2 );
   env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_BYPASS_TDEST[1], 3 );
   env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_BYPASS_TDEST[2], 0 );
   env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_BYPASS_TDEST[3], 1 );

   env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_APP_0_TDEST_REMAP[0], 0 );
   env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_APP_0_TDEST_REMAP[1], 1 );
   env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_APP_0_TDEST_REMAP[2], 2 );
   env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_APP_0_TDEST_REMAP[3], 3 );

   env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_APP_1_TDEST_REMAP[0], 0 );
   env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_APP_1_TDEST_REMAP[1], 1 );
   env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_APP_1_TDEST_REMAP[2], 2 );
   env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_APP_1_TDEST_REMAP[3], 3 );
endtask


task configure_port_map();
   env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_BYPASS_TDEST[0], out_port_map[0] );
   env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_BYPASS_TDEST[1], out_port_map[1] );
   env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_BYPASS_TDEST[2], out_port_map[2] );
   env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_BYPASS_TDEST[3], out_port_map[3] );
endtask


task automatic run_pkt_stream (
       input port_t           in_port, out_port,
       input string           in_pcap, out_pcap,
       output logic [63:0]    tx_pkt_cnt, tx_byte_cnt,
       output logic [63:0]    rx_pkt_cnt, rx_byte_cnt,
       input int              exp_pkt_cnt = 0,
       input int              tpause = 0, twait = 0, init_pause = 0,
       input bit              tuser = 0
    );
   
    // variabes for reading pcap data$
    byte                      pcap_data[$][$];
    pcap_pkg::pcap_hdr_t      pcap_hdr;
    pcap_pkg::pcaprec_hdr_t   pcap_record_hdr[$];

    // variables for sending packet data
    int num_pkts  = 0;
    int start_idx = 0;

    // variables for receiving (monitoring) packet data
    byte  rx_data[$];
    bit   id;
    bit   dest;
    bit   user;

   `INFO($sformatf("Stream in_port %0d: Reading input pcap file...", in_port));
    pcap_pkg::read_pcap(in_pcap, pcap_hdr, pcap_record_hdr, pcap_data);
    tx_pkt_cnt  = pcap_record_hdr.size();
    tx_byte_cnt = 0;  foreach (pcap_data[i,]) tx_byte_cnt += pcap_data[i].size();

   `INFO($sformatf("Stream in_port %0d: Reading output pcap file...", in_port));
    pcap_pkg::read_pcap(out_pcap, pcap_hdr, pcap_record_hdr, pcap_data);
   
   `INFO($sformatf("Stream in_port %0d: Starting packet stream...", in_port));
    fork
       begin
          // Send packets	    
          send_pcap(in_pcap, num_pkts, start_idx, twait, in_port, out_port, tuser);
       end
       begin
          // Monitor output packets
          rx_pkt_cnt = 0; rx_byte_cnt = 0;

          if (exp_pkt_cnt == 0) exp_pkt_cnt = pcap_record_hdr.size();

          #(init_pause);
          while (rx_pkt_cnt < exp_pkt_cnt) begin
             env.axis_monitor[out_port].receive_raw(.data(rx_data), .id(id), .dest(dest), .user(user), .tpause(tpause));
             rx_pkt_cnt++;
             rx_byte_cnt = rx_byte_cnt + rx_data.size();
            `INFO($sformatf("       Stream in_port %0d (out_port %0d): Receiving packet # %0d (of %0d)...", 
                                    in_port, out_port, rx_pkt_cnt, exp_pkt_cnt) );
             // pcap_pkg::print_pkt_data(rx_data);
             compare_pkts(rx_data, pcap_data[start_idx+rx_pkt_cnt-1]);
          end
       end
    join
endtask;


task run_stream_test (input int tpause = 0, twait = 0);
    fork
       run_pkt_stream ( .in_port(0), .out_port(out_port_map[0]), .in_pcap(in_pcap[0]), .out_pcap(out_pcap[0]),
                        .tx_pkt_cnt(tx_pkt_cnt[0]), .tx_byte_cnt(tx_byte_cnt[0]), 
                        .rx_pkt_cnt(rx_pkt_cnt[0]), .rx_byte_cnt(rx_byte_cnt[0]),
                        .exp_pkt_cnt(exp_pkt_cnt[0]),
                        .tpause(tpause), .twait(twait) );

       run_pkt_stream ( .in_port(1), .out_port(out_port_map[1]), .in_pcap(in_pcap[1]), .out_pcap(out_pcap[1]),
                        .tx_pkt_cnt(tx_pkt_cnt[1]), .tx_byte_cnt(tx_byte_cnt[1]), 
                        .rx_pkt_cnt(rx_pkt_cnt[1]), .rx_byte_cnt(rx_byte_cnt[1]),
                        .exp_pkt_cnt(exp_pkt_cnt[1]),
                        .tpause(tpause), .twait(twait) );

       run_pkt_stream ( .in_port(2), .out_port(out_port_map[2]), .in_pcap(in_pcap[2]), .out_pcap(out_pcap[2]),
                        .tx_pkt_cnt(tx_pkt_cnt[2]), .tx_byte_cnt(tx_byte_cnt[2]), 
                        .rx_pkt_cnt(rx_pkt_cnt[2]), .rx_byte_cnt(rx_byte_cnt[2]),
                        .exp_pkt_cnt(exp_pkt_cnt[2]),
                        .tpause(tpause), .twait(twait) );

       run_pkt_stream ( .in_port(3), .out_port(out_port_map[3]), .in_pcap(in_pcap[3]), .out_pcap(out_pcap[3]),
                        .tx_pkt_cnt(tx_pkt_cnt[3]), .tx_byte_cnt(tx_byte_cnt[3]), 
                        .rx_pkt_cnt(rx_pkt_cnt[3]), .rx_byte_cnt(rx_byte_cnt[3]),
                        .exp_pkt_cnt(exp_pkt_cnt[3]),
                        .tpause(tpause), .twait(twait) );

    join
endtask
   

task check_stream_test_probes (input logic ovfl_mode = 0);
    for (int i=0; i<NUM_PORTS; i++) begin
       check_stream_probes (
          .in_port         (i), 
          .out_port        (out_port_map[i]),
          .exp_good_pkts   (rx_pkt_cnt[i]), 
          .exp_good_bytes  (rx_byte_cnt[i]), 
          .exp_ovfl_pkts   (tx_pkt_cnt[i]  - rx_pkt_cnt[i]), 
          .exp_ovfl_bytes  (tx_byte_cnt[i] - rx_byte_cnt[i]),
          .ovfl_mode       (ovfl_mode)
       );
    end
endtask;


task check_stream_probes ( input port_t       in_port, out_port,
                           input logic [63:0] exp_good_pkts, exp_good_bytes, exp_ovfl_pkts=0, exp_ovfl_bytes=0,
                           input int          ovfl_mode = 0 );  // ovfl_mode: 0-egress_ovfl, 1-ingress_ovfl, 2-pkt_drops

    cntr_addr_t in_port_base_addr, out_port_base_addr;
    logic [63:0] exp_tot_pkts, exp_tot_bytes;

    // establish base addr for ingress probe
    case (in_port)
           CMAC_PORT0 : in_port_base_addr = PROBE_FROM_CMAC_PORT0; // 'h8000;
           CMAC_PORT1 : in_port_base_addr = PROBE_FROM_CMAC_PORT1; // 'h8c00;
           HOST_PORT0 : in_port_base_addr = PROBE_FROM_HOST_PORT0; // 'h9800;
           HOST_PORT1 : in_port_base_addr = PROBE_FROM_HOST_PORT1; // 'h9c00;
           default    : in_port_base_addr = 'hxxxx;
    endcase

    // establish base addr for egress probe
    case (out_port)
           CMAC_PORT0 : out_port_base_addr = PROBE_TO_CMAC_PORT0; // 'hb000;
           CMAC_PORT1 : out_port_base_addr = PROBE_TO_CMAC_PORT1; // 'hb800;
           HOST_PORT0 : out_port_base_addr = PROBE_TO_HOST_PORT0; // 'hc000;
           HOST_PORT1 : out_port_base_addr = PROBE_TO_HOST_PORT1; // 'hc800;
           default    : out_port_base_addr = 'hxxxx;
    endcase

    // establish pkt and byte totals       
    exp_tot_pkts  = exp_good_pkts  + exp_ovfl_pkts;
    exp_tot_bytes = exp_good_bytes + exp_ovfl_bytes;


    // check ingress and egress probe counts
    if (ovfl_mode==1)
       check_probe (.base_addr(in_port_base_addr), .exp_pkt_cnt(exp_good_pkts), .exp_byte_cnt(exp_good_bytes));
    else
       check_probe (.base_addr(in_port_base_addr), .exp_pkt_cnt(exp_tot_pkts),  .exp_byte_cnt(exp_tot_bytes));

    check_probe (.base_addr(out_port_base_addr), .exp_pkt_cnt(exp_good_pkts), .exp_byte_cnt(exp_good_bytes));


    // check ingress and egress ovfl counts
    if ( (in_port != HOST_PORT0) && (in_port != HOST_PORT1) ) begin  // no ovfl counters for these ingress ports.
       in_port_base_addr = in_port_base_addr + 'h400;
       if (ovfl_mode==1)
          check_probe (.base_addr(in_port_base_addr), .exp_pkt_cnt(exp_ovfl_pkts), .exp_byte_cnt(exp_ovfl_bytes));
       else if (ovfl_mode==0)
          check_probe (.base_addr(in_port_base_addr), .exp_pkt_cnt(0), .exp_byte_cnt(0));
    end

    out_port_base_addr = out_port_base_addr + 'h400;
    if (ovfl_mode==1)
       check_probe (.base_addr(out_port_base_addr), .exp_pkt_cnt(0), .exp_byte_cnt(0));
    else if (ovfl_mode==0)
       check_probe (.base_addr(out_port_base_addr), .exp_pkt_cnt(exp_ovfl_pkts), .exp_byte_cnt(exp_ovfl_bytes));
       
endtask;


task check_probe (input cntr_addr_t base_addr, input logic [63:0] exp_pkt_cnt, exp_byte_cnt);
    logic [63:0] rd_data;

    env.reg_agent.read_reg( base_addr + 'h0, rd_data[63:32] );  // pkt_count_upper
    env.reg_agent.read_reg( base_addr + 'h4, rd_data[31:0]  );  // pkt_count_lower
   `INFO($sformatf("%s pkt count: %0d", base_addr.encoded.name(), rd_data));
   `FAIL_UNLESS( rd_data == exp_pkt_cnt );

    env.reg_agent.read_reg( base_addr + 'h8, rd_data[63:32] );  // byte_count_upper
    env.reg_agent.read_reg( base_addr + 'hc, rd_data[31:0]  );  // byte_count_lower
   `INFO($sformatf("%s byte count: %0d", base_addr.encoded.name(), rd_data));
   `FAIL_UNLESS( rd_data == exp_byte_cnt );

endtask;


task check_and_clear_err_probes ( input port_t in_port, input logic [63:0] exp_err_pkts, exp_err_bytes );
    cntr_addr_t in_port_err_addr;

    // establish addr for ingress err counts
    case (in_port)
       CMAC_PORT0 : in_port_err_addr = DROPS_ERR_FROM_CMAC_PORT0; // 'h8800;
       CMAC_PORT1 : in_port_err_addr = DROPS_ERR_FROM_CMAC_PORT1; // 'h9400;
       default    : in_port_err_addr = 'hxxxx;
    endcase

    check_probe (.base_addr(in_port_err_addr), .exp_pkt_cnt(exp_err_pkts), .exp_byte_cnt(exp_err_bytes));

    env.reg_agent.write_reg( in_port_err_addr + 'h10, 'h2 ); // CLR_ON_WR_EVT

endtask;


task latch_probe_counters;
    env.probe_from_cmac_0_reg_blk_agent.write_probe_control  ( 'h1 );
    env.probe_from_cmac_1_reg_blk_agent.write_probe_control  ( 'h1 );
    env.probe_from_host_0_reg_blk_agent.write_probe_control  ( 'h1 );
    env.probe_from_host_1_reg_blk_agent.write_probe_control  ( 'h1 );

    env.probe_core_to_app0_reg_blk_agent.write_probe_control ( 'h1 );
    env.probe_core_to_app1_reg_blk_agent.write_probe_control ( 'h1 );
    env.probe_app0_to_core_reg_blk_agent.write_probe_control ( 'h1 );
    env.probe_app1_to_core_reg_blk_agent.write_probe_control ( 'h1 );

    env.probe_to_cmac_0_reg_blk_agent.write_probe_control    ( 'h1 );
    env.probe_to_cmac_1_reg_blk_agent.write_probe_control    ( 'h1 );
    env.probe_to_host_0_reg_blk_agent.write_probe_control    ( 'h1 );
    env.probe_to_host_1_reg_blk_agent.write_probe_control    ( 'h1 );

    env.probe_to_bypass_reg_blk_agent.write_probe_control    ( 'h1 );
endtask;


task latch_and_clear_probe_counters;
    env.probe_from_cmac_0_reg_blk_agent.write_probe_control  ( 'h3 );
    env.probe_from_cmac_1_reg_blk_agent.write_probe_control  ( 'h3 );
    env.probe_from_host_0_reg_blk_agent.write_probe_control  ( 'h3 );
    env.probe_from_host_1_reg_blk_agent.write_probe_control  ( 'h3 );

    env.probe_core_to_app0_reg_blk_agent.write_probe_control ( 'h3 );
    env.probe_core_to_app1_reg_blk_agent.write_probe_control ( 'h3 );
    env.probe_app0_to_core_reg_blk_agent.write_probe_control ( 'h3 );
    env.probe_app1_to_core_reg_blk_agent.write_probe_control ( 'h3 );

    env.probe_to_cmac_0_reg_blk_agent.write_probe_control    ( 'h3 );
    env.probe_to_cmac_1_reg_blk_agent.write_probe_control    ( 'h3 );
    env.probe_to_host_0_reg_blk_agent.write_probe_control    ( 'h3 );
    env.probe_to_host_1_reg_blk_agent.write_probe_control    ( 'h3 );

    env.probe_to_bypass_reg_blk_agent.write_probe_control    ( 'h3 );
endtask;


task clear_and_check_probe_counters;
    env.probe_from_cmac_0_reg_blk_agent.write_probe_control  ( 'h2 );
    env.probe_from_cmac_1_reg_blk_agent.write_probe_control  ( 'h2 );
    env.probe_from_host_0_reg_blk_agent.write_probe_control  ( 'h2 );
    env.probe_from_host_1_reg_blk_agent.write_probe_control  ( 'h2 );

    env.probe_core_to_app0_reg_blk_agent.write_probe_control ( 'h2 );
    env.probe_core_to_app1_reg_blk_agent.write_probe_control ( 'h2 );
    env.probe_app0_to_core_reg_blk_agent.write_probe_control ( 'h2 );
    env.probe_app1_to_core_reg_blk_agent.write_probe_control ( 'h2 );

    env.probe_to_cmac_0_reg_blk_agent.write_probe_control    ( 'h2 );
    env.probe_to_cmac_1_reg_blk_agent.write_probe_control    ( 'h2 );
    env.probe_to_host_0_reg_blk_agent.write_probe_control    ( 'h2 );
    env.probe_to_host_1_reg_blk_agent.write_probe_control    ( 'h2 );

    env.probe_to_bypass_reg_blk_agent.write_probe_control    ( 'h2 );

    check_cleared_probe_counters;
endtask;


task check_cleared_probe_counters;
    check_probe ( .base_addr(PROBE_FROM_CMAC_PORT0), .exp_pkt_cnt(0), .exp_byte_cnt(0) );
    check_probe ( .base_addr(PROBE_FROM_CMAC_PORT1), .exp_pkt_cnt(0), .exp_byte_cnt(0) );
    check_probe ( .base_addr(PROBE_FROM_HOST_PORT0), .exp_pkt_cnt(0), .exp_byte_cnt(0) );
    check_probe ( .base_addr(PROBE_FROM_HOST_PORT1), .exp_pkt_cnt(0), .exp_byte_cnt(0) );

    check_probe ( .base_addr(PROBE_CORE_TO_APP0),    .exp_pkt_cnt(0), .exp_byte_cnt(0) );
    check_probe ( .base_addr(PROBE_CORE_TO_APP1),    .exp_pkt_cnt(0), .exp_byte_cnt(0) );
    check_probe ( .base_addr(PROBE_APP0_TO_CORE),    .exp_pkt_cnt(0), .exp_byte_cnt(0) );
    check_probe ( .base_addr(PROBE_APP1_TO_CORE),    .exp_pkt_cnt(0), .exp_byte_cnt(0) );

    check_probe ( .base_addr(PROBE_TO_CMAC_PORT0),   .exp_pkt_cnt(0), .exp_byte_cnt(0) );
    check_probe ( .base_addr(PROBE_TO_CMAC_PORT1),   .exp_pkt_cnt(0), .exp_byte_cnt(0) );
    check_probe ( .base_addr(PROBE_TO_HOST_PORT0),   .exp_pkt_cnt(0), .exp_byte_cnt(0) );
    check_probe ( .base_addr(PROBE_TO_HOST_PORT1),   .exp_pkt_cnt(0), .exp_byte_cnt(0) );

    check_probe ( .base_addr(PROBE_TO_BYPASS),       .exp_pkt_cnt(0), .exp_byte_cnt(0) );
endtask;


task check_probe_control_defaults;
    logic [31:0] rd_data;
    bit          rd_fail = 0;

    env.probe_from_cmac_0_reg_blk_agent.read_probe_control  ( rd_data ); rd_fail = rd_fail || (rd_data != 0);
    env.probe_from_cmac_1_reg_blk_agent.read_probe_control  ( rd_data ); rd_fail = rd_fail || (rd_data != 0);
    env.probe_from_host_0_reg_blk_agent.read_probe_control  ( rd_data ); rd_fail = rd_fail || (rd_data != 0);
    env.probe_from_host_1_reg_blk_agent.read_probe_control  ( rd_data ); rd_fail = rd_fail || (rd_data != 0);

    env.probe_core_to_app0_reg_blk_agent.read_probe_control ( rd_data ); rd_fail = rd_fail || (rd_data != 0);
    env.probe_core_to_app1_reg_blk_agent.read_probe_control ( rd_data ); rd_fail = rd_fail || (rd_data != 0);
    env.probe_app0_to_core_reg_blk_agent.read_probe_control ( rd_data ); rd_fail = rd_fail || (rd_data != 0);
    env.probe_app1_to_core_reg_blk_agent.read_probe_control ( rd_data ); rd_fail = rd_fail || (rd_data != 0);

    env.probe_to_cmac_0_reg_blk_agent.read_probe_control    ( rd_data ); rd_fail = rd_fail || (rd_data != 0);
    env.probe_to_cmac_1_reg_blk_agent.read_probe_control    ( rd_data ); rd_fail = rd_fail || (rd_data != 0);
    env.probe_to_host_0_reg_blk_agent.read_probe_control    ( rd_data ); rd_fail = rd_fail || (rd_data != 0);
    env.probe_to_host_1_reg_blk_agent.read_probe_control    ( rd_data ); rd_fail = rd_fail || (rd_data != 0);

    env.probe_to_bypass_reg_blk_agent.read_probe_control    ( rd_data ); rd_fail = rd_fail || (rd_data != 0);
   `FAIL_UNLESS( rd_fail == 0 );

endtask;
