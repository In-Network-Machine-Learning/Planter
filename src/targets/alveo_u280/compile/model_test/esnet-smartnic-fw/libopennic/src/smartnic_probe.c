#include "smartnic.h"		/* API */
#include "memory-barriers.h"	/* barrier() */

bool smartnic_probe_read_counters(volatile struct axi4s_probe_block * probe, uint64_t *packet_count, uint64_t *byte_count, bool clear)
{
  if (!probe) {
    return false;
  }

  // Latch and optionally clear internal counts after latching
  union axi4s_probe_probe_control control_latched = {
    .latch = AXI4S_PROBE_PROBE_CONTROL_LATCH_LATCH_ON_WR_EVT,
    .clear = clear ? AXI4S_PROBE_PROBE_CONTROL_CLEAR_CLEAR_ON_WR_EVT
                   : AXI4S_PROBE_PROBE_CONTROL_CLEAR_NO_CLEAR,
  };
  probe->probe_control._v = control_latched._v;
  barrier();

  // Read the counters
  if (packet_count) {
    *packet_count = ((uint64_t)probe->pkt_count_upper  << 32) | probe->pkt_count_lower;
  }
  if (byte_count) {
    *byte_count   = ((uint64_t)probe->byte_count_upper << 32) | probe->byte_count_lower;
  }
  barrier();

  // Return counters to freerun
  union axi4s_probe_probe_control control_freerun = {
    .latch = AXI4S_PROBE_PROBE_CONTROL_LATCH_LATCH_ON_CLK,
    .clear = AXI4S_PROBE_PROBE_CONTROL_CLEAR_NO_CLEAR,
  };
  probe->probe_control._v = control_freerun._v;
  barrier();

  return true;
}
