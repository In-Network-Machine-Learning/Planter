# Planter Supports
![Planter Logo](../../images/logo.png)
<aside>
💡 A guide to Planter supported in-network ML algorithms and their variations.

</aside>


## Supported ML Algorithms

Each ML model can be mapped to a data plane in multiple ways. The three common ways are Direct Map (DM), Lookup Based (LB), and Encode Based (EB). In addition, there are multiple other ways, often a variation of the three, marked as Type_N. 

Mappings marked as EB, DM, or LB are suitable only for the performance use case. In these cases, stage allocation is better with manual optimization (better than in the paper). 

The recommended variation for each model is marked with 🔥.

**1. Decision Tree (DT)** [Folder](../../models/DT)

- **Type EB:** - Select only in conjunction with the performance use case.  This mapping is based on Type 3. The stage consumption is manually optimized (better than the paper).
- **Type DM:** - Select only in conjunction with the performance use case. This mapping is based on Depth Based BMv2 Only. The stage consumption is manually optimized (better than the paper).
- **Type 1:** In this mapping, feature tables can share stages. This model uses only exact match feature tables and decision tables (without a default action).  This is a reproduction of IIsy's DT.
- **Type 2:** Type 2 model is similar to Type 1, but uses a default action to reduce the number of entries in the decision table.
- **Type 3 🔥:** DT<sub>EB</sub> - This mapping is based on Type 2. Feature tables can share stages, and it uses ternary matches to reduce the number of entries in the feature tables, as well as default actions.
- **Type 4:** This mapping is very similar to Type 3 DT<sub>EB</sub>. It uses lpm match to reduce the number of entries in the feature tables.
- **Type 5:** This mapping is very similar to Type 1. It uses lpm match to reduce the number of entries in both feature and tree tables.
- **Type Depth Based BMv2 Only:** (DT<sub>DM</sub> - The original SwitchTrees' (and pForest's) design fitted into the Planter framework.
- **Type 1 xsa:** - The variation to support xsa architecture (AMD Alveo U280 FPGA over Open-NIC).

The bug of EB tree models when input has a large number of features has been fixed in Type 3, Type 4, and Type EB.

**2. Random Forest (RF)** [Folder](../../models/RF)

- **Type EB:** - Select only in conjunction with the performance use case. The stage consumption is manually optimized (better than the paper). 
- **Type DM:** - Select only in conjunction with the performance use case. The stage consumption is manually optimized (better than the paper). This is the SwitchTree method and optimized for Tofino.
- **Type 1:** In this mapping of RF model, feature tables can share stages and code tables can share another stage. However, this model uses only exact match feature tables as well as tree tables and decision tables (without a default action). 
- **Type 2:** Type 2 model is similar to Type 1, but uses a default action to reduce the number of entries in tree and decision tables.
- **Type 3:** RF<sub>EB</sub> - This mapping is based on Type 2. It uses a ternary match to reduce the number of entries in feature tables.
- **Type 4 🔥:** RF<sub>EB</sub> - This mapping is based on Type 3. It uses the lpm match to reduce the number of entries in feature tables.
- **Type 5:** This mapping is based on Type 4. It uses the lpm match tables to reduce the number of entries in feature, tree, and decision tables.
- **Type hybrid:** This mapping supports the hybrid use case. A large on-server model and a small on-switch model will be trained to collaboratively solve a classification problem. This mapping allows different trees to use different features, which allows using a larger number of features in the model.
- **Type Depth Based BMv2 Only:** The original SwitchTrees' (and pForest's) design fitted into the Planter framework.
- **Type EB_auto:** - Same as EB (support updated CLI).
- **Type Depth Based:** RF<sub>DM</sub> - An adjusted SwitchTrees' (and pForest's) design to fit the Planter's auto-generation system. It can be optimized to run on TNA. 
- **Type DM BMv2 Only:** - The most standard SwitchTree method (not optimized for Tofino).
- **Type hybrid EB:** -Select only in conjunction with the performance use case (Same as Type hybrid).
- **Type 1 xsa:** - The variation to support xsa architecture (AMD Alveo U280 FPGA over Open-NIC).

The bug of EB tree models when input has a large number of features has been fixed in Type 3, Type 4, and Type EB.

**3. XGBoost (XGB)** [Folder](../../models/XGB) 
 
- **Type EB:** - Select only in conjunction with the performance use case. The stage consumption in this mode is manually optimized (better than the paper).
- **Type 1:** XGB<sub>EB</sub> - This mapping of XGB model is very similar to the Type 3 RF. Type 3 XGB uses a ternary match to reduce the number of entries in the feature tables. It also uses a default action to reduce the number of entries in tree and decision tables.
- **Type 2 🔥:** XGB<sub>EB</sub> - This mapping is based on Type 1. It uses lpm match to reduce the number of entries in feature tables.
- **Type 3:** This mapping is based on Type 2. It uses lpm match table to reduce the number of entries in feature, tree, and decision tables.
- **Type hybrid:** This mapping supports the hybrid use case. A large on-server model and a small on-switch model will be trained to collaboratively solve a classification problem. 
- **Type EB_auto:** - Similar to EB (support updated CLI). More than CLI, this EB version adds an option to do accuracy and model size trade-offs.
- **Type 1 xsa:** - The variation to support xsa architecture (AMD Alveo U280 FPGA over Open-NIC).

