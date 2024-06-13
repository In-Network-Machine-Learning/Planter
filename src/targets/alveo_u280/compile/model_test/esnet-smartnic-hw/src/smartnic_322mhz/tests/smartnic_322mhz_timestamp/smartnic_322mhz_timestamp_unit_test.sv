`include "svunit_defines.svh"

//===================================
// (Failsafe) timeout
//===================================
`define SVUNIT_TIMEOUT 500us

module smartnic_322mhz_timestamp_unit_test;

    // Testcase name
    string name = "smartnic_322mhz_timestamp_ut";

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
        `INFO("Waiting to end testcase...");
        for (integer i = 0; i < 100 ; i=i+1 ) @(posedge tb.clk);
        `INFO("Ending testcase!");

        svunit_ut.teardown();
    endtask

    //=======================================================================
    // TESTS
    //=======================================================================

    // variables for timestamp testing
    logic [63:0] rd_data;
    smartnic_322mhz_reg_pkg::reg_timestamp_incr_t   rd_incr, new_incr;

    int period_ns = 5000;
    int num_samples = 5;

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

    `SVTEST(timestamp_sanity)
        // --------------------------------------------------------------
        // validate default increment value
        env.smartnic_322mhz_reg_blk_agent.read_timestamp_incr( rd_incr );
       `INFO($sformatf("Read default timestamp increment: 0x%0h", rd_incr )); // expect 0x2e8ba3 (2.909091ns)
       `FAIL_UNLESS( rd_incr == smartnic_322mhz_reg_pkg::INIT_TIMESTAMP_INCR );

        // --------------------------------------------------------------
        // check timestamp_wr access
        env.smartnic_322mhz_reg_blk_agent.write_timestamp_wr_upper( 32'h_8765_4321 );
        env.smartnic_322mhz_reg_blk_agent.write_timestamp_wr_lower( 32'h_1234_5678 );
        env.smartnic_322mhz_reg_blk_agent.read_timestamp_wr_upper ( rd_data[63:32] );
        env.smartnic_322mhz_reg_blk_agent.read_timestamp_wr_lower ( rd_data[31:0] );
       `FAIL_UNLESS( rd_data == 64'h_8765_4321_1234_5678 );  

        // --------------------------------------------------------------
        // poll timestamp w default incr
       `INFO($sformatf("Poll %0d timestamps (each %0d ns)...", num_samples, period_ns));

        poll_timestamp (
            .init(64'd0), .increment_ns(2.909091), .period_ns(period_ns), .num_samples(num_samples));

        // --------------------------------------------------------------
        // check timestamp_incr access
        env.smartnic_322mhz_reg_blk_agent.write_timestamp_incr( 32'h_8765_4321 );
        env.smartnic_322mhz_reg_blk_agent.read_timestamp_incr( rd_incr );
       `FAIL_UNLESS( rd_incr == 32'h_8765_4321 );

   
        // --------------------------------------------------------------
       `INFO($sformatf("Adjust incr by +0.05ns.  Poll %0d timestamps (each %0d ns)...", num_samples, period_ns));

        new_incr = 32'h2_f586fce; // 2.909091ns + 0.05ns offset
        env.smartnic_322mhz_reg_blk_agent.write_timestamp_incr( new_incr );
   
        // set initial value to just below 2^32 i.e. timestamp crosses 32b word boundary.
        poll_timestamp (
            .init(64'h0000_0000_ffff_c000), .increment_ns(2.959091), .period_ns(period_ns), .num_samples(num_samples));


        // --------------------------------------------------------------
       `INFO($sformatf("Adjust incr by -0.05ns.  Poll %0d timestamps (each %0d ns)", num_samples, period_ns));

        new_incr = 32'h2_dbed634; // 2.909091ns - 0.05ns offset
        env.smartnic_322mhz_reg_blk_agent.write_timestamp_incr( new_incr );

        // set initial value to just below 2^64 so that timestamp will wrap.
        poll_timestamp (
            .init(64'hffff_ffff_ffff_c000), .increment_ns(2.859091), .period_ns(period_ns), .num_samples(num_samples));

    `SVTEST_END

    `SVUNIT_TESTS_END


    task poll_timestamp (
       input logic[63:0] init=0, input real increment_ns=2.909091, input int period_ns=5000, num_samples=5);

       real expected;
       real clk_period_ns = 2.909091;  // set clk period to 2.909091ns (343.75 MHz)
       integer guardband_ns = 5;
       logic [63:0] rd_data, prev_data;

       expected = (period_ns / clk_period_ns) * increment_ns;  // calculate expected timestamp delta

       // write and check initialization of timestamp counter 
       env.smartnic_322mhz_reg_blk_agent.write_timestamp_wr_upper( init[63:32] );
       env.smartnic_322mhz_reg_blk_agent.write_timestamp_wr_lower( init[31:0]  );

       env.smartnic_322mhz_reg_blk_agent.write_timestamp_rd_latch( 0 );

       env.smartnic_322mhz_reg_blk_agent.read_timestamp_rd_upper( rd_data[63:32] );
       env.smartnic_322mhz_reg_blk_agent.read_timestamp_rd_lower( rd_data[31:0]  );

      `INFO($sformatf("Timestamp reg: 0x%x.", rd_data) );
      `FAIL_UNLESS( rd_data > init );
      `FAIL_UNLESS( rd_data < init + 'd150 );  // check within 150ns margin, since timestamp counter is free running.

       env.smartnic_322mhz_reg_blk_agent.read_freerun_rd_upper( rd_data[63:32] );
       env.smartnic_322mhz_reg_blk_agent.read_freerun_rd_lower( rd_data[31:0]  );

      `INFO($sformatf("Freerun reg: 0x%x.", rd_data) );
      `FAIL_UNLESS( rd_data > init );
      `FAIL_UNLESS( rd_data < init + 'd150 );

       // initialize and start polling loop
       prev_data = 0;
       #(period_ns);
 
       repeat (num_samples) begin
          fork
             begin
                // latch and read timestamp.
                env.smartnic_322mhz_reg_blk_agent.write_timestamp_rd_latch( 0 );
                env.smartnic_322mhz_reg_blk_agent.read_timestamp_rd_upper( rd_data[63:32] );
                env.smartnic_322mhz_reg_blk_agent.read_timestamp_rd_lower( rd_data[31:0]  );

                // compare to expected.
                if (prev_data != 0) begin
                 `INFO($sformatf("Timestamp: 0x%x.  Delta: %0d.  Expected: %0d (+/- %0d ns guardband).", 
                                  rd_data, rd_data-prev_data, expected, guardband_ns) );
                 `FAIL_UNLESS( ( rd_data-prev_data ) < ( expected+guardband_ns ) );  // +/- guard band 
                 `FAIL_UNLESS( ( rd_data-prev_data ) > ( expected-guardband_ns ) );
                end 

                prev_data = rd_data;
             end

	     // wait for period_ns nanoseconds.
             #(period_ns);
         join
       end
    endtask;
      
endmodule
