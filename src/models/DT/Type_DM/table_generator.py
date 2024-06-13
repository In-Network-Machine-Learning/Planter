# THIS FILE IS PART OF Planter PROJECT
# Planter.py - The core part of the Planter library
#
# THIS PROGRAM IS FREE SOFTWARE TOOL, WHICH MAPS MACHINE LEARNING ALGORITHMS TO DATA PLANE, IS LICENSED UNDER Apache-2.0
# YOU SHOULD HAVE RECEIVED A COPY OF THE LICENSE, IF NOT, PLEASE CONTACT THE FOLLOWING E-MAIL ADDRESSES
#
# Copyright (c) 2019 Jong-Hyouk Lee and Kamal Singh
# If you want to use this type of model,
# please cite their work 'SwitchTree: In-network Computing and Traffic Analyses with Random Forests'
# Copyright (c) 2020-2021 Changgang Zheng
# Copyright (c) Computing Infrastructure Lab, Department of Engineering Science, University of Oxford
# E-mail: changgang.zheng@eng.ox.ac.uk or changgangzheng@qq.com
#
# Functions: This file is responsible for training, algorithm mapping, and software testing of the ML model.
#            Please refer to ./Docs/Planter_User_Document.pdf or further information.


from sklearn.preprocessing import LabelEncoder
from sklearn.tree import _tree
from sklearn.ensemble import RandomForestClassifier
import time
# from create_files import *
import math
import re
import json
from sklearn.metrics import *
from src.functions.Range_to_TCAM_Top_Down import *
from src.functions.json_encoder import *
import copy
import os

from sklearn import tree
from sklearn.tree import export_text
from sklearn.tree import _tree
from sklearn.tree import DecisionTreeClassifier

# i_tree = 0
#
# global_id = 0


