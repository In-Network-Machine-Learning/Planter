# Planter Supports
![Planter Logo](../../images/logo.png)
<aside>
💡 A guide to Planter supported use cases.

</aside>


## Supported use cases 
Planter currently supports four use cases. Here, each use case represents a type of networking paradigm, while the injected packets will be determined by the selected datasets. Recommended use cases are marked with 🔥.

**1. Standard Classification 🔥** [Folder](../../use_cases/standard_classification) - This use case is for functionality verification. In this case, the sender sends packets containing ```Ether|Planter``` headers, which the switch will parse, infer, and send the inference back straight to the sender.

**2. Anomaly Detection** [Folder](../../use_cases/anomaly_detection) - This is an anomaly detection use case. In this case, the IP 5-tuple will be used as input features, and the Planter will be able to create P4 files for parsing and classifying IP 5-tuples.

**3. Performance 🔥** [Folder](../../use_cases/performance) - The "Performance" mode is a template that shows the performance. Select only type EB, LB, or DM when choosing this mode. The stage consumption in this mode is manually optimized (better than the paper). This use case is very similar to the "Standard Classification" use case.

**4. Standard UDP** [Folder](../../use_cases/standard_UDP) - In this use case, the input and final results are encapsulated in UDP. The sender sends packets containing ```Ether|IP|UDP|Planter|<binary data>``` headers, which the switch will parse, infer, and send the inference back straight to the sender.

**5. Standard ASCII** [Folder](../../use_cases/standard_ASCII) - In this use case, the input and final results are encapsulated in UDP. The sender sends packets containing ```Ether|IP|UDP|Planter|<ASCII data>``` headers, which the switch will parse, infer, and send the inference back straight to the sender. This use case targets parsing unencrypted text files.

**6. Performance ASCII** [Folder](../../use_cases/performance_ASCII) - This is the combination of the performance mode and the standard ASCII mode.

**7. Performance Snake** [Folder](../../use_cases/performance_ASCII) - This is the combination of the performance mode and snake test (cost 3 extra stages). The snake test is used to test the throughput.

**8. Standard Classification for XSA** [Link](../../use_cases/standard_classification_with_xsa_support) - Support AMD Alveo U280 FPGA over Open-NIC.
