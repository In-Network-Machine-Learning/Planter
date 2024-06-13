# Planter Supports
![Planter Logo](../../images/logo.png)
<aside>
💡 A guide to Planter supported architectures.

</aside>

## Supported Architectures
The architectures here are indicative of the architecture used in your p4 file (e.g., ```#include <tna.p4>```). It is located under the ```./src/architectures/``` folder. Recommended architectures are marked with 🔥.


**1. TNA 🔥** [Folder](../../architectures/tna) - The Tofino Native Architecture (TNA) [Link](https://github.com/barefootnetworks/Open-Tofino/blob/master/PUBLIC_Tofino-Native-Arch-Document.pdf) is an architecture designed for Intel Tofino hardware and emulation targets. One example is the Tofino Switch. 

**2. v1model 🔥** [Folder](../../architectures/v1model) - The v1model [Link](https://sdn.systemsapproach.org/switch.html) was originally designed to support P4<sub>14</sub> and later to support P4<sub>16</sub>. It is used in BMv2, P4Pi-enabled BMv2, and P4Pi-enabled T4P4S. 

**3. PSA** [Folder](../../architectures/psa) - The Portable Switch Architecture (PSA) [Link](https://p4.org/specs/) architecture is more realistic compared with v1model. Although the PSA has workable demos, it is still under development.
 
**4. XSA** [Folder](../../architectures/xsa) - The xsa architecture is for AMD Alveo U280 FPGA over Open-NIC.
 
**5. Spectrum** [Folder](../../architectures/spectrum) - The spectrum architecture is for NVIDIA Spectrum.
