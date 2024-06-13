# ----------------------------------------------------
# Path setup
# ----------------------------------------------------
SRC_ROOT = .

include config.mk

# ----------------------------------------------------
# Targets
# ----------------------------------------------------
help: _help

.PHONY: help

compile: _compile

compile_clean: _compile_clean

.PHONY: compile compile_clean

synth: _synth

.PHONY: synth

clean: _clean

.PHONY: clean

# ----------------------------------------------------
# Include standard library targets
# ----------------------------------------------------
include $(SCRIPTS_ROOT)/Makefiles/lib_base.mk
