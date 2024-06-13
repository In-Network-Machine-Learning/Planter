# ----------------------------------------------------
# Standard application configuration Makefile snippet
# - assumes the following paths have been defined
#   in the calling (parent) Makefile:
#   SMARTNIC_ROOT: path to root of SmartNIC (platform) repo
#   APP_DIR : path to root of SmartNIC application repo
# ----------------------------------------------------
# Configure project paths
include $(SMARTNIC_ROOT)/paths.mk

# Configure common library paths for access to compile/build scripts
LIB_ROOT := $(SMARTNIC_ROOT)/esnet-fpga-library
include $(LIB_ROOT)/paths.mk

# Device configuration
CFG_ROOT := $(SMARTNIC_ROOT)/cfg

# Local paths
OUTPUT_ROOT := $(APP_DIR)/.app/out

# Auto-configure source library for P4-only applications
ifeq ($(wildcard $(APP_DIR)/app_if/.),)
SRC_ROOT := $(APP_DIR)/.app/src
endif

include $(SCRIPTS_ROOT)/Makefiles/proj_config_base.mk
