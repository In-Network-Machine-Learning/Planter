# Planter Supports
![Planter Logo](../../images/logo.png)
<aside>
💡 A guide to Planter supported targets.

</aside>

## Supported targets
Targets refer to the hardware or software programmable targets, running a supported architecture.

**1. Tofino** [Folder](../../targets/Tofino) - Tofino is a programmable switch ASIC supporting high throughput and low latency packet switching.
- **How to install?** The emulation and test environment (bf-sde-x.y.z) for the Intel/Barefoot Tofino Switch is under NDA. Please contact Intel/Barefoot Tofino for information. 
- A module support for barefoot SDE versions earlier than bf-sde-9.7.0 is **Tofino_old_SDE_version**.
- A module support for Tofino's second-generation programmable switch design is **Tofino2**.

**2. BMv2** [Folder](../../targets/bmv2) - BMv2 is a P4 behavioural model of a software switch. 
- **How to install?** Please follow the [Link](https://github.com/p4lang/behavioral-model) to install the required environment for the behavioral model version 2 (BMv2). BMv2 versions 1.15.0 and 1.14.0 are tested.

**3. NVIDIA Spectrum** [Link](../../targets/NVIDIA_Spectrum) - Spectrum is a type of NVIDIA high performance programmable ethernet switches. 
- **How to use?** This target only supports P4 codes in NVIDIA's specific P4 architecture. When using this target, the Planter should run under administration permission.
- The current NVIDIA Spectrum target only supports the compilation of P4 files.

**4. P4Pi (T4P4S)** [Link](../../targets/t4p4s) - P4Pi platform can generate DPDK-based software switches by using the T4P4S compiler. It supports P4 codes in PSA and v1model. T4P4S front end uses p4c reference compiler and basic end compiler generates target-agnostic switch code. Planter can generate P4 files for BMv2 and T4P4S compilers on P4Pi. 
- **How to install?** Please follow the [Link](https://github.com/p4lang/p4pi) to install the P4Pi. 

**5. Alveo u280** [Link](../../targets/alveo_u280) - AMD Alveo U280 FPGA over Open-NIC.

**6. P4Pi (BMv2)** [Folder](../../targets/bmv2)

**7. NVIDIA BlueField2** [Folder](../../targets/bmv2)