def export_p4(decision_tree, fname):
    tree_ = decision_tree.tree_
    class_names = decision_tree.classes_
    right_child_fmt = "{} {} <= {}\n"
    left_child_fmt = "{} {} >  {}\n"
    truncation_fmt = "{} {}\n"
    feature_names_ = ["{}".format(i) for i in tree_.feature]
    export_text.report = ""
    max_depth = 10
    spacing = 3
    decimals = 2
    show_weights = False

    if isinstance(decision_tree, DecisionTreeClassifier):
        value_fmt = "{}{} weights: {}\n"
        if not show_weights:
            value_fmt = "{}{}{}\n"
    else:
        value_fmt = "{}{} value: {}\n"

    def _add_leaf(value, class_name, indent, prevfeature, result, depth, previous_id, fname):
        global global_id
        global i_tree
        global Exact_Table

        current_id = global_id

        val = ''
        is_classification = isinstance(decision_tree,
                                       DecisionTreeClassifier)
        if show_weights or not is_classification:
            val = ["{1:.{0}f}, ".format(decimals, v) for v in value]
            val = '[' + ''.join(val)[:-2] + ']'
        if is_classification:
            val += ' class: ' + str(class_name)
        export_text.report += value_fmt.format(indent, '', val)
        # print("table_add MyIngress.level_", i_tree, "_", depth, " ", "MyIngress.SetClass", i_tree, " ", previous_id,
        #       " ", prevfeature, " ", result, " ", "=>", " ", current_id, " ", int(float(class_name)), sep="")
        with open(fname, 'a') as command:
            command.write("table_add SwitchIngress.level_"+str(i_tree)+ "_"+str(depth)+" SwitchIngress.SetClass"+str(i_tree)+
                          " "+str(previous_id)+ " "+str(prevfeature)+ " "+str(result)+ " => "+str(current_id)+ " "+
                          str(int(float(class_name))) +"\n")

        Exact_Table['node table'][Exact_Table['node table counter']] = ["SetClass"+str(i_tree),
                                                                        "level_" + str(i_tree) + "_" + str(depth),
                                                                        str(previous_id), str(prevfeature),
                                                                        str(result), str(current_id),
                                                                        str(int(float(class_name)))]
        Exact_Table['node table counter'] += 1





    def print_tree_recurse(node, depth, prevfeature, result, previous_id, fname):
        indent = ("|" + (" " * spacing)) * depth
        indent = indent[:-spacing] + "-" * spacing
        global global_id
        global i_tree
        global Exact_Table

        global_id = global_id + 1
        current_id = global_id

        value = None
        if tree_.n_outputs == 1:
            value = tree_.value[node][0]
        else:
            value = tree_.value[node].T[0]
        class_name = np.argmax(value)

        if (tree_.n_classes[0] != 1 and
                tree_.n_outputs == 1):
            class_name = class_names[class_name]

        if depth <= max_depth + 1:
            info_fmt = ""
            info_fmt_left = info_fmt
            info_fmt_right = info_fmt

            if tree_.feature[node] != _tree.TREE_UNDEFINED:
                name = feature_names_[node]
                threshold = tree_.threshold[node]
                threshold = "{1:.{0}f}".format(decimals, threshold)
                export_text.report += right_child_fmt.format(indent,
                                                             name,
                                                             threshold)
                export_text.report += info_fmt_left
                with open(fname, 'a') as command:
                    command.write("table_add SwitchIngress.level_"+str(i_tree)+ "_"+str(depth)+ " SwitchIngress.CheckFeature "+
                                  str(previous_id) + " " + str(prevfeature) + " "+str(result) + " => " + str(current_id) +
                                  " " + str(name) + " " + str(int(float(threshold)))+"\n")
                global first_entry
                global entry_info
                global Exact_Table

                Exact_Table['node table'][Exact_Table['node table counter']] = ["CheckFeature", "level_"+str(i_tree)+ "_"+str(depth),
                                                                                str(previous_id), str(prevfeature),
                                                                                str(result), str(current_id), str(name) ,
                                                                                str(int(float(threshold)))]
                Exact_Table['node table counter'] += 1

                if first_entry:
                    first_entry = False
                    entry_info += [[previous_id, prevfeature, result]]

                print_tree_recurse(tree_.children_left[node], depth + 1, name, 1, current_id, fname)

                export_text.report += left_child_fmt.format(indent,
                                                            name,
                                                            threshold)
                export_text.report += info_fmt_right
                #     print("level", depth, "checkfeature", prevfeature, result, "=>", name, threshold)

                print_tree_recurse(tree_.children_right[node], depth + 1, name, 0, current_id, fname)
            else:  # leaf
                _add_leaf(value, class_name, indent, prevfeature, result, depth, previous_id, fname)
        else:
            subtree_depth = _compute_depth(tree_, node)
            if subtree_depth == 1:
                _add_leaf(value, class_name, indent, prevfeature, result, depth, previous_id, fname)
            else:
                trunc_report = 'truncated branch of depth %d' % subtree_depth
                export_text.report += truncation_fmt.format(indent,
                                                            trunc_report)

    print_tree_recurse(0, 1, 0, 1, global_id, fname)



def votes_to_class(tree_num, vote_list, num_trees, num_classes, g_table, num):
    if tree_num  == num_trees:
        vote = np.zeros(num_classes).tolist()
        for i in range(num_trees):
            vote[vote_list[i]] += 1
        g_table['votes to class'][num] = {}
        for t in range(len(vote_list)):
            g_table['votes to class'][num]['t'+str(t)+' vote'] = vote_list[t]
        g_table['votes to class'][num]['class'] = vote.index(np.max(vote))
        num += 1
        return g_table, num
    else:
        for value in range(num_classes):
            vote_list[tree_num] = value
            tree_num += 1
            g_table, num = votes_to_class(tree_num, vote_list, num_trees, num_classes, g_table, num)
            tree_num -= 1
    return g_table, num


