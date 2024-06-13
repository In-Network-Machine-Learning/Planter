# THIS FILE IS PART OF Planter PROJECT
# Planter.py - The core part of the Planter library
#
# THIS PROGRAM IS FREE SOFTWARE TOOL, WHICH MAPS MACHINE LEARNING ALGORITHMS TO DATA PLANE, IS LICENSED UNDER Apache-2.0
# YOU SHOULD HAVE RECEIVED A COPY OF WTFPL LICENSE, IF NOT, PLEASE CONTACT THE FOLLOWING E-MAIL ADDRESSES
#
# Copyright (c) 2020-2021 Changgang Zheng
# Copyright (c) Computing Infrastructure Group, Department of Engineering Science, University of Oxford
# E-mail: changgang.zheng@eng.ox.ac.uk or changgangzheng@qq.com
#
# Functions: This file is the Planter's front end, which can be activated via the Planter's back end.
#            Please refer to ./Docs/Planter_User_Document.pdf or further information.

import os
import json
import sys
import time
import argparse
import importlib.util
import numpy as np

from sklearn import metrics
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from bayes_opt import BayesianOptimization
# pip install bayesian-optimization

from src.functions.config_modification import *
from src.functions.input_CLI import *
from src.functions.json_encoder import *


def write_config():
    # reload the config file
    Planter_config = reload_config('src/configs/Planter_config.json')

    # ========== prepare config ===========
    if 'model config' not in Planter_config.keys():
        Planter_config['model config'] = {}
    if 'target config' not in Planter_config.keys():
        Planter_config['target config'] = {}
    if 'test config' not in Planter_config.keys():
        Planter_config['test config'] = {}
    Planter_config['model config']['number of trees'] = Planter_config['optimisation config']['opt number of trees']
    Planter_config['model config']['number of depth'] = Planter_config['optimisation config']['opt number of depth']
    Planter_config['model config']['max number of leaf nodes'] = Planter_config['optimisation config']['opt max number of leaf nodes']
    Planter_config['model config']['model'] = 'RF'
    Planter_config['model config']['type'] = 'EB_auto'
    Planter_config['model config']['test table'] = 'n'
    Planter_config['target config']['architecture'] = 'tna'
    Planter_config['target config']['use case'] = 'performance'
    Planter_config['target config']['device'] = 'Tofino'
    Planter_config['target config']['type'] = 'compile_for_opt_mode'
    Planter_config["test config"]["type of test"] = "classification"
    Planter_config["test config"]["baseline model"] = "None"
    Planter_config["test config"]["port"] = "veth7"
    Planter_config["test config"]["sudo password"] = "12345"
    Planter_config["directory config"]["sde-tools existance"] = "y"
    Planter_config["directory config"]["sde-tools config file name"] = "Directory_config.json"

    # dump the planter config
    dump_config(Planter_config, 'src/configs/Planter_config.json')
    print('= src/configs/Planter_config.json is generated')
    # pass


