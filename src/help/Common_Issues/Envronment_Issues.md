# Common Issues
![Planter Logo](../../images/logo.png)
<aside>
💡 A guide to solve Planter's environment setup issues.

</aside>

## Common Environment Issues:

- **_The general rule is to run Planter in the same environment SDE is installed._**

- The architectures here are indicative of the architecture used - Environment: in each computer, there is a system-default python with version 2 or 3 (In my case, version 2.7 or 3.6). Under ```sudo su```, there is also a system-default python with version 2.7 or 3.6. You may also have your own created environment (e.g., conda environment). Please carefully choose the environment where you install the needed packages. For example, scapy should be installed under admin python 3.6:

  ```
  sudo su
  pip3 install scapy
  ``` 
  If the main program ```Planter.py``` is going to run under the conda environment:
  
  ```
  conda activate your_environment_name
  conda install required_packets
  python Planter.py -m
  ``` 

If it turns out that some packages were not installed (even though you have set up the environment based on ```requirements.txt```), install the missing packages manually.

💡 To set up Planter on P4Pi-enabled BMv2, follow the wiki page in [this link](./src/help/Throughput_Test/Planter_throughput_test_P4Pi-BMv2.md).


## Common Running Issues:

- **_The general rule is to debug while using, there may always be some unknown bugs when new modules are added._**

- If there are errors show:
  ```
  Traceback (most recent call last):
  File "/home/Planter/Planter/Planter.py", line 302, in <module>
    Planter()
  File "/home/Planter/Planter/Planter.py", line 190, in Planter
    sklearn_test_y = main_functions.run_model(train_X, train_y, test_X, test_y, used_features)
  File "/home/Planter/Planter/src/models/XGB/Type_EB_auto/table_generator.py", line 330, in run_model
    g_table, leaf_info = generate_table(estimator, idx, g_table, num_features, feature_names, feature_max, leaf_info)
  File "/home/Planter/Planter/src/models/XGB/Type_EB_auto/table_generator.py", line 185, in generate_table
    g_table[tree_index] = generate_feature_tables(feature_split, num_features, feature_max, g_table[tree_index])
  File "/home/Planter/Planter/src/models/XGB/Type_EB_auto/table_generator.py", line 124, in generate_feature_tables
    for j in range(feature_max[i]+1):
  TypeError: 'float' object cannot be interpreted as an integer
  ``` 
  This is due to the maximum value of each feature is not under the int type. The following code: 
  ```
  feature_max += [np.max(t_t)+1]
  ``` 
  should be replaced by:
  ```
  feature_max += [int(np.max(t_t)+1)]
  ``` 

