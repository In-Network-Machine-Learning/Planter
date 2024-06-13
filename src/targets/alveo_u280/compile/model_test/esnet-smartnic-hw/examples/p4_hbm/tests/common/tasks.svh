//=======================================================================
// Tasks
//=======================================================================
import smartnic_322mhz_pkg::*;

// Execute block reset (dataplane + control plane)
task reset();
    automatic bit reset_done;
    automatic string msg;
    env.reset();
    env.wait_reset_done(reset_done, msg);
    `FAIL_IF_LOG((reset_done == 0), msg);
endtask


// Send packets described in PCAP file on AXI-S input interface
task send_pcap(input string pcap_filename, input int num_pkts=0, start_idx=0, twait=0, input port_t id=0, dest=0);
    env.axis_driver.send_from_pcap(pcap_filename, num_pkts, start_idx, twait, id, dest);
endtask


// Compare packets
task compare_pkts(input byte pkt1[$], pkt2[$]);
    automatic int byte_idx = 0;

    if (pkt1.size != pkt2.size()) begin
        $display("pkt1:"); pcap_pkg::print_pkt_data(pkt1);
        $display("pkt2:"); pcap_pkg::print_pkt_data(pkt2);
        `FAIL_IF_LOG(
            pkt1.size() != pkt2.size(),
            $sformatf("FAIL!!! Packet size mismatch. size1=%0d size2=%0d", pkt1.size(), pkt2.size())
        );
    end

    byte_idx = 0;
    while ( byte_idx < pkt1.size() ) begin
       if (pkt1[byte_idx] != pkt2[byte_idx]) begin
          $display("pkt1:"); pcap_pkg::print_pkt_data(pkt1);
          $display("pkt2:"); pcap_pkg::print_pkt_data(pkt2);
	  
          `FAIL_IF_LOG( pkt1[byte_idx] != pkt2[byte_idx],
                        $sformatf("FAIL!!! Packet bytes mismatch at byte_idx: 0x%0h (d:%0d)", byte_idx, byte_idx) )
       end
       byte_idx++;
    end
endtask
