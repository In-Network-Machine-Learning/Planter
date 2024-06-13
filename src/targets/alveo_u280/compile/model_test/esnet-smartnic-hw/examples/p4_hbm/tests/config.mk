# -----------------------------------------------
# Path setup
# -----------------------------------------------
# Set relative to IP directory
# Note: IP_ROOT is configured in calling (parent) Makefile
APP_DIR = $(abspath $(IP_ROOT)/..)

# All other project paths can be derived
include $(APP_DIR)/config.mk

# -----------------------------------------------
# Import default IP config
# -----------------------------------------------
include $(SCRIPTS_ROOT)/Makefiles/ip_config_base.mk