def get_lineage(tree, feature_names, file):
    left = tree.tree_.children_left
    right = tree.tree_.children_right
    threshold = tree.tree_.threshold
    features = [feature_names[i] for i in tree.tree_.feature]
    value = tree.tree_.value
    le = '<='
    g = '>'
    # get ids of child nodes
    idx = np.argwhere(left == -1)[:, 0]
    # traverse the tree and get the node information
    def recurse(left, right, child, lineage=None):
        if lineage is None:
            lineage = [child]
        if child in left:
            parent = np.where(left == child)[0].item()
            split = 'l'
        else:
            parent = np.where(right == child)[0].item()
            split = 'r'
        lineage.append((parent, split, threshold[parent], features[parent]))
        if parent == 0:
            lineage.reverse()
            return lineage
        else:
            return recurse(left, right, parent, lineage)
    for j, child in enumerate(idx):
        clause = ' when '
        for node in recurse(left, right, child):
            if len(str(node)) < 3:
                continue
            i = node
            if not isinstance(i, tuple):
                continue
            if i[1] == 'l':
                sign = le
            else:
                sign = g
            clause = clause + i[3] + sign + str(i[2]) + ' and '
        # wirte the node information into text file
        a = list(value[node][0])
        ind = a.index(np.max(a))
        clause = clause[:-4] + ' then ' + str(ind)
        file.write(clause)
        file.write(";\n")

