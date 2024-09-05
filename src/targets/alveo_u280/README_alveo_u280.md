# Setup for running Planter on Alveo U280 FPGA

To run Planter on the Alveo U280 FPGA, additional packages must be installed that are required by ESnet-SmartNIC. These requirements are listed in the README files for these repositories (esnet-smartnic-fw, esnet-smartnic-hw, smartnic-dpdk-docker, xilinx-labtools-docker), which are located under Planter/src/targets/alveo_u280/hardware/model_test. These currently support Vivado 2023.2 running on Ubuntu 20.04 LTS. Requirements to start running Planter on Alveo U280 are given below; there is also more information in the repositories listed above.

Docker (for esnet-smartnic-fw)
------

Install Docker on your system following the instructions found here for the **linux** variant that you are using
* https://docs.docker.com/engine/install/

Ensure that you follow the post-install instructions here so that you can run docker **without sudo**
* https://docs.docker.com/engine/install/linux-postinstall/

Verify your docker setup by running this as an ordinary (non-root) user without using `sudo`
```
docker run hello-world
```

Docker Compose (for esnet-smartnic-fw)
--------------

The `docker-compose.yml` file for the smartnic build and the sn-stack depends on features that are only supported in the compose v2 plugin.

Install the `docker compose` plugin like this for a single user:

```
mkdir -p ~/.docker/cli-plugins/
curl -SL https://github.com/docker/compose/releases/download/v2.17.2/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose
chmod +x ~/.docker/cli-plugins/docker-compose
```

Alternatively, you can install the `docker compose` plugin system-wide like this:
```
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl  -o /usr/local/lib/docker/cli-plugins/docker-compose -SL https://github.com/docker/compose/releases/download/v2.17.2/docker-compose-linux-x86_64
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
```

Verify your docker compose installation by running this as an ordinary (non-root) user without using `sudo`.  For this install, the version output should be
```
$ docker compose version
Docker Compose version v2.17.2
```

Download the Xilinx Labtools Installer (for xilinx-labtools-docker)
--------------------------------------

* Open a web browser to this page: https://www.xilinx.com/support/download/index.html/content/xilinx/en/downloadNav/vivado-design-tools/2023-2.html
* Under the `Vivado Lab Solutions - 2023.2` section
  * Download `Vivado 2023.2: Lab Edition - Linux`

The filepath to the download will be required as an input to Planter when running on the Alveo U280 with either compile or hardware mode.

Download the Alveo Smartnic Satellite Controller Update Tool (for xilinx-labtools-docker)
------------------------------------------------------------
* Open a web browser to this page: https://support.xilinx.com/s/article/73654
* At the bottom of the page under the `Files` section
  * Download `loadsc_v2.3.zip`

The filepath to the download will be required as an input to Planter when running on the Alveo U280 with either compile or hardware mode.

Installing prerequisites for the ESnet SmartNIC hardware repository (for esnet-smartnic-hw)
-------------------------------------------------------------------

```
cd Planter/src/targets/alveo_u280/hardware/model_test/esnet-smartnic-hw
git submodule update --init --recursive
sudo apt install python3-yaml python3-jinja2 python3-click
pip3 install -r esnet-fpga-library/tools/regio/requirements.txt
```

Installing and Configuring the Vivado Runtime Environment (for esnet-smartnic-hw)
---------------------------------------------------------

1. Install the AMD (Xilinx) Vivado tool suite, including the VitisNetP4 option. Note, to include the
VitisNetP4 option, the `VitisNetP4_Option_VISIBLE` environment variable must be set to `true` prior to
executing the Vivado installation program.  The example BASH shell command is:

       > export VitisNetP4_Option_VISIBLE=true

2. Configure the runtime environment by executing the settings64.sh script located in the Vivado
installation directory:

       > source /tools/Xilinx/Vivado/2023.2/settings64.sh

   where the Vivado installation directory is located at /tools/Xilinx/Vivado/2023.2/ in this example.

3. Set the XILINXD_LICENSE_FILE environment variable accordingly to resolve the site-specific license for
the AMD (Xilinx) VitisNetp4 IP core.  This can be done with a `.flexlmrc` file in the users home directory,
or in a BASH script file (such as a `.bashrc` in the users home directory).  The example BASH shell
command is:

       > export XILINXD_LICENSE_FILE=<filename>



# Currently supported models and modes

The currently supported models for the Alveo U280 FPGA are DT Type_1_xsa, RF Type_1_xsa, and XGB Type_2_xsa.

There are three different modes available for the Alveo U280 FPGA.

Behavioral: This generates the necessary P4 file that will be used to program the FPGA, as well as the table entries that will be inserted. A behavioral simulation is then performed to test the correctness of these files.

Hardware: This generates the necessary P4 file and table entries, and then uses these to generate files that are used to program the FPGA. After programming the FPGA, a test is performed on the hardware.

Compile: This generates the necessary P4 file and table entries, and then uses these to generate files that are used to program the FPGA. These files are then loaded onto the FPGA. However, the FPGA is not yet able to send and receive packets; the commands to do this are listed below (the path for the Planter repository may need to be changed depending on where it is located):

```
cd Planter/src/targets/alveo_u280/compile/model_test/esnet-smartnic-fw/sn-stack
docker compose exec smartnic-fw sn-cli cmac enable
docker compose exec smartnic-fw sn-cli sw in-port-rename cmac0:cmac0 cmac1:cmac1 host0:host0 host1:host1
docker compose exec smartnic-fw sn-cli sw in-port-connect cmac0:app0 cmac1:app0 host0:bypass host1:bypass
docker compose exec smartnic-fw sn-cli sw app0-port-redirect cmac0:cmac0 cmac1:cmac1 host0:host0 host1:host1
```

These commands are executed automatically when running the hardware mode.