def config_generator(args, round):
    # reload the config file
    Planter_config = reload_config('src/configs/Planter_config.json')
    # ====================== set dataset in config ======================
    question = 'Which dataset do you want to use?'
    default = 'Iris'
    Planter_config = take_CLI_input(Planter_config, 'data config', 'dataset', question, default,
                                    args.manually_config, check_dir_existance=True, check_available_options=True,
                                    option_address='/src/load_data', option_suffix='_dataset.py')

    # =================== set data feature numbers in config ===================
    question = 'Where is the number of features?'
    default = 4
    Planter_config = take_CLI_input(Planter_config, 'data config', 'number of features', question, default,
                                    args.manually_config, numeric=True)

    # prepare the log dict
    Planter_config['timer log'] = {}
    # dump the config file
    dump_config(Planter_config, 'src/configs/Planter_config.json')

    # =================== include model folder and files ===================
    load_data_file = importlib.util.spec_from_file_location("*", Planter_config['directory config'][
        'work'] + "/src/load_data/" + Planter_config['data config']['dataset'] + "_dataset.py")
    load_data_functions = importlib.util.module_from_spec(load_data_file)
    load_data_file.loader.exec_module(load_data_functions)
    global train_X, train_y, test_X, test_y
    # reload the config file
    Planter_config = reload_config('src/configs/Planter_config.json')
    # =================== load data timer ===================
    Planter_config['timer log']['load data'] = {}
    Planter_config['timer log']['load data']['start'] = time.time()
    # =================== load data timer ===================
    # dump the planter config
    dump_config(Planter_config, 'src/configs/Planter_config.json')
    train_X, train_y, test_X, test_y, used_features = load_data_functions.load_data(
        Planter_config['data config']['number of features'], Planter_config['directory config']['data'])
    # reload the config file
    Planter_config = reload_config('src/configs/Planter_config.json')
    # =================== load data timer ===================
    Planter_config['timer log']['load data']['end'] = time.time()
    # =================== load data timer ===================
    # dump the planter config
    dump_config(Planter_config, 'src/configs/Planter_config.json')
    print('= src/configs/Planter_config.json is generated')
    test_mode = 'n'
    if not args.testing_mode:
        # =================== set testing mode in config ===================
        question = 'Use the testing mode or not?'
        default = 'y'
        Planter_config = take_CLI_input(Planter_config, 'data config', 'testing mode', question, default,
                                        args.manually_config)
        test_mode = Planter_config['data config']['testing mode']
    if args.testing_mode or (test_mode == 'y'):
        print("= Testing model open, at most 20000 input data and 5000 testing data will be used")
        if train_X.shape[0] > 20000:
            train_X = train_X[:20000]
            train_y = train_y[:20000]
        if test_X.shape[0] > 5000:
            test_X = test_X[:5000]
            test_y = test_y[:5000]
    print('= The shape of the dataset - ', 'train x: ', train_X.shape, 'train y: ', train_y.shape, 'test x: ',
          test_X.shape, 'test y: ', test_y.shape)
    # Load data finished

    # Set optimiser config
    # =================== set max number of trees in config ===================
    question = 'What is the maximum number of trees?'
    default = 5
    Planter_config = take_CLI_input(Planter_config, 'optimisation config', 'max number of trees', question, default,
                                    args.manually_config, numeric=True)
    # =================== set max tree depth in config ===================
    question = 'What is the maximum tree depth?'
    default = 10
    Planter_config = take_CLI_input(Planter_config, 'optimisation config', 'max number of depth', question, default,
                                    args.manually_config, numeric=True)
    # =================== set max number of leaf nodes in config ===================
    question = 'What is the maximum number of max leaf nodes?'
    default = 10000
    Planter_config = take_CLI_input(Planter_config, 'optimisation config', 'max max number of leaf nodes', question, default,
                                    args.manually_config, numeric=True)

    if round == 1:
        Planter_config['optimisation config']['opt number of trees'] = Planter_config['optimisation config'][
            'max number of trees']
        Planter_config['optimisation config']['opt number of depth'] = Planter_config['optimisation config'][
            'max number of depth']
        Planter_config['optimisation config']['opt max number of leaf nodes'] = Planter_config['optimisation config'][
            'max max number of leaf nodes']

    # =================== optimiser ===================
    def rf_predict(num_trees, num_depth, max_leaf_nodes):
        rfc = RandomForestClassifier(n_estimators=int(np.round(num_trees)), max_depth=int(np.round(num_depth)),
                                     max_leaf_nodes=int(np.round(max_leaf_nodes)))
        rfc.fit(train_X, train_y)
        sklearn_y_predict = rfc.predict(test_X)
        performance = metrics.f1_score(test_y, sklearn_y_predict, average='macro')

        if Planter_config['optimisation config']['compile result'] == 'n':
            if num_trees >= Planter_config['optimisation config']['opt number of trees'] and num_depth >= \
                    Planter_config['optimisation config']['opt number of depth'] and max_leaf_nodes >= \
                    Planter_config['optimisation config']['opt max number of leaf nodes']:
                performance = 0
        return performance

    rf_opt_obj = BayesianOptimization(
        rf_predict,
        {'num_trees': (2, Planter_config['optimisation config']['max number of trees']),
         'num_depth': (2, Planter_config['optimisation config']['max number of depth']),
         'max_leaf_nodes': (500, Planter_config['optimisation config']['max max number of leaf nodes'])}
    )

    rf_opt_obj.maximize(n_iter=10)
    print("Final result:", rf_opt_obj.max)

    Planter_config['optimisation config']['opt number of trees'] = int(np.round(rf_opt_obj.max['params']['num_trees']))
    Planter_config['optimisation config']['opt number of depth'] = int(np.round(rf_opt_obj.max['params']['num_depth']))
    Planter_config['optimisation config']['opt max number of leaf nodes'] = int(np.round(rf_opt_obj.max['params']['max_leaf_nodes']))
    # dump the planter config
    dump_config(Planter_config, 'src/configs/Planter_config.json')
    print('= src/configs/Planter_config.json is generated')
    write_config()


