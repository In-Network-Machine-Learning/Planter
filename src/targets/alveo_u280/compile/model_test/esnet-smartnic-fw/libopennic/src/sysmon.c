#include "sysmon.h"		/* API */

/*
 * Reference: https://www.xilinx.com/support/documentation/user_guides/ug580-ultrascale-sysmon.pdf
 */

/*
 * Power Supply Sensor (Page 41)
 *
 * Convert raw 10-bit ADC value to voltage
 */
static float adc_to_v(uint16_t adc_code) {
  return(((float)adc_code) / 1024.0f);
};

/*
 * Temperature Sensor (Page 40)
 *
 * The SYSMON contains a temperature sensor that produces a voltage output
 * proportional to the die temperature.
 *
 * Ultrascale+ FPGAs have the SYSMONE4 block
 *
 */

static float v_to_degc_sysmone4(float v, enum sysmon_flag_ref ref) {
  if (ref == SYSMON_FLAG_REF_INTERNAL) {
    return (v * 509.3140064 - 280.23087870);
  } else {
    return (v * 507.5921310 - 279.42657680);
  }
}

float sysmon_get_temp(volatile struct sysmon_block * sysmon) {
  float v = adc_to_v(sysmon->temperature.adc);

  return (v_to_degc_sysmone4(v, sysmon->flag.ref));
};
