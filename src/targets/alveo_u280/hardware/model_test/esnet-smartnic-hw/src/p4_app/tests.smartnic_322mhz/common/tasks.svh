    //===================================
    // Setup for running the Unit Tests
    //===================================
    task setup();
        svunit_ut.setup();

        for (int i=0; i<NUM_PORTS; i++) env.axis_driver[i].set_min_gap(0);

        reset(); // Issue reset (both datapath and management domains)

        // Write hdr_length register (hdr_length = 0B to disable split-join logic).
        env.smartnic_322mhz_reg_blk_agent.write_hdr_length(HDR_LENGTH);

        // Initialize VitisNetP4 tables
        vitisnetp4_agent.init();

        // Configure bypass path to send all traffic to port 3 (i.e. HOST_1, not CMAC_0).
        env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_BYPASS_TDEST[0], 2'h3 );
        env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_BYPASS_TDEST[1], 2'h3 );
        env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_BYPASS_TDEST[2], 2'h3 );
        env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_BYPASS_TDEST[3], 2'h3 );

        // Configure tdest for CMAC_0 to APP_0 i.e. ingress switch port 0 is connected to sdnet block. 
        env.reg_agent.write_reg( smartnic_322mhz_reg_pkg::OFFSET_IGR_SW_TDEST[0], 2'h0 );

        `INFO("Waiting to initialize axis fifos...");
        for (integer i = 0; i < 100 ; i=i+1 ) begin
          @(posedge tb.clk);
        end

    endtask


    //=======================================
    // Teardown from running the Unit Tests
    //=======================================
    task teardown();
        `INFO("Waiting to end testcase...");
        for (integer i = 0; i < 100 ; i=i+1 ) @(posedge tb.clk);
        `INFO("Ending testcase!");

        svunit_ut.teardown();

        // Clean up SDNet tables
        vitisnetp4_agent.cleanup();

    endtask


    //=======================================================================
    // Packet test sequence
    //=======================================================================
     task run_pkt_test (
        input string testdir, input logic[63:0] init_timestamp=0, input port_t dest_port=0, input VERBOSE=1 );
	
        string filename;

        // variabes for reading expected pcap data
        byte                      exp_data[$][$];
        pcap_pkg::pcap_hdr_t      exp_pcap_hdr;
        pcap_pkg::pcaprec_hdr_t   exp_pcap_record_hdr[$];

        // variables for sending packet data
        automatic logic [63:0] timestamp = init_timestamp;
        automatic int          num_pkts  = 0;
        automatic int          start_idx = 0;

        // variables for receiving (monitoring) packet data
        automatic int rx_pkt_cnt = 0;
        automatic bit rx_done = 0;
        byte          rx_data[$];
        port_t        id;
        port_t        dest;
        bit           user;

        debug_msg($sformatf("Write initial timestamp value: %0x", timestamp), VERBOSE);
        env.ts_agent.set_static(timestamp);

        debug_msg("Start writing VitisNetP4 tables...", VERBOSE);
        filename = {"../../../p4/sim/", testdir, "/runsim.txt"};
        vitisnetp4_agent.table_init_from_file(filename);
        debug_msg("Done writing VitisNetP4 tables...", VERBOSE);

        debug_msg("Reading expected pcap file...", VERBOSE);
        filename = {"../../../p4/sim/", testdir, "/packets_out.pcap"};
        pcap_pkg::read_pcap(filename, exp_pcap_hdr, exp_pcap_record_hdr, exp_data);

        debug_msg("Starting simulation...", VERBOSE);
         filename = {"../../../p4/sim/", testdir, "/packets_in.pcap"};
         rx_pkt_cnt = 0;
         fork
             begin
                 // Send packets
                 send_pcap(filename, num_pkts, start_idx);  // sends from port 0 (CMAC_0) by default.
             end
             begin
                 // If init_timestamp=1, increment timestamp after each tx packet (puts packet # in timestamp field)
                 while ( (init_timestamp == 1) && !rx_done ) begin
                    @(posedge tb.axis_in_if[0].tlast or posedge rx_done) begin
                       if (tb.axis_in_if[0].tlast) begin timestamp++; env.ts_agent.set_static(timestamp); end
                    end
                 end
             end
             begin
                 time t = $time;
                 // Monitor output packets
                 while (rx_pkt_cnt < exp_pcap_record_hdr.size() || ($time < t + 5us)) begin
                     fork
                         begin
                             // Always monitor for some minumum period, even if no receive packets are expected
                             #5us;
                         end
                         begin
                             // Monitor received packets on port 0 (CMAC_0).
                             env.axis_monitor[dest_port].receive_raw(.data(rx_data), .id(id), .dest(dest), .user(user), .tpause(0));
                             rx_pkt_cnt++;
                             debug_msg( $sformatf( "      Receiving packet # %0d (of %0d)...",
                                                  rx_pkt_cnt, exp_pcap_record_hdr.size()), VERBOSE );
                             debug_msg("      Comparing rx_pkt to exp_pkt...", VERBOSE);
                             compare_pkts(rx_data, exp_data[start_idx+rx_pkt_cnt-1]);
                            `FAIL_IF_LOG( dest != dest_port,
                                         $sformatf("FAIL!!! Output tdest mismatch. tdest=%0h (exp:%0h)", dest, dest_port) )
                         end
                     join_any
                     disable fork;
                 end
                 rx_done = 1;
             end
         join
     endtask

     task debug_msg(input string msg, input bit VERBOSE=0);
         if (VERBOSE) `INFO(msg);
     endtask
