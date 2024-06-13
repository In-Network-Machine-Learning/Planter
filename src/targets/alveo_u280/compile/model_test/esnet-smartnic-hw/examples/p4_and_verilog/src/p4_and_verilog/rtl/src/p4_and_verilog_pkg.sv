package p4_and_verilog_pkg;
    // --------------------------------------------------------------
    // Imports
    // --------------------------------------------------------------
    import sdnet_0_pkg::*;

    // --------------------------------------------------------------
    // Parameters & Typedefs
    // --------------------------------------------------------------

    // Timestamp
    localparam int TIMESTAMP_WID = 64;

    typedef logic [TIMESTAMP_WID-1:0] timestamp_t;

    // User metadata
    typedef USER_META_DATA_T user_metadata_t;

endpackage : p4_and_verilog_pkg
