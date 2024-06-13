# *************************************************************************
#
# Copyright 2020 Xilinx, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# *************************************************************************
set curdir [pwd]
cd ../../smartnic_322mhz/build/

# read design sources
source add_sources.tcl
read_checkpoint -cell box_322mhz_inst/smartnic_322mhz/smartnic_322mhz_app $app_root/app_if/smartnic_322mhz_app.dcp

# read constraints
read_xdc constraints/${board}/timing.xdc
read_xdc constraints/${board}/place.xdc
set lib_root $env(LIB_ROOT)
read_xdc $lib_root/src/sync/build/sync.xdc

cd $curdir
