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
# Functions: This file serves as the main function of the Planter framework.
#            Please refer to ./Docs/Planter_User_Document.pdf or further information.

# =================== import needed pkgs ===================

import os
import json
import sys
import importlib.util
import platform
import argparse
import warnings
import time
import subprocess as sub
from multiprocessing import *
import signal
warnings.filterwarnings('ignore')

# =================== import Planter src ===================
# funtions
from src.functions.figure_to_ASCII import *
from src.functions.json_encoder import *
from src.functions.project_tree_graph import *
from src.functions.directory_management import *
from src.functions.timer_printer import *
from src.functions.config_modification import *
from src.functions.input_CLI import *


def Planter(iteration = 0):

    # =================== logo and copyright ===================
    if iteration == 0:
        print_logo()

    # =================== set argparse for Planter ===================

    parser = argparse.ArgumentParser(prog="Please use commend '-h' or '--help' for further information",
                                usage='Planter can embed several ML algorithms to programmable network devices',
                                description='It is a on going work, if you find any bugs, please feel free to contact changgang.zheng@eng.ox.ac.uk, it is really important to us. Thank you.',
                                epilog='Play happy with Planter ~')
    parser.add_argument("-m", "--manually_config", help="Manually config Planter or not? If not set, please config the following file <src/config/Planter_config.json>. If set, the Planter will ask you to input all the necessary configs.", action="store_true")
    parser.add_argument("-o", "--auto_optimisation", help="Use auto hyperparameters tunning or not? If set, the Planter will trigger auto optimisation process. Please do not use this mode with other modes, Planter will handle everything.", action="store_true")
    parser.add_argument("-t", "--testing_mode", help="Use testing mode or not? If set, the testing mode will only use at most 20000 input data and 5000 testing data.", action="store_true")
    parser.add_argument("-d", "--draw_project_tree", help="Draw the project tree or not? If set, this mode will output a tree graph of the Planter project.", action="store_true")
    parser.add_argument("-f", "--draw_function_call_graph", help="Draw function calling dependency graph or not, if set, after running Planter, a function calling dependency graph will be generated under <src/logs>.", action="store_true")
    args = parser.parse_args()

    # =================== draw project tree graph ===================
    if args.draw_project_tree:
        print('Tree graph of the Planter project:')
        draw_project_tree_graph(os.getcwd(),0)
        exit_planter = input('- Exit Planter? (default = y) ') or 'y'
        if exit_planter == 'y':
            exit()

    # =========== draw function calling dependency graph ============
    call_graph = False
    try:
        call_graph_time = json.load(open('src/temp/call_graph_time.json', 'r'))
        call_graph_time['end'] = time.time()
        time_gap = call_graph_time['end'] - call_graph_time['start']
        if time_gap > 1:
            call_graph = True
    except Exception as e:
        call_graph = True
    if args.draw_function_call_graph and call_graph:
        from pycallgraph import PyCallGraph
        from pycallgraph.output import GraphvizOutput
        from pycallgraph import Config
        from pycallgraph import GlobbingFilter
        print('Draw function calling dependency graph when running Planter:')
        graphviz = GraphvizOutput()
        graphviz.output_file = 'src/logs/function_calling_dependency_graph.png'
        config = Config()
        call_graph_time = {}
        call_graph_time['start'] = time.time()
        json.dump(call_graph_time, open('src/temp/call_graph_time.json', 'w'), indent=4, cls=NpEncoder)
        with PyCallGraph(output=graphviz, config=config):
            Planter()
        exit()


    # =================== set Planter config ===================
    if args.manually_config and iteration == 0:
        Planter_config = {}
    else:
        Planter_config = reload_config('src/configs/Planter_config.json')

    if iteration == 0:
        print('Please set the following configurations:')
        # ====================== set data directory in config ======================
        question = 'Where is your data folder?'
        default = os.path.abspath(os.path.join(os.getcwd(), "..")) + '/Data'
        Planter_config = take_CLI_input(Planter_config, 'directory config', 'data', question, default,
                                        args.manually_config, check_dir_existance=True)

        # ====================== set working directory in config ======================
        question = 'Where is your Planter folder?'
        default = os.getcwd()
        Planter_config = take_CLI_input(Planter_config, 'directory config', 'work', question, default,
                                        args.manually_config, check_dir_existance=True)
    else:
        args.manually_config = False
    # =================== set auto opt mode config ===================
    if args.auto_optimisation and iteration == 0:
        # ====================== set optimisation mode in config ======================
        question = 'Which optimiser do you use?'
        default = 'Bayesian'
        Planter_config = take_CLI_input(Planter_config, 'optimisation config', 'model', question, default,
                                        args.manually_config, check_dir_existance=True, check_available_options=True,
                                        option_address='/src/optimiser/')
        # ====================== set optimisation mode/type in config ======================
        question = 'Which optimisation model do you use?'
        default = 'RF_only'
        Planter_config = take_CLI_input(Planter_config, 'optimisation config', 'type', question, default,
                                        args.manually_config, check_dir_existance=True, check_available_options=True,
                                        option_address='/src/optimiser/' + Planter_config['optimisation config'][
                                            'model'], option_prefix='Type_')

        # =================== include optimisation folder and files - config generator ===================
        model_path = Planter_config['directory config']['work'] + '/src/optimiser/' + \
                     Planter_config['optimisation config']['model'] + '/Type_' + Planter_config['optimisation config'][
                         'type']

        # =================== include configuration generation file ===================
        # ===================
        print('= Add the following path: ' + model_path)
        sys.path.append(model_path)
        model_main = importlib.util.spec_from_file_location("*", model_path + "/optimiser.py")
        main_functions = importlib.util.module_from_spec(model_main)
        model_main.loader.exec_module(main_functions)

        Planter_config['optimisation config']['compile result'] = "None"
        # dump the config file
        dump_config(Planter_config, 'src/configs/Planter_config.json')
        round = 0
        while True:
            round += 1
            # call the function to find best paraemters and generate the config file
            main_functions.config_generator(args, round)
            # call Plantrer to verify the generated configs
            print('= Begin varifcation for the generated configs. Rounds', round)
            args.manually_config = False
            Planter(round)
            # reload the config file
            Planter_config = reload_config('src/configs/Planter_config.json')
            if Planter_config['optimisation config']['compile result'] == 'y':
                print('= Verification seccess. Data plane and control plane codes are generated with best hyperparameters.')
                break
            else:
                print('= Verification fales. Regenerate configs with higher constrained configs')
        exit()
    # =================== auto config mode config and operations finished ===================
    # print('= args:', args)
    # ====================== set machine learning model in config ======================
    question = 'Which model do you want to plant?'
    default = 'DT'
    Planter_config = take_CLI_input(Planter_config, 'model config', 'model', question, default,
                                    args.manually_config, check_dir_existance=True, check_available_options=True,
                                    option_address='/src/models')

    # ====================== set model type in config ======================
    question = 'Which type (variation) of model do you want to plant?'
    default = '1'
    Planter_config = take_CLI_input(Planter_config, 'model config', 'type', question, default,
                                    args.manually_config, check_dir_existance=True, check_available_options=True,
                                    option_address='/src/models/' + Planter_config['model config']['model'],
                                    option_prefix='Type_')

    # ====================== set dataset in config ======================
    question = 'Which dataset do you want to use?'
    default = 'UNSW_5_tuple'
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
    load_data_file = importlib.util.spec_from_file_location("*", Planter_config['directory config']['work']+"/src/load_data/"+Planter_config['data config']['dataset']+"_dataset.py")
    load_data_functions = importlib.util.module_from_spec(load_data_file)
    load_data_file.loader.exec_module(load_data_functions)
    global test_X, test_y
    # reload the config file
    Planter_config = reload_config('src/configs/Planter_config.json')
    # =================== load data timer ===================
    Planter_config['timer log']['load data'] = {}
    Planter_config['timer log']['load data']['start'] = time.time()
    # =================== load data timer ===================
    # dump the planter config
    dump_config(Planter_config, 'src/configs/Planter_config.json')
    train_X, train_y, test_X, test_y, used_features = load_data_functions.load_data(Planter_config['data config']['number of features'], Planter_config['directory config']['data'])
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
    if args.testing_mode or (test_mode=='y'):
        print("= Testing model open, at most 20000 input data and 5000 testing data will be used")
        if train_X.shape[0]>20000:
            train_X = train_X[:20000]
            train_y = train_y[:20000]
        if test_X.shape[0]>5000:
            test_X = test_X[:5000]
            test_y = test_y[:5000]
    print('= The shape of the dataset - ', 'train x: ',train_X.shape,  'train y: ',train_y.shape, 'test x: ', test_X.shape, 'test y: ', test_y.shape)
    # dump the planter config
    dump_config(Planter_config, 'src/configs/Planter_config.json')
    print('= src/configs/Planter_config.json is generated')
    # =================== include model folder and files - table generator and table tester ===================
    model_path = Planter_config['directory config']['work']+ '/src/models/' + Planter_config['model config']['model'] + '/Type_' + Planter_config['model config']['type']
    print('= Add the following path: '+model_path)
    sys.path.append(model_path)
    model_main = importlib.util.spec_from_file_location("*", model_path+"/table_generator.py")
    main_functions = importlib.util.module_from_spec(model_main)
    model_main.loader.exec_module(main_functions)
    sklearn_test_y = main_functions.run_model(train_X, train_y, test_X, test_y, used_features)
    # reload the config file
    Planter_config = reload_config('src/configs/Planter_config.json')
    # =================== set testing table or not in config ===================
    question = 'Test the table or not?'
    default = 'y'
    Planter_config = take_CLI_input(Planter_config, 'model config', 'test table', question, default, args.manually_config)
    if Planter_config['model config']['test table'] == 'y':

        # =================== python-based test timer ===================
        Planter_config['timer log']['python-based test'] = {}
        Planter_config['timer log']['python-based test']['start'] = time.time()
        # =================== python-based test timer ===================
        main_functions.test_tables(sklearn_test_y, test_X, test_y)
        # =================== python-based test timer ===================
        Planter_config['timer log']['python-based test']['end'] = time.time()
        # =================== python-based test timer ===================

    # dump the planter config
    dump_config(Planter_config, 'src/configs/Planter_config.json')
    print('= src/configs/Planter_config.json is generated')
    try:
        main_functions.resource_prediction()
    except Exception as e:
        pass

    # =================== select the target device ===================
    # reload the config file
    Planter_config = reload_config('src/configs/Planter_config.json')

    # ====================== set architecture type in config ======================
    question = 'Which architecture do you use?'
    default = 'tna'
    Planter_config = take_CLI_input(Planter_config, 'target config', 'architecture', question, default,
                                    args.manually_config, check_dir_existance=True, check_available_options=True,
                                    option_address='/src/architectures/')

    # ====================== set use case in config ======================
    question = 'Which is the use case?'
    default = 'performance'
    Planter_config = take_CLI_input(Planter_config, 'target config', 'use case', question, default,
                                    args.manually_config, check_dir_existance=True, check_available_options=True,
                                    option_address='/src/use_cases/')

    dump_config(Planter_config, 'src/configs/Planter_config.json')

    # =================== include model generate p4 file ===================
    # ===================
    common_p4_path = Planter_config['directory config']['work']+'/src/use_cases/'+Planter_config['target config']['use case']
    print('= Add the following path: '+common_p4_path)
    sys.path.append(common_p4_path)
    p4_generator_path = Planter_config['directory config']['work'] + '/src/architectures/' + Planter_config['target config']['architecture']
    print('= Add the following path: ' + p4_generator_path)
    # ===================
    sys.path.append(p4_generator_path)
    p4_generator_main = importlib.util.spec_from_file_location("*", Planter_config['directory config']['work']+"/src/architectures/"+Planter_config['target config']['architecture']+"/p4_generator.py")
    p4_generator_functions = importlib.util.module_from_spec(p4_generator_main)
    p4_generator_main.loader.exec_module(p4_generator_functions)
    p4_generator_functions.main()

    # =================== select the target device ===================
    # reload the config file
    Planter_config = reload_config('src/configs/Planter_config.json')

    # ====================== set target device in config ======================
    question = 'What is the target device?'
    default = 'Tofino'
    Planter_config = take_CLI_input(Planter_config, 'target config', 'device', question, default,
                                    args.manually_config, check_dir_existance=True, check_available_options=True,
                                    option_address='/src/targets/')

    # ====================== set target testing mode in config ======================
    question = 'Which type of mode do you want to choose?'
    default = 'software'
    Planter_config = take_CLI_input(Planter_config, 'target config', 'type', question, default,
                                    args.manually_config, check_dir_existance=True, check_available_options=True,
                                    option_address='/src/targets/'+Planter_config['target config']['device'])

    dump_config(Planter_config, 'src/configs/Planter_config.json')
    print('= Dump the targets info to src/configs/Planter_config.json')

    # =================== include model compile load and test module ===================
    if_using_subprocess = False
    test_model_path = Planter_config['directory config']['work']+'/src/targets/'+Planter_config['target config']['device'] +'/'+Planter_config['target config']['type']
    print('= Add the following path: '+test_model_path)
    sys.path.append(test_model_path)
    run_model_main = importlib.util.spec_from_file_location("*", test_model_path+"/run_model.py")
    run_model_functions = importlib.util.module_from_spec(run_model_main)
    run_model_main.loader.exec_module(run_model_functions)
    processes, if_using_subprocess = run_model_functions.main(if_using_subprocess)

    test_model_main = importlib.util.spec_from_file_location("*", test_model_path+"/test_model.py")
    test_model_functions = importlib.util.module_from_spec(test_model_main)
    test_model_main.loader.exec_module(test_model_functions)
    processes, if_using_subprocess = test_model_functions.main(sklearn_test_y, test_X, test_y, processes, if_using_subprocess)

    if if_using_subprocess:
        print('Join all subprocess together ...')
        try:
            for p in processes:
                p.join()
        except Exception as e:
            print(str(e))

    print_timer()





if __name__ == "__main__":
    try:
        Planter()
    except KeyboardInterrupt:
        print("\n==============================================================================================\n"
              "=                                      Exiting Planter                                       =\n"
              "==============================================================================================")
        print_timer()

