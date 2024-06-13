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

driver_package:

clean:
	@$(MAKE) -s -C $(SRC_ROOT)/smartnic_322mhz_app/build clean
	@rm -rf smartnic_322mhz_app*
	@rm -rf *.lua

.PHONY: all build package build_package reg_package p4_package driver_package clean
