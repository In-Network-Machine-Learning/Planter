import smartnic_322mhz_pkg::*;

class tb_env extends std_verif_pkg::base;

    // Parameters
    // -- Datapath
    localparam int AXIS_DATA_WID = 512;
    localparam int AXIS_DATA_BYTE_WID = AXIS_DATA_WID/8;
    // -- Timeouts
    localparam int RESET_TIMEOUT = 1024;     // In clk cycles
    localparam int MGMT_RESET_TIMEOUT = 256; // In aclk cycles

    //===================================
    // Properties
    //===================================

    // Reset interfaces
    virtual std_reset_intf #(.ACTIVE_LOW(1)) reset_vif;
    virtual std_reset_intf #(.ACTIVE_LOW(1)) mgmt_reset_vif;

    // AXI-L management interface
    virtual axi4l_intf axil_vif;

    // SDnet AXI-L management interface
    virtual axi4l_intf axil_sdnet_vif;

    // AXI-S input interface
    virtual axi4s_intf #(.DATA_BYTE_WID(AXIS_DATA_BYTE_WID), .TID_T(port_t), .TDEST_T(port_t)) axis_in_vif;
    virtual axi4s_intf #(.DATA_BYTE_WID(AXIS_DATA_BYTE_WID), .TID_T(port_t), .TDEST_T(egr_tdest_t)) axis_out_vif;
    virtual axi4s_intf #(.DATA_BYTE_WID(AXIS_DATA_BYTE_WID), .TID_T(port_t), .TDEST_T(egr_tdest_t)) axis_to_adpt_vif;
    virtual axi4s_intf #(.DATA_BYTE_WID(AXIS_DATA_BYTE_WID), .TID_T(port_t), .TDEST_T(port_t)) axis_from_adpt_vif;

    // AXI3 interfaces to HBM
    virtual axi3_intf #(.DATA_BYTE_WID(32), .ADDR_WID(33), .ID_T(logic[5:0])) axi_to_hbm_vif [16];

    // Drivers/Monitors
    axi4s_driver #(
        .DATA_BYTE_WID (AXIS_DATA_BYTE_WID), .TID_T (port_t), .TDEST_T (port_t)
    ) axis_driver;

    axi4s_monitor #(
        .DATA_BYTE_WID (AXIS_DATA_BYTE_WID), .TID_T (port_t), .TDEST_T (egr_tdest_t)
    ) axis_monitor;

    axi4s_monitor #(
        .DATA_BYTE_WID (AXIS_DATA_BYTE_WID), .TID_T (port_t), .TDEST_T (egr_tdest_t)
    ) axis_to_adpt_monitor;

    // AXI-L agent
    axi4l_reg_agent #() reg_agent;

    // SDnet AXI-L agent
    axi4l_reg_agent #() sdnet_reg_agent;

    // Register agents
    p4_app_reg_agent p4_app_reg_agent;

    // Timestamp
    virtual timestamp_if #() timestamp_vif;

    timestamp_agent #() ts_agent;

    //===================================
    // Methods
    //===================================

    // Constructor
    function new(string name , bit bigendian = 1);
        super.new(name);
        axis_driver          = new(.BIGENDIAN(bigendian));
        axis_monitor         = new(.BIGENDIAN(bigendian));
        axis_to_adpt_monitor = new(.BIGENDIAN(bigendian));
        reg_agent            = new("axi4l_reg_agent");
        sdnet_reg_agent      = new("axi4l_reg_agent");
        p4_app_reg_agent     = new("p4_app_reg_agent", reg_agent, 'h0000);
        ts_agent             = new;
    endfunction

    function void connect();
        axis_driver.axis_vif          = axis_in_vif;
        axis_monitor.axis_vif         = axis_out_vif;
        axis_to_adpt_monitor.axis_vif = axis_to_adpt_vif;
        ts_agent.timestamp_vif        = timestamp_vif;
        reg_agent.axil_vif            = axil_vif;
        sdnet_reg_agent.axil_vif      = axil_sdnet_vif;
    endfunction

    task reset();
        reg_agent.idle();
        sdnet_reg_agent.idle();
        axis_driver.idle();
        axis_monitor.idle();
        axis_to_adpt_monitor.idle();
        reset_vif.pulse(8);
        mgmt_reset_vif.pulse(8);
        sdnet_reg_agent._wait(32);
    endtask

    task init_timestamp();
        ts_agent.reset();
    endtask

    task read(
            input  bit [31:0] addr,
            output bit [31:0] data,
            output bit error,
            output bit timeout,
            input  int TIMEOUT=128
        );
        axil_vif.read(addr, data, error, timeout, TIMEOUT);
    endtask

    task write(
            input  bit [31:0] addr,
            input  bit [31:0] data,
            output bit error,
            output bit timeout,
            input  int TIMEOUT=32
        );
        axil_vif.write(addr, data, error, timeout, TIMEOUT);
    endtask

    task wait_reset_done(
            output bit done,
            output string msg
        );
        bit reset_done;
        bit mgmt_reset_done;
        bit reset_timeout;
        bit mgmt_reset_timeout;
        fork
            begin
                reset_vif.wait_ready(
                    reset_timeout, RESET_TIMEOUT);
            end
            begin
                mgmt_reset_vif.wait_ready(
                    mgmt_reset_timeout, MGMT_RESET_TIMEOUT);
            end
        join
        reset_done = !reset_timeout;
        mgmt_reset_done = !mgmt_reset_timeout;
        done = reset_done & mgmt_reset_done;
        if (reset_done) begin
            if (mgmt_reset_done) begin
                msg = "Return from datapath and management resets completed.";
            end else begin
                msg =
                    $sformatf(
                        "Return from management reset timed out after %d mgmt_clk cycles.",
                        MGMT_RESET_TIMEOUT
                    );
            end
        end else begin
            if (mgmt_reset_done) begin
                msg =
                    $sformatf(
                        "Return from datapath reset timed out after %d clk cycles.",
                        RESET_TIMEOUT
                    );
            end else begin
                msg = "Return from datapath/management resets timed out.";
            end
        end
    endtask

    // SDnet Tasks
    task sdnet_read(
            input  bit [31:0] addr,
            output bit [31:0] data
        );
        sdnet_reg_agent.set_rd_timeout(128);
        sdnet_reg_agent.read_reg(addr, data);
    endtask

    task sdnet_write(
            input  bit [31:0] addr,
            input  bit [31:0] data
        );
        sdnet_reg_agent.set_wr_timeout(128);
        sdnet_reg_agent.write_reg(addr, data);
    endtask

endclass : tb_env
