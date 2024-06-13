# Specify project paths in terms of (child) PROJ_ROOT
SMARTNIC_ROOT = $(abspath $(PROJ_ROOT)/..)
CFG_ROOT__LOCAL = $(SMARTNIC_ROOT)/cfg
OUTPUT_ROOT__LOCAL = $(SMARTNIC_ROOT)/.out/common

# Source other project paths
include $(SMARTNIC_ROOT)/paths.mk
