`include "svunit_defines.svh"

//===================================
// (Failsafe) timeout
//===================================
`define SVUNIT_TIMEOUT 200us

module p2p_smartnic_322mhz_datapath_unit_test;

    // Testcase name
    string name = "p2p_smartnic_322mhz_datapath_ut";

    // SVUnit base testcase
    svunit_pkg::svunit_testcase svunit_ut;

    //===================================
    // DUT + testbench
    //===================================
    // This test suite references the common smartnic_322mhz
    // testbench top level. The 'tb' module is
    // loaded into the tb_glbl scope, so is available
    // at tb_glbl.tb.
    //
    // Interaction with the testbench is expected to occur
    // via the testbench environment class (tb_env). A
    // reference to the testbench environment is provided
    // here for convenience.
    tb_pkg::tb_env env;

    //===================================
    // Import common testcase tasks
    //=================================== 
    `include "../../../../../src/smartnic_322mhz/tests/common/tasks.svh"       

    //===================================
    // Build
    //===================================
    function void build();
        svunit_ut = new(name);

        // Build testbench
        tb.build();

        // Retrieve reference to testbench environment class
        env = tb.env;

    endfunction

    //===================================
    // Local test variables
    //===================================

   
    //===================================
    // Setup for running the Unit Tests
    //===================================
    task setup();
        svunit_ut.setup();

        for (int i=0; i<NUM_PORTS; i++) env.axis_driver[i].set_min_gap(0);

        reset(); // Issue reset (both datapath and management domains)

        // initialize switch configuration registers.
        init_sw_config_regs;

        switch_config = 0; env.smartnic_322mhz_reg_blk_agent.write_switch_config(switch_config);

        // default variable configuration
         in_pcap[0] = "../../../../../src/smartnic_322mhz/tests/common/pcap/20xrandom_pkts.pcap";
        out_pcap[0] = "../../../../../src/smartnic_322mhz/tests/common/pcap/20xrandom_pkts.pcap";
         in_pcap[1] = "../../../../../src/smartnic_322mhz/tests/common/pcap/30xrandom_pkts.pcap";
        out_pcap[1] = "../../../../../src/smartnic_322mhz/tests/common/pcap/30xrandom_pkts.pcap";
         in_pcap[2] = "../../../../../src/smartnic_322mhz/tests/common/pcap/40xrandom_pkts.pcap";
        out_pcap[2] = "../../../../../src/smartnic_322mhz/tests/common/pcap/40xrandom_pkts.pcap";
         in_pcap[3] = "../../../../../src/smartnic_322mhz/tests/common/pcap/50xrandom_pkts.pcap";
        out_pcap[3] = "../../../../../src/smartnic_322mhz/tests/common/pcap/50xrandom_pkts.pcap";

        out_port_map = {2'h3, 2'h2, 2'h1, 2'h0};
        exp_pkt_cnt  = {0, 0, 0, 0};  // if exp_pkt_cnt field is set 0, value is determined from pcap file.

        // Configure bypass path to send all traffic to port 3 (i.e. HOST_1, not CMAC_0).
        env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_BYPASS_TDEST[0], 2'h3 );
        env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_BYPASS_TDEST[1], 2'h3 );
        env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_BYPASS_TDEST[2], 2'h3 );
        env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_BYPASS_TDEST[3], 2'h3 );

        // Configure tdest for CMAC_0 to APP_0 i.e. ingress switch port 0.
        env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_IGR_SW_TDEST[0], 2'h0 );

        `INFO("Waiting to initialize axis fifos...");
        for (integer i = 0; i < 100 ; i=i+1 ) begin
          @(posedge tb.clk);
        end

    endtask


    //===================================
    // Here we deconstruct anything we
    // need after running the Unit Tests
    //===================================
    task teardown();
        `INFO("Waiting to end testcase...");
        for (integer i = 0; i < 100 ; i=i+1 ) @(posedge tb.clk);
        `INFO("Ending testcase!");

        svunit_ut.teardown();

    endtask

    //=======================================================================
    // TESTS
    //=======================================================================

    //===================================
    // All tests are defined between the
    // SVUNIT_TESTS_BEGIN/END macros
    //
    // Each individual test must be
    // defined between `SVTEST(_NAME_)
    // `SVTEST_END
    //
    // i.e.
    //   `SVTEST(mytest)
    //     <test code>
    //   `SVTEST_END
    //===================================

    `SVUNIT_TESTS_BEGIN

      `SVTEST(basic_sanity)
         // Configure igr_sw tdest registers (CMAC_0 -> APP_0, CMAC_1 -> APP_1).
         env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_IGR_SW_TDEST[0], 2'h0 );
         env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_IGR_SW_TDEST[1], 2'h1 );

         for (int i=0; i<NUM_PORTS; i++) begin
            out_port_map = {out_port_map[2:0], out_port_map[3]};

            // Configure egr_sw tdest (output port) registers (APP_0 CMAC_0 -> out_port_map[0], APP_1 CMAC_1 -> out_port_map[1]).
            env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_APP_0_TDEST_REMAP[0], out_port_map[0] );
            env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_APP_1_TDEST_REMAP[1], out_port_map[1] );

            fork
               run_pkt_stream ( .in_port(0), .out_port(out_port_map[0]), .in_pcap(in_pcap[0]), .out_pcap(out_pcap[0]),
                                .tx_pkt_cnt(tx_pkt_cnt[0]), .tx_byte_cnt(tx_byte_cnt[0]),
                                .rx_pkt_cnt(rx_pkt_cnt[0]), .rx_byte_cnt(rx_byte_cnt[0]),
                                .exp_pkt_cnt(exp_pkt_cnt[0]),
                                .tpause(0), .twait(0) );

               run_pkt_stream ( .in_port(1), .out_port(out_port_map[1]), .in_pcap(in_pcap[1]), .out_pcap(out_pcap[1]),
                                .tx_pkt_cnt(tx_pkt_cnt[1]), .tx_byte_cnt(tx_byte_cnt[1]),
                                .rx_pkt_cnt(rx_pkt_cnt[1]), .rx_byte_cnt(rx_byte_cnt[1]),
                                .exp_pkt_cnt(exp_pkt_cnt[1]),
                                .tpause(0), .twait(0) );
            join

            check_probe (.base_addr(PROBE_APP0_TO_CORE), .exp_pkt_cnt(tx_pkt_cnt[0]), .exp_byte_cnt(tx_byte_cnt[0]));
            check_probe (.base_addr(PROBE_CORE_TO_APP0), .exp_pkt_cnt(tx_pkt_cnt[0]), .exp_byte_cnt(tx_byte_cnt[0]));

            check_probe (.base_addr(PROBE_APP1_TO_CORE), .exp_pkt_cnt(tx_pkt_cnt[1]), .exp_byte_cnt(tx_byte_cnt[1]));
            check_probe (.base_addr(PROBE_CORE_TO_APP1), .exp_pkt_cnt(tx_pkt_cnt[1]), .exp_byte_cnt(tx_byte_cnt[1]));

            check_stream_test_probes;
            clear_and_check_probe_counters;
         end

      `SVTEST_END


      `SVTEST(app0_pkt_loop_drops)
         switch_config.drop_pkt_loop = 1; env.smartnic_322mhz_reg_blk_agent.write_switch_config(switch_config);

         fork
            run_pkt_stream ( .in_port(0), .out_port(out_port_map[0]), .in_pcap(in_pcap[0]), .out_pcap(out_pcap[0]),
                             .tx_pkt_cnt(tx_pkt_cnt[0]), .tx_byte_cnt(tx_byte_cnt[0]),
                             .rx_pkt_cnt(rx_pkt_cnt[0]), .rx_byte_cnt(rx_byte_cnt[0]),
                             .exp_pkt_cnt(exp_pkt_cnt[0]),
                             .tpause(0), .twait(0) );

            begin
               #10us
               check_probe (.base_addr(PROBE_CORE_TO_APP0), .exp_pkt_cnt(tx_pkt_cnt[0]), .exp_byte_cnt(tx_byte_cnt[0]));
               check_probe (.base_addr(PROBE_APP0_TO_CORE), .exp_pkt_cnt(0), .exp_byte_cnt(0));
               check_probe (.base_addr(DROPS_FROM_APP0), .exp_pkt_cnt(tx_pkt_cnt[0]), .exp_byte_cnt(tx_byte_cnt[0]));
               check_stream_probes (.in_port(0), .out_port(out_port_map[0]),
                                    .exp_good_pkts(0), .exp_good_bytes(0), .exp_ovfl_pkts(tx_pkt_cnt[0]), .exp_ovfl_bytes(tx_byte_cnt[0]),
                                    .ovfl_mode(2) );
            end
         join_any

      `SVTEST_END

    `SVUNIT_TESTS_END

endmodule
