# -----------------------------------------------
# Path setup
# -----------------------------------------------
IP_ROOT := ..

# -----------------------------------------------
# IP config
# -----------------------------------------------
include $(IP_ROOT)/config.mk

# -----------------------------------------------
# Configuration
# Note: these parameters can also be provided
#       at the command line, e.g.:
#       make REGRESSION=1
#       make waves=ON
#       make SEED=29 waves=ON
# -----------------------------------------------
REGRESSION ?= 0
SEED ?= 0
waves ?= OFF

# ----------------------------------------------------
# Top
#   Specify top module(s) for elaboration
# ----------------------------------------------------
TOP = $(SVUNIT_TOP) p4_and_verilog__tb.tb

# ----------------------------------------------------
# Sources
#   List source files and include directories for test
#   (see $(SCRIPTS_ROOT)/Makefiles/sources.mk)
#   NOTE: SVUnit sources are automatically included
# ----------------------------------------------------
SRC_FILES =
INC_DIRS =
SRC_LIST_FILES = $(SVUNIT_SRC_LIST_FILE)

# ----------------------------------------------------
# Dependencies
#   List IP component and external library dependencies
#   (see $SCRIPTS_ROOT/Makefiles/dependencies.mk for details)
# ----------------------------------------------------
COMPONENTS = p4_and_verilog.rtl \
             p4_and_verilog.verif \
             p4_and_verilog.tb \
             axi4l.rtl@common@smartnic \
             axi4s.rtl@common@smartnic

EXT_LIBS =

# ----------------------------------------------------
# Defines
#   List macro definitions.
#   Macros listed here will add to any defines set at
#   command line, as e.g.:
#     make DEFINES="DEBUG FAST=TRUE"
# ----------------------------------------------------
override DEFINES += SIMULATION

# ----------------------------------------------------
# VitisNetP4 DPI-C driver
# ----------------------------------------------------
VITISNETP4_DRV_DPI_DIR = $(OUTPUT_ROOT)/vitisnetp4/xilinx_ip/sdnet_0
VITISNETP4_DRV_DPI_LIB = vitisnetp4_drv_dpi
VITISNETP4_DRV_DPI_FILE = $(VITISNETP4_DRV_DPI_DIR)/$(VITISNETP4_DRV_DPI_LIB).so

# ----------------------------------------------------
# Options
# ----------------------------------------------------
COMPILE_OPTS +=

ELAB_OPTS += --debug typical --sv_lib $(VITISNETP4_DRV_DPI_LIB) --sv_root $(VITISNETP4_DRV_DPI_DIR)

SIM_OPTS +=

# ----------------------------------------------------
# Targets
# ----------------------------------------------------
all: p4bm build_test sim

p4bm:
	$(MAKE) sim-all-svh P4BM_LOGFILE="-l log" -C $(APP_DIR)/p4/sim

build_test: _build_test

sim: _sim

clean: _clean_test _clean_sim

.PHONY: all p4bm build_test sim clean

# ----------------------------------------------------
# Test configuration
# ----------------------------------------------------
SRC_DIR = .
INC_DIR = .

# ----------------------------------------------------
# Import SVUNIT build targets/configuration
# ----------------------------------------------------
include $(SCRIPTS_ROOT)/Makefiles/svunit.mk

# Export SVUNIT configuration
SVUNIT_TOP = $(COMPONENT_NAME).$(SVUNIT_TOP_MODULE)
SVUNIT_SRC_LIST_FILE = $(SVUNIT_FILE_LIST)

# ----------------------------------------------------
# Import Vivado sim targets
# ----------------------------------------------------
include $(SCRIPTS_ROOT)/Makefiles/vivado_sim.mk

