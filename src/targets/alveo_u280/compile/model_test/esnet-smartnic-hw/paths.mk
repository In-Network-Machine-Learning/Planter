# -----------------------------------------------
# Project path setup
#
# Describe paths within library to provided resources.
#
# The intent of this file is that it can be sourced
# by an enclosing project. As such, project-specific paths,
# such as the location of config files or output directories,
# are intentionally not included here, to avoid contention
# with values set by the enclosing project.
# -----------------------------------------------
# Set relative to SMARTNIC__ROOT (current) directory
# Note: SMARTNIC_ROOT is configured in calling (parent) Makefile
ONS_ROOT := $(abspath $(SMARTNIC_ROOT)/open-nic-shell)
