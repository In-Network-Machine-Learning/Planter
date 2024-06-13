# -----------------------------------------------
# Configure project paths
#
# - assumes PROJ_ROOT is defined by calling Makefile
# - at a minimum, must provide:
#
#     SMARTNIC_ROOT: path to root of SmartNIC repo
#     LIB_ROOT: path to common FPGA library providing scripts/tools
#     SRC_ROOT: path to main source (i.e. RTL) library
#     CFG_ROOT__LOCAL: path to local config files (for device config, etc.)
#     OUT_ROOT__LOCAL: path to local output directory
#                       
# -----------------------------------------------
SMARTNIC_ROOT      := $(abspath $(PROJ_ROOT))
LIB_ROOT           := $(SMARTNIC_ROOT)/esnet-fpga-library
SRC_ROOT           := $(SMARTNIC_ROOT)/src

CFG_ROOT__LOCAL    ?= $(SMARTNIC_ROOT)/cfg
OUTPUT_ROOT__LOCAL ?= $(SMARTNIC_ROOT)/.out

# -----------------------------------------------
# Include paths to common scripts/tools
# -----------------------------------------------
include $(LIB_ROOT)/paths.mk

# -----------------------------------------------
# Include paths to local resources
# -----------------------------------------------
include $(PROJ_ROOT)/paths.mk

# -----------------------------------------------
# Include standard project Makefile snippet
# -----------------------------------------------
include $(SCRIPTS_ROOT)/Makefiles/proj_config_base.mk

# -----------------------------------------------
# Define common library
# -----------------------------------------------
COMMON_LIB_NAME := common
