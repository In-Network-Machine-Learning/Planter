`include "svunit_defines.svh"

import tb_pkg::*;

//===================================
// (Failsafe) timeout
//===================================
`define SVUNIT_TIMEOUT 200us

module p4_app_datapath_unit_test
#(
    parameter int HDR_LENGTH = 0
 );
    // Testcase name
    string name = $sformatf("p4_app_datapath_hdrlen_%0d_ut", HDR_LENGTH);

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

    // VitisNetP4 table agent
    vitisnetp4_verif_pkg::vitisnetp4_agent vitisnetp4_agent;

    wire [11:0] rss_entropy [2];
    assign rss_entropy[0] = tb.m_axis_adpt_rx_322mhz_tuser_rss_entropy[11:0];
    assign rss_entropy[1] = tb.m_axis_adpt_rx_322mhz_tuser_rss_entropy[23:12];

    //===================================
    // Import common testcase tasks
    //===================================
    `include "../../../../src/smartnic_322mhz/tests/common/tasks.svh"
    `include "../common/tasks.svh"

    //===================================
    // Build
    //===================================
    function void build();
        svunit_ut = new(name);

        // Build testbench
        tb.build();

        // Retrieve reference to testbench environment class
        env = tb.env;

        vitisnetp4_agent = new;

    endfunction

    //===================================
    // Local test variables
    //===================================

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

       `SVTEST(test_rss_metadata)
           port_t  src_port, dst_port;

           fork
              // --- run traffic from both HOST ports, and to both HOST ports ---
              begin
                 // relabel source traffic from src_port=HOST_0. direct traffic to dst_port=HOST_0.
                 src_port = 2'h2; dst_port = 2'h2;
                 env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_IGR_SW_TID[0], src_port );
                 env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_APP_0_TDEST_REMAP[src_port], dst_port );
                 run_pkt_test ( .testdir( "test-default" ), .init_timestamp(1), .dest_port(dst_port) );

                 // redirect traffic to dst_port=HOST_1.
                 dst_port = 2'h3;
                 env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_APP_0_TDEST_REMAP[src_port], dst_port );
                 run_pkt_test ( .testdir( "test-default" ), .init_timestamp(1), .dest_port(dst_port) );

                 // relabel source traffic from src_port=HOST_1.
                 src_port = 2'h3;
                 env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_IGR_SW_TID[0], src_port );
                 env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_APP_0_TDEST_REMAP[src_port], dst_port );
                 run_pkt_test ( .testdir( "test-default" ), .init_timestamp(1), .dest_port(dst_port) );

                 // redirect traffic to dst_port=HOST_0.
                 dst_port = 2'h2;
                 env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_APP_0_TDEST_REMAP[src_port], dst_port );
                 run_pkt_test ( .testdir( "test-default" ), .init_timestamp(1), .dest_port(dst_port) );
              end

              // --- compare rss metadata to expected on HOST_0 port ---
              while (1) @(posedge tb.axis_out_if[2].aclk) if (tb.axis_out_if[2].tvalid) begin
                 `FAIL_UNLESS( tb.m_axis_adpt_rx_322mhz_tuser_rss_enable[dst_port[0]] == 1'b1 );
                 `FAIL_UNLESS( rss_entropy[dst_port[0]] == src_port );
              end

              // --- compare rss metadata to expected on HOST_1 port ---
              while (1) @(posedge tb.axis_out_if[3].aclk) if (tb.axis_out_if[3].tvalid) begin
                 `FAIL_UNLESS( tb.m_axis_adpt_rx_322mhz_tuser_rss_enable[dst_port[0]] == 1'b1 );
                 `FAIL_UNLESS( rss_entropy[dst_port[0]] == src_port );
              end
           join_any

       `SVTEST_END

       `SVTEST(test_pkt_loopback)
           run_pkt_test ( .testdir("test-pkt-loopback"), .init_timestamp('0), .dest_port(0) );
       `SVTEST_END

       `include "../../p4/sim/run_pkt_test_incl.svh"

    `SVUNIT_TESTS_END

endmodule



// 'Boilerplate' unit test wrapper code
//  Builds unit test for a specific axi4s_split_join configuration in a way
//  that maintains SVUnit compatibility

`define P4_APP_DATAPATH_UNIT_TEST(HDR_LENGTH)\
  import svunit_pkg::svunit_testcase;\
  svunit_testcase svunit_ut;\
  p4_app_datapath_unit_test #(HDR_LENGTH) test();\
  function void build();\
    test.build();\
    svunit_ut = test.svunit_ut;\
  endfunction\
  task run();\
    test.run();\
  endtask

/*
module p4_app_datapath_hdrlen_0_unit_test;
`P4_APP_DATAPATH_UNIT_TEST(0)
endmodule

module p4_app_datapath_hdrlen_64_unit_test;
`P4_APP_DATAPATH_UNIT_TEST(64)
endmodule
*/

module p4_app_datapath_hdrlen_256_unit_test;
`P4_APP_DATAPATH_UNIT_TEST(256)
endmodule