**4. Support Vector Machine (SVM)** [Folder](../../models/SVM) 
 
- **Type LB:** - Select only in conjunction with the performance use case. The stage consumption in this mode is manually optimized (better than the paper).
- **Type 1 🔥:** SVM<sub>LB</sub> - This is SVM model mapped using a lookup-based approach. This is a reproduction of IIsy's SVM.


**5. Naive Bayes (NB)** [Folder](../../models/Bayes)

- **Type LB:** - Select only in conjunction with the performance use case. The stage consumption in this mode is manually optimized (better than the paper).
- **Type 1 🔥:** NB<sub>LB</sub> - This mapping of NB uses log() operation to change Bayes from comparing ‘multiplied components’ to ‘added components’, which achieves a better result and saves memory.
- **Type 2:** In this mapping, after training, P(x<sub>i</sub>|y) is mapped to a predefined range. It is then converted to int and used for P(X|y) lookups, where X={x<sub>1</sub>, x<sub>2</sub>, ..., x<sub>n</sub>}.
- **Type 3:** This mapping is very similar to the Type 1. The difference is that this mapping allows all feature tables to share stages. It saves stages, but requires more logic operations.
- **Type LB Bernoulli:** - Select only in conjunction with the performance use case. Different from Type 1-3 and Type LB using traditional GaussianNB, this Type LB Bernoulli applies BernoulliNB.


**6. K-means (KM)** [Folder](../../models/KM) 
 
- **Type LB:** - Select only in conjunction with the performance use case. The stage consumption in this mode is manually optimized (better than the paper).
- **Type EB:** - Select only in conjunction with the performance use case. The stage consumption in this mode is manually optimized (better than the paper).
- **Type 1 🔥:** KM<sub>LB</sub> - In this mapping, M/A tables are used to store an intermediate result (L2 distance) of each feature component. The next operation in the pipeline is logic-based, adding up all the components. Next, there is a comparison and labeling of the packet. This is the reproduction of IIsy's K-means.
- **Type Clustream 🔥:** (KM<sub>EB</sub> - This mapping is Clustream's design. This solution is classified as an encode-based solution. The input features should be preprocessed on the host before in-band classification. 


**7. K-nearest Neighbors (KNN)** [Folder](../../models/KNN) 
 
- **Type EB:** - Select only in conjunction with the performance use case. The stage consumption in this mode is manually optimized (better than the paper).
- **Type 1:** (KNN<sub>EB</sub> - This mapping solution is similar to Clustream's design and can be classified as an encode-based solution. The input features should be preprocessed on the host before in-band classification. 


**8. Autoencoder (Autoencoder)** [Folder](../../models/Autoencoder)

- **Type LB:** - Select only in conjunction with the performance use case. The stage consumption in this mode is manually optimized (better than the paper).
- **Type 1:** AE<sub>LB</sub> - A newly designed Autoencoder model based on the lookup-based approach.

**9. Principle Component Analysis (PCA)** [Folder](../../models/PCA) 
 
- **Type LB:** - Select only in conjunction with the performance use case. The stage consumption in this mode is manually optimized (better than the paper).
- **Type 1 🔥:** PCA<sub>LB</sub> - A newly designed PCA model based on the lookup-based approach.

**10. Isolation Forest (IF)** [Folder](../../models/IF) 
 
- **Type EB:** - (Same as Type 1) Select only in conjunction with the performance use case. The stage consumption in this mode is manually optimized.
- **Type 1 🔥:** IF<sub>EB</sub> - A newly designed IF model based on the encode-based approach. This mapping will help you to gain the same result as the original paper. The lpm match in this variation is used to reduce the number of entries in feature tables.
- **Type 2:** IF<sub>EB</sub> - This mapping is the simplified version of scikit-learn. The result consumes fewer table entries but is different from the original paper. It uses the lpm match to reduce the number of entries in feature tables.
- **Type Simplified EB:** - (Same as Type 2) Select only in conjunction with the performance use case. The stage consumption in this mode is manually optimized.

**11. Neural Network (NN)** [Folder](../../models/NN) 

- **Type DM:** - Select only in conjunction with the performance use case. The stage consumption in this mode is manually optimized (better than the paper).
- **Type 1 🔥:** NN<sub>DM</sub> - This mapping is based on Qin's work. The latest version has some tiny flaws in the NN model training process. The current implementation uses MLP instead of XNOR Net. (the XNOR Net implementation was tried, but the accuracy was different than expected)

