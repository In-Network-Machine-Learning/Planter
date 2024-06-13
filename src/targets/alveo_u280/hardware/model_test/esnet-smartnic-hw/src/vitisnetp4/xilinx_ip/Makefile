# -----------------------------------------------
# IP config (for compilation library setup)
# -----------------------------------------------
IP_ROOT = ..

include $(IP_ROOT)/config.mk

# -----------------------------------------------
# VitisNetP4 IP config
# -----------------------------------------------
VITISNETP4_IP_NAME = sdnet_0
VITISNET_IP_DIR = $(COMPONENT_OUT_PATH)

P4_FILE ?= $(SRC_ROOT)/p4_app/p4/p4_app.p4
P4_OPTS ?= CONFIG.PKT_RATE {150} CONFIG.OUTPUT_METADATA_FOR_DROPPED_PKTS {true}

# ----------------------------------------------------
# Sources
#   List source files and include directories for component.
#   (see $(SCRIPTS_ROOT)/Makefiles/sources.mk)
#   Note: if no sources are explicitly listed, all
#   source files from ./src are added automatically,
#   with include directory ./include
# ----------------------------------------------------
IP_LIST = $(VITISNETP4_IP_NAME)

SRC_FILES = \
    $(VITISNET_IP_DIR)/$(VITISNETP4_IP_NAME)/src/verilog/$(VITISNETP4_IP_NAME)_top_pkg.sv \
    $(VITISNET_IP_DIR)/$(VITISNETP4_IP_NAME)/src/verilog/$(VITISNETP4_IP_NAME)_pkg.sv \
    $(VITISNET_IP_DIR)/$(VITISNETP4_IP_NAME)/src/verilog/$(VITISNETP4_IP_NAME)_sync_fifos.sv \
    $(VITISNET_IP_DIR)/$(VITISNETP4_IP_NAME)/src/verilog/$(VITISNETP4_IP_NAME)_header_sequence_identifier.sv \
    $(VITISNET_IP_DIR)/$(VITISNETP4_IP_NAME)/src/verilog/$(VITISNETP4_IP_NAME)_header_field_extractor.sv \
    $(VITISNET_IP_DIR)/$(VITISNETP4_IP_NAME)/src/verilog/$(VITISNETP4_IP_NAME)_error_check_module.sv \
    $(VITISNET_IP_DIR)/$(VITISNETP4_IP_NAME)/src/verilog/$(VITISNETP4_IP_NAME)_parser_engine.sv \
    $(VITISNET_IP_DIR)/$(VITISNETP4_IP_NAME)/src/verilog/$(VITISNETP4_IP_NAME)_deparser_engine.sv \
    $(VITISNET_IP_DIR)/$(VITISNETP4_IP_NAME)/src/verilog/$(VITISNETP4_IP_NAME)_action_engine.sv \
    $(VITISNET_IP_DIR)/$(VITISNETP4_IP_NAME)/src/verilog/$(VITISNETP4_IP_NAME)_lookup_engine.sv \
    $(VITISNET_IP_DIR)/$(VITISNETP4_IP_NAME)/src/verilog/$(VITISNETP4_IP_NAME)_axi4lite_interconnect.sv \
    $(VITISNET_IP_DIR)/$(VITISNETP4_IP_NAME)/src/verilog/$(VITISNETP4_IP_NAME)_statistics_registers.sv \
    $(VITISNET_IP_DIR)/$(VITISNETP4_IP_NAME)/src/verilog/$(VITISNETP4_IP_NAME)_match_action_engine.sv \
    $(VITISNET_IP_DIR)/$(VITISNETP4_IP_NAME)/src/verilog/$(VITISNETP4_IP_NAME)_top.sv \
    $(VITISNET_IP_DIR)/$(VITISNETP4_IP_NAME)/src/verilog/$(VITISNETP4_IP_NAME).sv \
	$(VITISNET_IP_DIR)/$(VITISNETP4_IP_NAME)/$(VITISNETP4_IP_NAME)_wrapper.sv

INC_DIRS = \
    $(VITISNET_IP_DIR)/$(VITISNETP4_IP_NAME)/src/hw/include

SRC_LIST_FILES =

# ----------------------------------------------------
# Dependencies
#   List IP component and external library dependencies
#   (see $SCRIPTS_ROOT/Makefiles/dependencies.mk)
# ----------------------------------------------------
COMPONENTS =
EXT_LIBS = cam_v2_3_0 \
           vitis_net_p4_v1_1_0

# ----------------------------------------------------
# Defines
#   List macro definitions.
# ----------------------------------------------------
DEFINES =

# ----------------------------------------------------
# Options
# ----------------------------------------------------
COMPILE_OPTS=
ELAB_OPTS=--debug typical
SIM_OPTS=

# ----------------------------------------------------
# Compile Targets
# ----------------------------------------------------
all: compile

compile: ip _vitisnetp4_drv_dpi _vitisnetp4_exdes _compile

synth: ip _ip_synth

ip: vitisnetp4_wrapper _ip

clean: _clean_compile _ip_clean _vitisnetp4_clean

.PHONY: all compile synth ip clean

# ----------------------------------------------------
# IP management targets
#
#   These targets are used for managing IP, i.e. creating
#   new IP, or modifying or upgrading existing IP.
# ----------------------------------------------------
ip_proj: _ip_proj

ip_status: _ip_status

ip_proj_clean: _ip_proj_clean

.PHONY: ip_proj ip_upgrade ip_status _ip_proj_clean

# ----------------------------------------------------
# Import Vivado compile targets
# ----------------------------------------------------
include $(SCRIPTS_ROOT)/Makefiles/vivado_compile.mk

# ----------------------------------------------------
# Import Vivado IP management targets
# ----------------------------------------------------
include $(SCRIPTS_ROOT)/Makefiles/vivado_vitisnetp4.mk

vitisnetp4_wrapper: $(VITISNETP4_XCI_DIR)/$(VITISNETP4_IP_NAME)_wrapper.sv

.PHONY: vitisnetp4_wrapper

$(VITISNETP4_XCI_DIR)/$(VITISNETP4_IP_NAME)_wrapper.sv: $(VITISNETP4_IP_DIR)/.ip__$(VITISNETP4_IP_NAME)
	$(SMARTNIC_ROOT)/scripts/vitisnetp4/gen_vitisnetp4_wrapper.py $(VITISNETP4_XCI_FILE) --out_dir $(VITISNETP4_XCI_DIR) --template-dir $(SMARTNIC_ROOT)/scripts/vitisnetp4
