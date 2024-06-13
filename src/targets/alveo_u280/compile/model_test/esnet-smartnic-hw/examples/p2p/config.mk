# -----------------------------------------------
# Path to root of SmartNIC repo
# (all other project paths are inferred)
# -----------------------------------------------
SMARTNIC_ROOT = $(abspath $(APP_DIR)/../..)

# -----------------------------------------------
# Application paths
# -----------------------------------------------
SRC_ROOT := $(abspath $(APP_DIR)/src)

# -----------------------------------------------
# Standard application config
# -----------------------------------------------
include $(SMARTNIC_ROOT)/scripts/app_config_base.mk
