class timestamp_agent #(
    parameter type TIMESTAMP_T = bit[63:0]
);

    //===================================
    // Properties
    //===================================
    rand TIMESTAMP_T _timestamp_init;

    //===================================
    // Interfaces
    //===================================
    virtual timestamp_if timestamp_vif;

    //===================================
    // Methods
    //===================================

    // Constructor
    function new();
        randomize();
    endfunction

    task reset();
        timestamp_vif.update(_timestamp_init);
    endtask

    task set_static(input TIMESTAMP_T timestamp);
        timestamp_vif.freeze_at(timestamp);
    endtask

    task set(input TIMESTAMP_T timestamp);
        timestamp_vif.update(timestamp);
    endtask

    task freeze();
        timestamp_vif.freeze();
    endtask

    task unfreeze();
        timestamp_vif.unfreeze();
    endtask

endclass : timestamp_agent
