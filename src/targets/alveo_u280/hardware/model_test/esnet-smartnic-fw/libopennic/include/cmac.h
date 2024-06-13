#include "cmac_block.h"
#include <stdbool.h>

extern bool cmac_enable(volatile struct cmac_block * cmac);
extern bool cmac_disable(volatile struct cmac_block * cmac);
