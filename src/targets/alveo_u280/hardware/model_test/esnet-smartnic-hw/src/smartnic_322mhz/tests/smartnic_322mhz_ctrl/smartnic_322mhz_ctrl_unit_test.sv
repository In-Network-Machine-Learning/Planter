`include "svunit_defines.svh"

//===================================
// (Failsafe) timeout
//===================================
`define SVUNIT_TIMEOUT 500us

module smartnic_322mhz_ctrl_unit_test;

    string name = "smartnic_322mhz_ctrl_ut";
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

    endfunction

    //===================================
    // Setup for running the Unit Tests
    //===================================
    task setup();
        svunit_ut.setup();

        // Issue reset (both datapath and management domains)
        reset();

    endtask


    //===================================
    // Here we deconstruct anything we
    // need after running the Unit Tests
    //===================================
    task teardown();
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

    // Test read access to smartnic_322mhz.status register
    // (currently a read-only register containing 32'hC0BEBEEF)
    `SVTEST(read_smartnic_322mhz_status)
        logic [31:0] exp_data = 32'hc0bebeef;
        logic [31:0] got_data;

        // Read smartnic_322mhz status register
        env.smartnic_322mhz_reg_blk_agent.read_status(got_data);
        `FAIL_UNLESS(got_data == exp_data);
    `SVTEST_END

    // Test flow_control access.
    `SVTEST(flow_control)
        logic [3:0][7:0] exp_data;
        logic [3:0][7:0] got_data;

        // check default values.
        exp_data = smartnic_322mhz_reg_pkg::INIT_EGR_FC_THRESH;
        env.smartnic_322mhz_reg_blk_agent.read_egr_fc_thresh(0, got_data); `FAIL_UNLESS(got_data == exp_data);

        exp_data = smartnic_322mhz_reg_pkg::INIT_EGR_FC_THRESH;
        env.smartnic_322mhz_reg_blk_agent.read_egr_fc_thresh(1, got_data); `FAIL_UNLESS(got_data == exp_data);

        exp_data = smartnic_322mhz_reg_pkg::INIT_EGR_FC_THRESH;
        env.smartnic_322mhz_reg_blk_agent.read_egr_fc_thresh(2, got_data); `FAIL_UNLESS(got_data == exp_data);

        exp_data = smartnic_322mhz_reg_pkg::INIT_EGR_FC_THRESH;
        env.smartnic_322mhz_reg_blk_agent.read_egr_fc_thresh(3, got_data); `FAIL_UNLESS(got_data == exp_data);

        // check r/w access.
        exp_data = 32'h1111_1111; env.smartnic_322mhz_reg_blk_agent.write_egr_fc_thresh(0, exp_data);
        env.smartnic_322mhz_reg_blk_agent.read_egr_fc_thresh(0, got_data); `FAIL_UNLESS(got_data == exp_data);

        exp_data = 32'h2222_2222; env.smartnic_322mhz_reg_blk_agent.write_egr_fc_thresh(1, exp_data);
        env.smartnic_322mhz_reg_blk_agent.read_egr_fc_thresh(1, got_data); `FAIL_UNLESS(got_data == exp_data);

        exp_data = 32'h3333_3333; env.smartnic_322mhz_reg_blk_agent.write_egr_fc_thresh(2, exp_data);
        env.smartnic_322mhz_reg_blk_agent.read_egr_fc_thresh(2, got_data); `FAIL_UNLESS(got_data == exp_data);

        exp_data = 32'h4444_4444; env.smartnic_322mhz_reg_blk_agent.write_egr_fc_thresh(3, exp_data);
        env.smartnic_322mhz_reg_blk_agent.read_egr_fc_thresh(3, got_data); `FAIL_UNLESS(got_data == exp_data);

    `SVTEST_END

    // Test endian check component
    // Write packed value and compare against values unpacked to byte monitors
    `SVTEST(endian_check_packed_to_unpacked)
        logic [3:0][7:0] exp_data;
        logic [3:0][7:0] got_data;

        exp_data = 32'h88776655;

        env.reg_endian_check_reg_blk_agent.write_scratchpad_packed(exp_data);
        env.reg_endian_check_reg_blk_agent.read_scratchpad_packed_monitor_byte_0(got_data[0]);
        env.reg_endian_check_reg_blk_agent.read_scratchpad_packed_monitor_byte_1(got_data[1]);
        env.reg_endian_check_reg_blk_agent.read_scratchpad_packed_monitor_byte_2(got_data[2]);
        env.reg_endian_check_reg_blk_agent.read_scratchpad_packed_monitor_byte_3(got_data[3]);

        `FAIL_UNLESS(got_data == exp_data);
    `SVTEST_END

    // Test endian check component
    // Write unpacked byte values and compare against values packed to reg monitor
    `SVTEST(endian_check_unpacked_to_packed)
        logic [3:0][7:0] exp_data;
        logic [3:0][7:0] got_data;

        exp_data = 32'h88776655;

        env.reg_endian_check_reg_blk_agent.write_scratchpad_unpacked_byte_0(exp_data[0]);
        env.reg_endian_check_reg_blk_agent.write_scratchpad_unpacked_byte_1(exp_data[1]);
        env.reg_endian_check_reg_blk_agent.write_scratchpad_unpacked_byte_2(exp_data[2]);
        env.reg_endian_check_reg_blk_agent.write_scratchpad_unpacked_byte_3(exp_data[3]);
        env.reg_endian_check_reg_blk_agent.read_scratchpad_unpacked_monitor(got_data);

        `FAIL_UNLESS(got_data == exp_data);
    `SVTEST_END

    // Read HBM0 DRAM temp
    // Read temperature value from HBM DRAM (set to static value of 30 for simulation)
    `SVTEST(read_hbm_0_dram_temp)
        int got_temp;
        int exp_temp = 30;
        env.hbm_0_reg_agent.get_dram_temp(got_temp);
        `FAIL_UNLESS(got_temp === exp_temp);
    `SVTEST_END

    // Read HBM0 DRAM CATTRIP (catastrophic temperature exceeded flag)
    `SVTEST(read_hbm_0_dram_cattrip)
        bit got_cattrip;
        bit exp_cattrip = 1'b0;
        env.hbm_0_reg_agent.get_dram_cattrip(got_cattrip);
        `FAIL_UNLESS(got_cattrip === exp_cattrip);
    `SVTEST_END

    // Read HBM1 DRAM temp
    // Read temperature value from HBM DRAM (set to static value of 30 for simulation)
    `SVTEST(read_hbm_1_dram_temp)
        int got_temp;
        int exp_temp = 30;
        env.hbm_1_reg_agent.get_dram_temp(got_temp);
        `FAIL_UNLESS(got_temp === exp_temp);
    `SVTEST_END

    // Read HBM1 DRAM CATTRIP (catastrophic temperature exceeded flag)
    `SVTEST(read_hbm_1_dram_cattrip)
        bit got_cattrip;
        bit exp_cattrip = 1'b0;
        env.hbm_1_reg_agent.get_dram_cattrip(got_cattrip);
        `FAIL_UNLESS(got_cattrip === exp_cattrip);
    `SVTEST_END

    `SVUNIT_TESTS_END

endmodule
