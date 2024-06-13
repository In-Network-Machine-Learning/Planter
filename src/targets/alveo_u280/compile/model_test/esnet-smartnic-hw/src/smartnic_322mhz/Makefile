# -----------------------------------------------
# Path setup
# -----------------------------------------------
IP_ROOT := .

# -----------------------------------------------
# IP config
# -----------------------------------------------
include $(IP_ROOT)/config.mk

# -----------------------------------------------
# Targets
# -----------------------------------------------
all: regression

regression: _regression

clean: _clean

.PHONY: all regression clean

# Import standard IP root targets
include $(SCRIPTS_ROOT)/Makefiles/ip_base.mk

