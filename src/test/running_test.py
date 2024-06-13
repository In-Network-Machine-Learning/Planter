# THIS FILE IS PART OF Planter PROJECT
# Planter.py - The core part of the Planter library
#
# THIS PROGRAM IS FREE SOFTWARE TOOL, WHICH MAPS MACHINE LEARNING ALGORITHMS TO DATA PLANE, IS LICENSED UNDER Apache-2.0
# YOU SHOULD HAVE RECEIVED A COPY OF THE LICENSE, IF NOT, PLEASE CONTACT THE FOLLOWING E-MAIL ADDRESSES
#
# Copyright (c) 2020-2021 Changgang Zheng
# Copyright (c) Computing Infrastructure Lab, Department of Engineering Science, University of Oxford
# E-mail: changgang.zheng@eng.ox.ac.uk or changgangzheng@qq.com
#
# Functions: This file is an auto running test.
#            Please refer to ./Docs/Planter_User_Document.pdf or further information.
# Please add the following contents to /tools/p4_build.sh
# #!/bin/bash
# source ~/.bashrc
# source /home/parallels/tools/set_sde.bash
# The first several compiling will be failed, please add the needed packages



import subprocess as sub
import json
import os
import shlex

init_number_features = 3
init_number_trees = 3
init_number_depth =4
max_number_features = 5
max_number_trees = 10
max_number_depth = 10

directory_config = json.load(open('directory_config.json', 'r'))
sde_root = directory_config['sde']
tools_root =  directory_config['tools']
work_root =  directory_config['work']

log_file = 'log.json'
log_dict = {}
json.dump(log_dict, open(log_file, 'w'), indent=4)

model_config = {}
for number_features in range(init_number_features, max_number_features):
    for number_trees in range(init_number_trees,max_number_trees):
        for number_depth in range( init_number_depth, max_number_depth):
            print('\n\n'+('#' * 20) +" Test for parameters: num_feature: " + str(number_features)+" num_tree: " + str(number_trees)+" num_depth: " + str(number_depth)+(' '+'#' * 20) )
            model_config["number of features"] = number_features
            model_config["number of trees"] = number_trees
            model_config["number of classes"] = 2
            model_config["number of depth"] = number_depth
            json.dump(model_config, open('./model_config.json', 'w'), indent=4)
            print('./model_config.json is generated')
            # sub.run(['conda', 'activate' ,'changgang-python3.6'])
            sub.run(['python', 'main.py'])

            p4_config_file = 'config_auto.json'
            p4_generator_config = json.load(open(p4_config_file, 'r'))
            log_file = 'log.json'
            log_dict = json.load(open(log_file, 'r'))
            log_dict["num_feature: " + str(number_features)][ "num_tree: " + str(number_trees)][ "num_depth: " + str(number_depth)]['p4_generator_config'] = {}
            log_dict["num_feature: " + str(number_features)]["num_tree: " + str(number_trees)][
                "num_depth: " + str(number_depth)]['p4_generator_config'] = p4_generator_config
            print('compiling test')
            # os.chdir(sde_root)

            # sub.run(['source', '/home/parallels/tools/set_sde.bash'], shell=True)

            successfully_compiled = None
            result = sub.run([tools_root+'/p4_build.sh', work_root+'/main.p4'],cwd=sde_root)
            if result.returncode ==0:
                successfully_compiled = "yes"
            else: successfully_compiled = "no"

            log_dict["num_feature: " + str(number_features)]["num_tree: " + str(number_trees)][
                "num_depth: " + str(number_depth)]['successfully_compiled'] = successfully_compiled

            json.dump(log_dict, open(log_file, 'w'), indent=4)
            print('P4 generator parameters and compiling result are downloaded to log as', log_file)

