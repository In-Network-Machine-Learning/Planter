#------- Variables -------
# Notes:
#  In typical usage, this Makefile will be invoked within the context
#  of a particular SmartNIC application. Direct invocation is also
#  supported.

# Configure project paths
PROJ_ROOT := $(CURDIR)
include $(PROJ_ROOT)/config.mk

# Configure default application if none is specified
APP_DIR ?= $(CURDIR)/src/p4_app

# Include standard application configuration
include $(PROJ_ROOT)/scripts/app_config.mk

ARTIFACTS_BUILD_DIR := $(ARTIFACTS_DIR)/$(BUILD_NAME)

# Build options
max_pkt_len ?= 1518
jobs ?= 16

#------- Targets -------

build: bitfile package

# Include targets for config validation
# - checks Vivado version
# - checks that licenses are available for IP, where required
# - checks that required command-line utilities are available in path
include $(SCRIPTS_ROOT)/Makefiles/config.mk

config : $(APP_DIR)/.app/config.mk
	$(_print_app_config)

$(APP_DIR)/.app/config.mk: $(APP_DIR)/Makefile
	$(_configure_app)

proj_paths:
	$(_proj_print_paths)

bitfile : config config_check
	@echo "Starting bitfile build $(BUILD_NAME)..."
	@echo "Generating smartnic platform IP..."
	@$(MAKE) -s -C $(APP_ROOT)/app_if
	@$(MAKE) -s -C $(PROJ_ROOT)/src/smartnic_322mhz/build APP_ROOT=$(APP_ROOT)
	@echo "Generating smartnic bitfile..."
	@$(MAKE) -C $(PROJ_ROOT) -f makefile.esnet bitfile \
		BOARD=$(BOARD) BUILD_NAME=$(BUILD_NAME) APP_ROOT=$(APP_ROOT) max_pkt_len=$(max_pkt_len) jobs=$(jobs)

package : | $(ARTIFACTS_BUILD_DIR)
	@echo "Packaging build $(BUILD_NAME)..."
	@$(MAKE) -C $(PROJ_ROOT) -f makefile.esnet package \
		BOARD=$(BOARD) BUILD_NAME=$(BUILD_NAME) APP_ROOT=$(APP_ROOT) ARTIFACTS_BUILD_DIR=$(ARTIFACTS_BUILD_DIR)

clean_build :
ifneq ($(wildcard $(APP_DIR)/app_if),)
	@-$(MAKE) -s -C $(APP_DIR)/app_if clean
endif
	@-rm -rf $(APP_DIR)/.app
	-$(MAKE) -C $(PROJ_ROOT) -f makefile.esnet clean_build BUILD_NAME=$(BUILD_NAME)

clean_artifacts :
	@-rm -rf $(ARTIFACTS_BUILD_DIR)

.PHONY : config bitfile package clean_build clean_artifacts


$(ARTIFACTS_BUILD_DIR) : | $(ARTIFACTS_DIR)
	@mkdir $(ARTIFACTS_BUILD_DIR)

$(ARTIFACTS_DIR) :
	@mkdir $(ARTIFACTS_DIR)

build_smartnic_322mhz :
	@$(MAKE) -s -C $(PROJ_ROOT)/src/smartnic_322mhz/build all

