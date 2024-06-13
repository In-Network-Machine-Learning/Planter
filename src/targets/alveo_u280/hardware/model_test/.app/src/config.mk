# ----------------------------------------------------
# Path setup
# - specify paths in terms of SRC_ROOT
#   (defined in parent Makefile)
# ----------------------------------------------------
PROJ_ROOT = /home/liam/Planter/src/targets/alveo_u280/hardware/model_test/.app

include $(PROJ_ROOT)/config.mk

# ----------------------------------------------------
# Library setup
# ----------------------------------------------------
LIB_NAME := "model_test"
LIB_DESC := "model_test SmartNIC application library"

# ----------------------------------------------------
# Sub-library config
# ----------------------------------------------------
# LIBRARIES
#
# List of source libraries, as 'name=path' pairs; Allows 'import' of source
# files from libraries located at arbitrary locations.
#
# Indidual IP components can be imported into designs using a dot notation, where
# the most significant element is the name of the source library. For example, the
# following reference might be used to refer to an AXI RTL library from some vendor:
#
#   vendorx.axi.rtl
#
# For this to resolve properly it would be necessary to have a corresponding entry in
# the LIBRARIES variable, describing the path to the referenced library:
#
#   LIBRARIES = vendorx=[path_to_vendorx_library]
#
#  The local library is implied if the library name is omitted. For example, a reference
#  to the AXI rtl library provided in the local library could appear as:
#
#  	 axi.rtl
#
LIBRARIES = smartnic=/home/liam/Planter/src/targets/alveo_u280/hardware/model_test/esnet-smartnic-hw/src

# Specify name of 'common' library (for autogenerating register infrastructure from regio specifications)
COMMON_LIB_NAME = common@smartnic
