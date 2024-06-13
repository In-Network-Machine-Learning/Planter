# -----------------------------------------------
# Path setup
# -----------------------------------------------
APP_DIR = ..

include $(APP_DIR)/config.mk

# ----------------------------------------------------
# Targets
# ----------------------------------------------------
all: build package

build:
	@$(MAKE) -s -C $(SRC_ROOT)/smartnic_322mhz_app/build

package: build_package reg_package p4_package driver_package

build_package:
	@cp $(OUTPUT_ROOT)/smartnic_322mhz_app/build/smartnic_322mhz_app.opt.dcp smartnic_322mhz_app.dcp
	@cp src/smartnic_322mhz_app_pkg.sv smartnic_322mhz_app_pkg.sv

reg_package:
	@$(REGIO_ROOT)/regio-flatten -i $(LIB_ROOT) -o smartnic_322mhz_app_decoder.yaml src/smartnic_322mhz_app_decoder.yaml

p4_package:
	@cp $(P4_FILE) smartnic_322mhz_app.p4
	@find $(dir $(P4_FILE)) -name \*.lua -exec cp {} ./ \;

driver_package:
	# Start: Hack to fix missing files in libvitisnetp4.a and libvitisnetp4.so in Vivado 2022.1.1
	@-cp ${XILINX_VIVADO}/data/ip/xilinx/cam_v2_3/sw/cam_src/inc/bf.h $(OUTPUT_ROOT)/vitisnetp4/xilinx_ip/sdnet_0/src/sw/drivers/cam_obf/inc
	@-cp ${XILINX_VIVADO}/data/ip/xilinx/cam_v2_3/sw/cam_src/src/bf.c $(OUTPUT_ROOT)/vitisnetp4/xilinx_ip/sdnet_0/src/sw/drivers/cam_obf/src
	# End: Hack to fix missing files in libvitisnetp4.a and libvitisnetp4.so in Vivado 2022.1.1
	@$(MAKE) -s -C $(OUTPUT_ROOT)/vitisnetp4/xilinx_ip/sdnet_0/src/sw/drivers && \
	 tar -cf smartnic_322mhz_app_drv.tar -C $(OUTPUT_ROOT)/vitisnetp4/xilinx_ip/sdnet_0/src/sw/drivers/install .

clean:
	@$(MAKE) -s -C $(SRC_ROOT)/smartnic_322mhz_app/build clean
	@rm -rf smartnic_322mhz_app*
	@rm -rf *.lua

.PHONY: all build package build_package reg_package p4_package driver_package clean
