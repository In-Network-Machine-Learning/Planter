#include <fcntl.h>		/* open */
#include <sys/mman.h>		/* mmap/munmap */
#include <unistd.h>		/* close */
#include <stdio.h>              /* snprintf */

#include "esnet_smartnic_toplevel.h" /* ESNET_SMARTNIC_BAR2_* */

volatile struct esnet_smartnic_bar2 * smartnic_map_bar2_by_pciaddr(const char *addr) {
  char dev_resource_path[80];
  snprintf(dev_resource_path, sizeof(dev_resource_path), "/sys/bus/pci/devices/%s/resource2", addr);

  int fd = open(dev_resource_path, O_RDWR | O_SYNC | O_CLOEXEC);
  if (fd < 0) {
    return (struct esnet_smartnic_bar2 *) NULL;
  }

  void * virt_addr = mmap(0, ESNET_SMARTNIC_BAR2_SIZE_BYTES, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);

  close(fd);

  if (virt_addr == MAP_FAILED) {
    return (struct esnet_smartnic_bar2 *) NULL;
  }

  return (struct esnet_smartnic_bar2 *) virt_addr;
}

void smartnic_unmap_bar2(volatile struct esnet_smartnic_bar2 * virt_addr) {
  (void) munmap((void *)virt_addr, ESNET_SMARTNIC_BAR2_SIZE_BYTES);
}
