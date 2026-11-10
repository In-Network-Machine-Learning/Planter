
# DPDK Software Target (p4c-dpdk)

This target extends Planter with support for the `p4c-dpdk` compiler backend, enabling in-network machine learning inference using DPDK software pipelines.

## Overview

The DPDK target enables Planter-generated P4 programs to be compiled and executed using `p4c-dpdk` and DPDK SWX. It supports deployment on resource-constrained edge devices, including Raspberry Pi 5.

This integration was developed as part of **PlanPi**, extending Planter to the P4Pi platform.

## Key Features

- **DPDK Target Support:** Compilation and execution of Planter-generated P4 programs using `p4c-dpdk`.
- **Raspberry Pi Integration:** Deployment of in-network ML on Raspberry Pi 5 using the P4Pi platform.
- **ML Model Support:** End-to-end deployment and validation of Decision Tree and Random Forest classifiers.
- **Performance:** Up to 22.1× higher lossless packet rate compared with BMv2 in the reported PlanPi evaluation.
- **Applications:** Traffic classification and network anomaly detection.

## Using the DPDK Target

The implementation is located in `src/targets/dpdk/software/`.

The target consists of:

- `run_model.py`: Compiles P4 programs using `p4c-dpdk`, prepares DPDK pipeline specifications, and generates table entries and pipeline configuration.
- `test_model.py`: Executes packet-based inference tests and validates classification results.

To select the target, run Planter:

    python3 Planter.py -m

Select the following options:

- Architecture: `psa`
- Target device: `dpdk`
- Target type: `software`

The target requires a working `p4c-dpdk` compiler and DPDK pipeline environment. The current implementation includes compatibility adjustments for DPDK 20.11.

## PlanPi Project

PlanPi was developed through **Google Summer of Code (GSoC) 2026**, under the P4 Language Consortium, and is presented at **EuroP4 2026**.

### Resources

- [PlanPi GitHub Repository](https://github.com/ox-computing/PlanPi)
- [PlanPi Paper (EuroP4 2026)](https://ora.ox.ac.uk/objects/uuid:f90dd9fe-d7b9-423f-b7b8-6624fcf594e4)
- [GSoC 2026 Project Report](https://p4lang.github.io/gsoc/blog/posts/2026-08-24-p4pi/)
- [P4Pi Platform](https://github.com/p4lang/p4pi)
