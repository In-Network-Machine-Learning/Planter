#include "cmac.h"		/* API */
#include "memory-barriers.h"	/* barrier() */

bool cmac_enable(volatile struct cmac_block * cmac) {
  union cmac_conf_rx_1 conf_rx = {
    .ctl_rx_enable = 1,
  };
  cmac->conf_rx_1._v = conf_rx._v;

  union cmac_conf_tx_1 conf_tx = {
    .ctl_tx_enable = 1,
  };
  cmac->conf_tx_1._v = conf_tx._v;

  barrier();

  uint32_t tx_status;
  for (int i = 0; i < 2; i++) {
    tx_status = cmac->stat_tx_status._v;
  }

  uint32_t rx_status;
  for (int i = 0; i < 2; i++) {
    rx_status = cmac->stat_rx_status._v;
  }

  if (tx_status != 0) return false;
  if (rx_status != 3) return false;

  return true;
}

bool cmac_disable(volatile struct cmac_block * cmac) {
  union cmac_conf_rx_1 conf_rx = {
    .ctl_rx_enable = 0,
  };
  cmac->conf_rx_1._v = conf_rx._v;

  union cmac_conf_tx_1 conf_tx = {
    .ctl_tx_enable = 0,
  };
  cmac->conf_tx_1._v = conf_tx._v;

  barrier();

  return true;
}

