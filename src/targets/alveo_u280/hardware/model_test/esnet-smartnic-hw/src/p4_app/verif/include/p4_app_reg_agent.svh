class p4_app_reg_agent #(
) extends p4_app_reg_blk_agent;
  
    //===================================
    // Methods
    //===================================
    // Constructor
    function new(
            input string name="p4_app_reg_agent",
            const ref reg_verif_pkg::reg_agent reg_agent,
            input int BASE_OFFSET=0
        );
        super.new(name, BASE_OFFSET);
        this.reg_agent = reg_agent;
    endfunction

    // Read status
    task get_status(output p4_app_reg_pkg::reg_status_t status);
        this.read_status(status);
    endtask

    // Check status
    task check_status(output bit fail, output string msg);
        p4_app_reg_pkg::reg_status_t exp_status = p4_app_reg_pkg::INIT_STATUS;
        p4_app_reg_pkg::reg_status_t got_status;
        this.get_status(got_status);
        if (got_status == exp_status) begin
            fail = 1'b0;
            msg = "STATUS check passed";
        end else begin
            fail = 1'b1;
            msg = $sformatf("[p4_app_reg_agent]: STATUS check failed. Exp: 0x%x, Got: 0x%x", exp_status, got_status);
        end
    endtask

endclass : p4_app_reg_agent