def run_model(train_X, train_y, test_X, test_y, used_features):
    config_file = 'src/configs/Planter_config.json'

    Planter_config = json.load(open(config_file, 'r'))

    Planter_config['model config']['number of trees'] = 1
    Planter_config['model config']['number of depth'] = int(input('- Number of depth? (default = 4) ') or '4')
    Planter_config['model config']['max number of leaf nodes'] = int(input('- Number of leaf nodes? (default = 1000) ') or '1000')
    Planter_config['model config']['number of classes'] = int(np.max(train_y) + 1)

    num_features = Planter_config['data config']['number of features']
    num_classes = Planter_config['model config']['number of classes']
    num_depth = Planter_config['model config']['number of depth']
    num_trees = Planter_config['model config']['number of trees']
    max_leaf_nodes = Planter_config['model config']['max number of leaf nodes']

    feature_names = []
    for i, f in enumerate(used_features):
        train_X.rename(columns={f: "f" + str(i)}, inplace=True)
        test_X.rename(columns={f: "f" + str(i)}, inplace=True)
        feature_names += ["f" + str(i)]

    feature_max = []
    for i in feature_names:
        t_t = [test_X[[i]].max()[0], train_X[[i]].max()[0]]
        feature_max += [np.max(t_t)+1]

    # =================== train model timer ===================
    Planter_config['timer log']['train model'] = {}
    Planter_config['timer log']['train model']['start'] = time.time()
    # =================== train model timer ===================

    # Decision Tree
    model = DecisionTreeClassifier(max_depth=num_depth, max_leaf_nodes=max_leaf_nodes)
    model.fit(train_X, train_y)
    sklearn_y_predict = model.predict(test_X)

    result = classification_report(test_y, sklearn_y_predict, digits= 4)
    print('\n',result)

    # =================== train model timer ===================
    Planter_config['timer log']['train model']['end'] = time.time()
    # =================== train model timer ===================

    # =================== convert model timer ===================
    Planter_config['timer log']['convert model'] = {}
    Planter_config['timer log']['convert model']['start'] = time.time()
    # =================== convert model timer ===================

    # exit()
    log_file = 'src/logs/log.json'
    if os.path.exists(log_file):
        log_dict = json.load(open(log_file, 'r'))
    else:
        log_dict = {}

    if ( "num_feature: "+str(num_features)) not in log_dict:
        log_dict["num_feature: "+str(num_features)] = {}
    if ( "num_tree: "+str(num_trees)) not in log_dict["num_feature: "+str(num_features)]:
        log_dict["num_feature: "+str(num_features)]["num_tree: "+str(num_trees)] = {}
    if ( "num_depth: "+str(num_depth)) not in log_dict["num_feature: "+str(num_features)]["num_tree: "+str(num_trees)]:
        log_dict["num_feature: "+str(num_features)]["num_tree: "+str(num_trees)]["num_depth: "+ str(num_depth)]= {}
    log_dict["num_feature: " + str(num_features)][ "num_tree: " + str(num_trees)]["num_depth: " + str(num_depth)]["classification_report"] = result
    log_dict["num_feature: " + str(num_features)][ "num_tree: " + str(num_trees)]["num_depth: " + str(num_depth)]["max number of leaf nodes"] =max_leaf_nodes
    json.dump(log_dict, open(log_file, 'w'), indent=4)
    print ('Classification results are downloaded to log as', log_file)


    fname =  Planter_config['directory config']['work']+'/Tables/Depth_Based_Table.txt'
    # refresh the command (Table) file
    with open(fname, 'w') as command:
        command.write('')

    global global_id
    global i_tree
    global first_entry
    global entry_info
    global Exact_Table

    i_tree = 0
    global_id = 0
    entry_info = []
    Exact_Table = {}
    Exact_Table['node table'] = {}
    Exact_Table['node table counter'] = 0

    estimator = model
    idx = 0
    with open('./src/temp/tree' + str(idx) + '.txt', 'w') as f:
        f.write('')
    with open('./src/temp/tree' + str(idx) + '.txt', 'a') as f:
        get_lineage(estimator, feature_names, f)
    first_entry = True
    i_tree = i_tree + 1
    export_p4(estimator, fname)
    # print(entry_info)

    g_table = {}
    print("Generating vote to class table...", end="")
    g_table['votes to class'] = {}
    g_table, _ = votes_to_class(0, np.zeros(num_trees).tolist(), num_trees, num_classes, g_table, 0)
    print('Done')

    g_table['decision'] = g_table['votes to class']

    collect_class = []
    for idx in g_table['decision']:
        collect_class += [g_table['decision'][idx]['class']]
    default_class = max(collect_class, key=collect_class.count)

    code_table_size = 0
    Exact_Table['decision'] = {}
    for idx in g_table['decision']:
        if g_table['decision'][idx]['class'] != default_class:
            Exact_Table['decision'][code_table_size] = g_table['decision'][idx]
            code_table_size += 1

    # =================== convert model timer ===================
    Planter_config['timer log']['convert model']['end'] = time.time()
    # =================== convert model timer ===================

    json.dump(Exact_Table, open('Tables/Exact_Table.json', 'w'), indent=4)
    print('Depth_Based_Table.txt and Exact_Table.json is generated')





    Planter_config['p4 config'] = {}
    Planter_config['p4 config']["model"] = "RF"
    Planter_config['p4 config']["number of features"] = num_features
    Planter_config['p4 config']["number of classes"] =  num_classes
    Planter_config['p4 config']["number of trees"] =  num_trees
    Planter_config['p4 config']["number of depth"] = num_depth
    Planter_config['p4 config']['table name'] = 'Exact_Table.json'
    Planter_config['p4 config']["decision table size"] = len(Exact_Table['decision'].keys())
    Planter_config['p4 config']["first entry info"] = entry_info
    Planter_config['p4 config']["default label"] = default_class

    Planter_config['test config'] = {}
    Planter_config['test config']['type of test'] = 'classification'

    json.dump(Planter_config , open(Planter_config['directory config']['work']+'/src/configs/Planter_config.json', 'w'), indent=4, cls=NpEncoder)
    print(Planter_config['directory config']['work']+'/src/configs/Planter_config.json is generated')

    return sklearn_y_predict.tolist()

def test_tables(sklearn_test_y, test_X, test_y):
    print('The python simulation test does not support this model, please do the following emulation test on the software switch.')


def resource_prediction():

    config_file = './src/configs/Planter_config.json'
    Planter_config = json.load(open(config_file, 'r'))

    print('Exact match entries: ',Planter_config['p4 config']["decision table size"]+1024*Planter_config['p4 config']["number of depth"])


if __name__ == '__main__':
    print('there are many dependencies, directly run is not currently supported')
