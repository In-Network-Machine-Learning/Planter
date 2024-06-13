package smartnic_322mhz_pkg;

    // --------------------------------------------------------------
    // Imports
    // --------------------------------------------------------------

    // --------------------------------------------------------------
    // Parameters
    // --------------------------------------------------------------

    // --------------------------------------------------------------
    // Typedefs
    // --------------------------------------------------------------

    typedef enum logic [1:0] {
        CMAC_PORT0 = 2'h0,
        CMAC_PORT1 = 2'h1,
        HOST_PORT0 = 2'h2,
        HOST_PORT1 = 2'h3
    } port_encoding_t;

    typedef union packed {
        port_encoding_t encoded;
        bit [1:0]       raw;
    } port_t;

    typedef enum logic [2:0] {
        CMAC0 = 3'h0,
        CMAC1 = 3'h1,
        HOST0 = 3'h2,
        HOST1 = 3'h3,
        LOOPBACK = 3'h7
    } egr_tdest_encoding_t;

    typedef union packed {
        egr_tdest_encoding_t encoded;
        bit [2:0]       raw;
    } egr_tdest_t;

    typedef struct packed {
        logic [15:0] pid;
        logic        rss_enable;
        logic [11:0] rss_entropy;
        logic        hdr_tlast;
    } tuser_smartnic_meta_t;

endpackage : smartnic_322mhz_pkg
