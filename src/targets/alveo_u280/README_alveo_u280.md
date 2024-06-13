### Setup for running Planter on Alveo U280 FPGA

To run Planter on the Alveo U280 FPGA, additional packages must be installed that are required by Esnet-SmartNIC. These requirements are listed in the README files for these two repositories, which are located under src/targets/alveo_u280/compile/model_test.

The currently supported models for the Alveo U280 FPGA are DT Type_1_xsa and RF Type_1_xsa.

After running the compile mode for the FPGA, the FPGA cmac ports still need to be configured to send and receive packets. This is done using the esnet-smartnic-fw repository. The commands for this are (the path for the Planter repository will need to be changed depending on where it is located):

```
cd Planter/src/targets/alveo_u280/compile/model_test/esnet-smartnic-fw/sn-stack
docker compose exec smartnic-fw bash
sn-cli cmac enable
sn-cli sw in-port-rename cmac0:cmac0 cmac1:cmac1 host0:host0 host1:host1
sn-cli sw in-port-connect cmac0:app0 cmac1:app0
sn-cli sw app0-port-redirect cmac0:cmac0 cmac1:cmac1 host0:host0 host1:host1
```
