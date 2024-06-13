#include <stdint.h>
#include <stdbool.h>

extern bool snp4_io_reg_write(uintptr_t snp4_base_addr, uintptr_t offset, uint32_t data);
extern bool snp4_io_reg_read(uintptr_t snp4_base_addr, uintptr_t offset, uint32_t * data);

