// *************************************************************************
//
// Copyright 2020 Xilinx, Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
// *************************************************************************
localparam C_NUM_USER_BLOCK = 1;

// Make sure for all the unused reset pair, corresponding bits in
// "mod_rst_done" are tied to 0
assign mod_rst_done[7:C_NUM_USER_BLOCK] = {(8-C_NUM_USER_BLOCK){1'b1}};

smartnic_322mhz #(
  .NUM_CMAC (NUM_CMAC_PORT),
  .MAX_PKT_LEN (MAX_PKT_LEN)
) smartnic_322mhz (
  .s_axil_awvalid                  (s_axil_awvalid),
  .s_axil_awaddr                   (s_axil_awaddr),
  .s_axil_awready                  (s_axil_awready),
  .s_axil_wvalid                   (s_axil_wvalid),
  .s_axil_wdata                    (s_axil_wdata),
  .s_axil_wready                   (s_axil_wready),
  .s_axil_bvalid                   (s_axil_bvalid),
  .s_axil_bresp                    (s_axil_bresp),
  .s_axil_bready                   (s_axil_bready),
  .s_axil_arvalid                  (s_axil_arvalid),
  .s_axil_araddr                   (s_axil_araddr),
  .s_axil_arready                  (s_axil_arready),
  .s_axil_rvalid                   (s_axil_rvalid),
  .s_axil_rdata                    (s_axil_rdata),
  .s_axil_rresp                    (s_axil_rresp),
  .s_axil_rready                   (s_axil_rready),

  .s_axis_adpt_tx_322mhz_tvalid    (s_axis_adap_tx_322mhz_tvalid),
  .s_axis_adpt_tx_322mhz_tdata     (s_axis_adap_tx_322mhz_tdata),
  .s_axis_adpt_tx_322mhz_tkeep     (s_axis_adap_tx_322mhz_tkeep),
  .s_axis_adpt_tx_322mhz_tlast     (s_axis_adap_tx_322mhz_tlast),
  .s_axis_adpt_tx_322mhz_tdest     ('0),
  .s_axis_adpt_tx_322mhz_tuser_err (s_axis_adap_tx_322mhz_tuser_err),
  .s_axis_adpt_tx_322mhz_tready    (s_axis_adap_tx_322mhz_tready),

  .m_axis_adpt_rx_322mhz_tvalid    (m_axis_adap_rx_322mhz_tvalid),
  .m_axis_adpt_rx_322mhz_tdata     (m_axis_adap_rx_322mhz_tdata),
  .m_axis_adpt_rx_322mhz_tkeep     (m_axis_adap_rx_322mhz_tkeep),
  .m_axis_adpt_rx_322mhz_tlast     (m_axis_adap_rx_322mhz_tlast),
  .m_axis_adpt_rx_322mhz_tdest     (),
  .m_axis_adpt_rx_322mhz_tuser_err (m_axis_adap_rx_322mhz_tuser_err),
  .m_axis_adpt_rx_322mhz_tuser_rss_enable  (m_axis_adap_rx_322mhz_tuser_rss_hash_valid),
  .m_axis_adpt_rx_322mhz_tuser_rss_entropy (m_axis_adap_rx_322mhz_tuser_rss_hash),
  .m_axis_adpt_rx_322mhz_tready    (m_axis_adap_rx_322mhz_tready),

  .m_axis_cmac_tx_322mhz_tvalid           (m_axis_cmac_tx_tvalid),
  .m_axis_cmac_tx_322mhz_tdata            (m_axis_cmac_tx_tdata),
  .m_axis_cmac_tx_322mhz_tkeep            (m_axis_cmac_tx_tkeep),
  .m_axis_cmac_tx_322mhz_tlast            (m_axis_cmac_tx_tlast),
  .m_axis_cmac_tx_322mhz_tdest            (),
  .m_axis_cmac_tx_322mhz_tuser_err        (m_axis_cmac_tx_tuser_err),
  .m_axis_cmac_tx_322mhz_tready           (m_axis_cmac_tx_tready),

  .s_axis_cmac_rx_322mhz_tvalid           (s_axis_cmac_rx_tvalid),
  .s_axis_cmac_rx_322mhz_tdata            (s_axis_cmac_rx_tdata),
  .s_axis_cmac_rx_322mhz_tkeep            (s_axis_cmac_rx_tkeep),
  .s_axis_cmac_rx_322mhz_tlast            (s_axis_cmac_rx_tlast),
  .s_axis_cmac_rx_322mhz_tdest            ('0),
  .s_axis_cmac_rx_322mhz_tuser_err        (s_axis_cmac_rx_tuser_err),
  .s_axis_cmac_rx_322mhz_tready           (),

  .mod_rstn                        (mod_rstn[0]),
  .mod_rst_done                    (mod_rst_done[0]),

  .axil_aclk                       (axil_aclk),
  .cmac_clk                        (cmac_clk)
);
