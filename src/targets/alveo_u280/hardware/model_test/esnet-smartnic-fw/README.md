# Copyright Notice

ESnet SmartNIC Copyright (c) 2022, The Regents of the University of
California, through Lawrence Berkeley National Laboratory (subject to
receipt of any required approvals from the U.S. Dept. of Energy),
12574861 Canada Inc., Malleable Networks Inc., and Apical Networks, Inc.
All rights reserved.

If you have questions about your rights to use or distribute this software,
please contact Berkeley Lab's Intellectual Property Office at
IPO@lbl.gov.

NOTICE.  This Software was developed under funding from the U.S. Department
of Energy and the U.S. Government consequently retains certain rights.  As
such, the U.S. Government has been granted for itself and others acting on
its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the
Software to reproduce, distribute copies to the public, prepare derivative
works, and perform publicly and display publicly, and to permit others to do so.


# Support

The ESnet SmartNIC platform is made available in the hope that it will
be useful to the networking community. Users should note that it is
made available on an "as-is" basis, and should not expect any
technical support or other assistance with building or using this
software. For more information, please refer to the LICENSE.md file in
each of the source code repositories.

The developers of the ESnet SmartNIC platform can be reached by email
at smartnic@es.net.


Setting up the build environment
================================

The smartnic firmware build depends on `docker` and the `docker compose` plugin.

Docker
------

Install Docker on your system following the instructions found here for the **linux** variant that you are using
* https://docs.docker.com/engine/install/

Ensure that you follow the post-install instructions here so that you can run docker **without sudo**
* https://docs.docker.com/engine/install/linux-postinstall/

Verify your docker setup by running this as an ordinary (non-root) user without using `sudo`
```
docker run hello-world
```

Docker Compose
==============

The `docker-compose.yml` file for the smartnic build and the sn-stack depends on features that are only supported in the compose v2 plugin.

Install the `docker compose` plugin like this for a single user:

```
mkdir -p ~/.docker/cli-plugins/
curl -SL https://github.com/docker/compose/releases/download/v2.12.2/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose
chmod +x ~/.docker/cli-plugins/docker-compose
```

Alternatively, you can install the `docker compose` plugin system-wide like this:
```
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl  -o /usr/local/lib/docker/cli-plugins/docker-compose -SL https://github.com/docker/compose/releases/download/v2.12.2/docker-compose-linux-x86_64
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
```

Verify your docker compose installation by running this as an ordinary (non-root) user without using `sudo`.  For this install, the version output should be
```
$ docker compose version
Docker Compose version v2.12.2
```

Git Submodules
--------------
Ensure that all submodules have been pulled.

```
git submodule init
git submodule update
```

Building a new firmware image
=============================


Install Smartnic Hardware Build Artifact
----------------------------------------

The firmware build depends on the result of a smartnic hardware (FPGA) build.  This file must be available prior to invoking the firmware build.

This file will be called `artifacts.<board>.<build_name>.0.zip` and should be placed in the `sn-hw` directory in your source tree before starting the firmware build.

Set up your .env file for building a new firmware image
-------------------------------------------------------

The `.env` file tells the build about its inputs and outputs.

There is an `example.env` file in top level directory of this repo that will provide documentation and examples for the values you need to set.

```
cd $(git rev-parse --show-toplevel)
cp example.env .env
```

Build the firmware
------------------

The firmware build happens inside of a docker container which manages all of the build-time dependencies and tools.

```
cd $(git rev-parse --show-toplevel)
docker compose build
docker compose run --rm sn-fw-pkg
```

Note: to pick up the very latest Ubuntu packages used in the build environment, you may wish to occasionally run `docker compose build --no-cache` to force the build env to be refreshed rather than (potentially) using the previously cached docker image.

The firmware build produces its output files in the `sn-stack/debs` directory where you'll find files similar to these
```
cd $(git rev-parse --show-toplevel)
$ tree sn-stack/debs/
sn-stack/debs/
└── focal
    ├── esnet-smartnic_1.0.0-user.001_amd64.buildinfo
    ├── esnet-smartnic_1.0.0-user.001_amd64.changes
    ├── esnet-smartnic1_1.0.0-user.001_amd64.deb
    ├── esnet-smartnic1-dbgsym_1.0.0-user.001_amd64.ddeb
    └── esnet-smartnic-dev_1.0.0-user.001_amd64.deb
```

These files will be used to customize the smartnic runtime environment and the `esnet-smartnic-dev_*` packages can also be used in your application software development environment.  For further details about the contents of these `.deb` files, see `README.fw.artifacts`.

The entire `sn-stack` directory will need to be transferred to the runtime system.

```
cd $(git rev-parse --show-toplevel)
zip -r artifacts.esnet-smartnic-fw.package_focal.user.001.zip sn-stack
```
