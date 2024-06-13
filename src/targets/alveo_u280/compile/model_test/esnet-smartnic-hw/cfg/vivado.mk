# ------------------------------------------------------------------
# Vivado tool configuration
#
# - describes version of Vivado supported by the repository
# - both 'primary' (major + minor) 
# ------------------------------------------------------------------

# 'Major' release version
# - full dot-release, e.g. 2021.2, 2022.1
# - matches install directory, e.g. /tools/Xilinx/Vivado/2022.1
VIVADO_VERSION = 2022.1

# 'Patched' release version
# - e.g. 2022.1, 2022.1.1, 2022.1.1_AR88888
# - matches output of `vivado -version`, e.g. Vivado v2022.1.1 (64-bit)
VIVADO_VERSION__WITH_PATCHES = 2022.1.1

# ------------------------------------------------------------------
# Vivado IP configuration
#
# - list of IP cores used in project for which licenses are
#   (or may be) required
# - used for validating that the proper licenses are in place
#   ahead of launching builds
# - omitting IP here only omits that IP from being considered in the
#   pre-validation step (i.e. it does not omit the IP from the design)
# ------------------------------------------------------------------
LICENSED_IP = \
    xilinx.com:ip:cmac_usplus:3.1 \
    xilinx.com:ip:vitis_net_p4:1.1
