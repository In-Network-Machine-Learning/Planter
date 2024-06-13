`include "svunit_defines.svh"

import tb_pkg::*;

//===================================
// (Failsafe) timeout
//===================================
`define SVUNIT_TIMEOUT 200us

module p4_app_passthrough_test_unit_test;
    // Testcase name
    string name = "p4_app_passthrough_ut";

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
    localparam int HDR_LENGTH = 0;

    tb_pkg::tb_env env;

    // VitisNetP4 table agent
    vitisnetp4_verif_pkg::vitisnetp4_agent vitisnetp4_agent;

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

       `SVTEST( test_default )
             // Configure igr_sw CMAC_0 tdest to APP_1 (igr_sw output port APP_1 is connected to p4_app passthrough path).
             env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_IGR_SW_TDEST[0], 2'h1 );

             // Configure egr_sw output port APP_1 tdest remapping to redirect CMAC_1 pkts to CMAC_0. 
             env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_APP_1_TDEST_REMAP[1], 2'h0 );

             run_pkt_test ( .testdir( "test-default" ), .init_timestamp(1) );
       `SVTEST_END

        // `include "../../../p4/sim/run_pkt_test_incl.svh"

    `SVUNIT_TESTS_END

endmodule
