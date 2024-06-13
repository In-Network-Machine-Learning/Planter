# THIS FILE IS PART OF Planter PROJECT
# Planter.py - The core part of the Planter library
#
# THIS PROGRAM IS FREE SOFTWARE TOOL, WHICH MAPS MACHINE LEARNING ALGORITHMS TO DATA PLANE, IS LICENSED UNDER Apache-2.0
# YOU SHOULD HAVE RECEIVED A COPY OF WTFPL LICENSE, IF NOT, PLEASE CONTACT THE FOLLOWING E-MAIL ADDRESSES
#
# Copyright (c) 2020-2021 Changgang Zheng
# Copyright (c) Computing Infrastructure Lab, Department of Engineering Science, University of Oxford
# E-mail: changgang.zheng@eng.ox.ac.uk or changgangzheng@qq.com
#
# Functions: This file is responsible for training, algorithm mapping, and software testing of the ML model.
#            Please refer to ./Docs/Planter_User_Document.pdf or further information.

import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
import math
import json
import copy
from sklearn.metrics import *
import re
from src.functions.json_encoder import *
from src.functions.Range_to_TCAM_Top_Down import *
from src.functions.Range_to_LPM import *
from src.functions.json_encoder import *
from src.functions.Muti_Exact_to_LPM import *

def get_lineage(tree, feature_names, file):
    left = tree.tree_.children_left
    right = tree.tree_.children_right
    threshold = tree.tree_.threshold
    features = [feature_names[i] for i in tree.tree_.feature]
    value = tree.tree_.value
    n_node_samples = tree.tree_.n_node_samples
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
        # print(node)
        ind = n_node_samples[node]
        clause = clause[:-4] + ' then ' + str(ind)
        file.write(clause)
        file.write(";\n")

def print_tree(tree, feature_names):
    tree_ = tree.tree_
    feature_name = [
        feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
        for i in tree_.feature
    ]
    # print('feature_name:', feature_name)
    print("def tree({}):".format(", ".join(feature_names)))
    share = {}
    def recurse(node, depth, share):
        indent = "  " * depth
        if tree_.feature[node] != _tree.TREE_UNDEFINED:
            name = feature_name[node]
            share[name] = {}
            threshold = tree_.threshold[node]
            print("{}if {} <= {}:".format(indent, name, threshold))
            recurse(tree_.children_left[node], depth + 1, share)
            print("{}else:  # if {} > {}".format(indent, name, threshold))
            recurse(tree_.children_right[node], depth + 1, share)
        else:
            print("{}return {}".format(indent, tree_.value[node]))
    recurse(0, 1, share)




def ten_to_bin(num, count):
    num = bin(int(num)).lstrip('0b')
    if len(num) != count:
        cont = count - len(num)
        num = cont * '0' + num
    return num




def find_feature_split(model, tree_index, num_features):
    feature_names = []
    feature_split = {}
    for l in range(num_features):
        feature_split["feature "+str(l)] = []
        feature_names += ["f" + chr(ord('A') + l)]
    threshold = model.tree_.threshold
    features = [feature_names[i] for i in model.tree_.feature]
    for i, fe in enumerate(features):
        for l in range(num_features):
            if l == 0:
                if fe == feature_names[l]:
                    feature_split["feature "+str(l)].append(threshold[i])
                    continue
            if fe == feature_names[l]:
                if threshold[i] != -2.0:
                    feature_split["feature "+str(l)].append(threshold[i])
                continue
    for l in range(num_features):
        feature_split["feature "+str(l)] = [int(np.floor(i)) for i in feature_split["feature "+str(l)]]
        feature_split["feature "+str(l)].sort()
    tree = open('src/temp/tree'+str(tree_index)+'.txt', "w+")
    for l in range(num_features):
        tree.write(str(feature_names[l]) + " = ")
        tree.write(str(feature_split["feature "+str(l)]))
        tree.write(";\n")
    # print_tree(model, feature_names)
    get_lineage(model, feature_names, tree)
    tree.close()
    action = [0, 1]
    textfile = 'src/temp/tree'+str(tree_index)+'.txt'
    for f in range(num_features):
        feature_split['feature ' + str(f)] = sorted(list(set(feature_split['feature ' + str(f)])))
    return textfile, feature_split

def generate_feature_tables(split, num_features,feature_max, table):
    for i in range(num_features):
        table["feature "+str(i)] = {}
        count_code = 0
        nife = sorted(split["feature "+str(i)])
        for j in range(feature_max[i]+1):
            if nife !=[] :
                if len(nife) > count_code:
                    if j-1 == nife[count_code]:
                        count_code+=1
            table["feature " + str(i)][j] = count_code
    return table


def find_classification(textfile, feature_split, num_features):
    fea = []
    sign = []
    num = []
    f = open(textfile, 'r')
    feature_n = {}
    text = r"("
    for l in range(num_features):
        feature_n[l] = []
        if l==0:
            text += "f"+chr(ord('A')+l)
        else:
            text += "|f" + chr(ord('A')+l)
    text += ")"
    for line in f:
        n = re.findall(r"when", line)
        if n:
            fea.append(re.findall(text, line))
            sign.append(re.findall(r"(<=|>)", line))
            num.append(re.findall(r"\d+\.?\d*", line))
    f.close()
    classfication = []
    featuren = {}
    for i in range(len(fea)):
        num_nodes = 0
        for l in range(num_features):
            featuren[l] = [k for k in range(len(feature_split["feature "+str(l)]) + 1)]
        for j, feature in enumerate(fea[i]):
            for l in range(num_features):
                if feature == "f"+chr(ord('A')+l):
                    sig = sign[i][j]
                    thres = int(float(num[i][j]))
                    id = feature_split["feature "+str(l)].index(thres)
                    num_nodes += 1
                    if sig == '<=':
                        while id < len(feature_split["feature "+str(l)]):
                            if id + 1 in featuren[l]:
                                featuren[l].remove(id + 1)
                            id = id + 1
                    else:
                        while id >= 0:
                            if id in featuren[l]:
                                featuren[l].remove(id)
                            id = id - 1
                    continue
        for l in range(num_features):
            feature_n[l].append(featuren[l])
        a = len(num[i])
        classfication.append([num_nodes, int(num[i][a - 1])])

    return feature_n, classfication


def find_path_for_leaf_nodes(feature_n, classfication, num_features):
    path_to_leaf = {}
    for i in range(len(classfication)):
        path_to_leaf["path "+str(i)] = {}
        path_to_leaf["path " + str(i)]["leaf"] = classfication[i]
        for j in range(num_features):
            path_to_leaf["path " + str(i)]["feature "+str(j)] = feature_n[j][i]
    return path_to_leaf




def generate_code_table_for_path(table, leaf_path, code_dict, feature_num, num_features, count):
    if feature_num == num_features:
        table['code to vote'][count] = {}
        for f in range(num_features):
            table['code to vote'][count]['f'+str(f)+' code'] = code_dict['feature ' + str(f)]
        table['code to vote'][count]['leaf'] = leaf_path['leaf']
        count += 1
        return table, count
    else:
        for value in leaf_path['feature '+str(feature_num)]:
            code_dict['feature ' + str(feature_num)] = value
            feature_num += 1
            table, count = generate_code_table_for_path(table, leaf_path, code_dict, feature_num, num_features, count)
            feature_num -= 1
    return table, count

def generate_code_table(table, path_to_leaf, num_features):
    table['code to vote'] = {}
    count = 0
    for p in path_to_leaf:
        table, count = generate_code_table_for_path(table, path_to_leaf[p], {}, 0, num_features, count)
    return table

def generate_table(model, tree_index, num_features, g_table, feature_max, leaf_info):
    textfile, feature_split = find_feature_split(model, tree_index, num_features)
    
    g_table[tree_index] = {}
    g_table[tree_index] = generate_feature_tables(feature_split, num_features, feature_max, g_table[tree_index])
    
    feature_n, classfication = find_classification(textfile, feature_split , num_features)
    path_to_leaf = find_path_for_leaf_nodes(feature_n, classfication, num_features)
    code_width_for_feature = np.zeros(num_features)
    for i in range(num_features):
        code_width_for_feature[i] = int(np.ceil(math.log(g_table[tree_index]['feature ' + str(i)][np.max(list(g_table[tree_index]['feature ' + str(i)].keys()))]+1,2))) or 1
    g_table[tree_index] = generate_code_table(g_table[tree_index], path_to_leaf, num_features)
    
    # print(classfication)
    print('\rThe table for Tree: {} is generated'.format(tree_index), end="")
    leaf_info['tree '+str(tree_index)]= np.unique(classfication, axis=0)
    return g_table, leaf_info

def _average_path_length(n_samples_leaf):
    """
    The average path length in a n_samples iTree, which is equal to
    the average path length of an unsuccessful BST search since the
    latter has the same structure as an isolation tree.
    Parameters
    ----------
    n_samples_leaf : array-like of shape (n_samples,)
        The number of training samples in each test sample leaf, for
        each estimators.

    Returns
    -------
    average_path_length : ndarray of shape (n_samples,)
    """

    # n_samples_leaf = check_array(n_samples_leaf, ensure_2d=False)

    n_samples_leaf_shape = n_samples_leaf.shape
    n_samples_leaf = n_samples_leaf.reshape((1, -1))
    average_path_length = np.zeros(n_samples_leaf.shape)

    mask_1 = n_samples_leaf <= 1
    mask_2 = n_samples_leaf == 2
    not_mask = ~np.logical_or(mask_1, mask_2)

    average_path_length[mask_1] = 0.
    average_path_length[mask_2] = 1.
    average_path_length[not_mask] = (
        2.0 * (np.log(n_samples_leaf[not_mask] - 1.0) + np.euler_gamma)
        - 2.0 * (n_samples_leaf[not_mask] - 1.0) / n_samples_leaf[not_mask]
    )

    return average_path_length.reshape(n_samples_leaf_shape)

def complex_list_idx(target_list, component):
    for i, x in enumerate(target_list):
        if np.all(x==component):
            # print(i)
            return i


def votes_to_class(tree_num, vote_list, num_trees, num_classes, g_table, num, leaf_info, path_len_threshold):
    if tree_num  == num_trees:
        vote = 0
        for t in range(num_trees):
            vote += (leaf_info["tree "+str(t)][vote_list[t]][0] + _average_path_length(leaf_info["tree "+str(t)][vote_list[t]][1]))
        # if vote.index(np.max(vote))== 0:
        # if True :
        g_table['votes to class'][num] = {}
        for t in range(len(vote_list)):
            g_table['votes to class'][num]['t'+str(t)+' vote'] = leaf_info["tree "+str(t)][vote_list[t]]
            # g_table['votes to class'][num]['t'+str(t)+' vote'] = vote_list[t]
        if vote >= path_len_threshold*num_trees:
            g_table['votes to class'][num]['class'] = 0
        else:
            g_table['votes to class'][num]['class'] = 1
        # g_table['votes to class'][num]['class'] = vote
        # print(g_table['votes to class'][num])
        num += 1
        return g_table, num
    else:
        for value in range(len(leaf_info["tree "+str(tree_num)])):
            vote_list[tree_num] = value
            tree_num += 1
            g_table, num = votes_to_class(tree_num, vote_list, num_trees, num_classes, g_table, num, leaf_info, path_len_threshold)
            tree_num -= 1
    return g_table, num



def run_model(train_X, train_y, test_X, test_y, used_features):
    config_file = 'src/configs/Planter_config.json'

    Planter_config = json.load(open(config_file, 'r'))

    Planter_config['model config']['number of trees'] = int(input('- Number of trees? (default = 5) ') or '5')
    Planter_config['model config']['number of samples'] = int(input('- Number of samples? (default = 128) ') or '128')
    Planter_config['model config']['number of classes'] = int(np.max(train_y) + 1)
    num_features = Planter_config['data config']['number of features']
    num_samples = Planter_config['model config']['number of samples']
    num_classes = Planter_config['model config']['number of classes']
    # num_depth = Planter_config['model config']['number of depth']
    num_trees = Planter_config['model config']['number of trees']
    path_len_threshold = (2 * (np.log(num_samples - 1) + np.euler_gamma) - (2 * (num_samples - 1) / num_samples)) * (-math.log(0.5, 2))
    print("The threshold of path length is %.2f" % path_len_threshold)
    # max_leaf_nodes = Planter_config['model config']['max number of leaf nodes']

    feature_names = []
    for i, f in enumerate(used_features):
        train_X.rename(columns={f: "f" + str(i)}, inplace=True)
        test_X.rename(columns={f: "f" + str(i)}, inplace=True)
        feature_names += ["f" + str(i)]

    feature_max = []
    for i in feature_names:
        t_t = [test_X[[i]].max()[0], train_X[[i]].max()[0]]
        feature_max += [np.max(t_t)+1]




    rng = np.random.RandomState(42)



    # fit the model
    clf = IsolationForest( n_estimators= num_trees, max_samples=num_samples, random_state=rng)
    clf.fit(train_X)

    clf.decision_function(train_X)

    y_pred_test = clf.predict(test_X)
    sklearn_y_predict = copy.deepcopy(y_pred_test)

    for i in range(len(y_pred_test)):
        if y_pred_test[i] == -1:
            sklearn_y_predict[i] = 1
        if y_pred_test[i] == 1:
            sklearn_y_predict[i] = 0

    result = classification_report(test_y, sklearn_y_predict, digits=4)
    print('\n', result)

    g_table = {}
    leaf_info = {}
    leaf_info['max value'] = 0
    leaf_info['min value'] = 0
    for idx, estimator in enumerate(clf.estimators_):
        g_table, leaf_info = generate_table(estimator, idx, num_features, g_table, feature_max, leaf_info)


    g_table['votes to class'] = {}
    print("\nGenerating vote to class table...", end="")
    g_table, _ = votes_to_class(0, np.zeros(num_trees).tolist(), num_trees, num_classes, g_table, 0, leaf_info, path_len_threshold)
    print('Done')

    for t in range(num_trees):
        leaf_info['tree ' + str(t)] = list(leaf_info['tree ' + str(t)])
        for i, x in enumerate(leaf_info['tree ' + str(t)]):
            leaf_info['tree ' + str(t)][i] = str(list(x))

    for t in range(num_trees):
        for k in g_table[t]['code to vote'].keys():
            g_table[t]['code to vote'][k]['leaf'] = leaf_info['tree ' + str(t)].index(str(list(g_table[t]['code to vote'][k]['leaf'])))

    for k in g_table['votes to class'].keys():
        for t in range(num_trees):
            g_table['votes to class'][k]['t'+str(t)+' vote'] = leaf_info['tree ' + str(t)].index(str(list(g_table['votes to class'][k]['t'+str(t)+' vote'])))

    feature_width = []
    for max_f in feature_max:
        feature_width += [int(np.ceil(math.log(max_f, 2)) + 1)]

    code_width_tree_feature = np.zeros((num_trees, num_features))
    for i in range(num_features):
        for tree in range(num_trees):
            # code_width_tree_feature[tree, i] = np.ceil(math.log(g_table[tree]['feature ' + str(i)][feature_max[i]],2))
            code_width_tree_feature[tree, i] = int(np.ceil(math.log(
                g_table[tree]['feature ' + str(i)][np.max(list(g_table[tree]['feature ' + str(i)].keys()))] + 1,
                2) + 1)) or 1
            # print(code_width_tree_feature[tree, i] , g_table[tree]['feature ' + str(i)][feature_max[i]])
            # print('stop')

    LPM_Table = {}
    LPM_Table['decision'] = g_table['votes to class']

    for tree in range(num_trees):
        LPM_Table['tree ' + str(tree)] = g_table[tree]['code to vote']

    for i in range(num_features):
        LPM_Table['feature ' + str(i)] = {}
        for value in range(feature_max[i]):
            LPM_Table['feature ' + str(i)][value] = []
            for tree in range(num_trees):
                LPM_Table['feature ' + str(i)][value] += [g_table[tree]["feature " + str(i)][value]]
    Exact_Table = copy.deepcopy(LPM_Table)
    for i in range(num_features):
        if i != 0:
            print('')
        print('Begine transfer: Feature table ' + str(i))
        LPM_Table['feature ' + str(i)] = Table_to_LPM(LPM_Table['feature ' + str(i)], feature_width[i])
        

    # ===================== prepare default vote =========================
    print("\nPreparing default vote...", end="")
    collect_votes = []
    for t in range(num_trees):
        for idx in Exact_Table['tree ' + str(t)]:
            collect_votes += [int(Exact_Table['tree ' + str(t)][idx]['leaf'])]
    default_vote = max(collect_votes, key=collect_votes.count)

    code_table_size = 0
    for t in range(num_trees):
        LPM_Table['tree ' + str(t)] = {}
        for idx in Exact_Table['tree ' + str(t)]:
            if int(Exact_Table['tree ' + str(t)][idx]['leaf']) != default_vote:
                LPM_Table['tree ' + str(t)][code_table_size] = Exact_Table['tree ' + str(t)][idx]
                code_table_size += 1
        Exact_Table['tree ' + str(t)] = copy.deepcopy(LPM_Table['tree ' + str(t)])
    print('Done')
    # ===================== prepare default class =========================
    print("Preparing default class...", end="")
    collect_class = []
    for idx in Exact_Table['decision']:
        collect_class += [Exact_Table['decision'][idx]['class']]
    default_class = max(collect_class, key=collect_class.count)
    code_table_size = 0
    LPM_Table['decision'] = {}
    for idx in Exact_Table['decision']:
        if Exact_Table['decision'][idx]['class'] != default_class:
            LPM_Table['decision'][code_table_size] = Exact_Table['decision'][idx]
            code_table_size += 1
    Exact_Table['decision'] = copy.deepcopy(LPM_Table['decision'])
    print('Done')

    table_name = 'LPM_Table.json'
    json.dump(LPM_Table, open('Tables/' + table_name, 'w'), indent=4, cls=NpEncoder)
    print('LPM_Table is generated')
    json.dump(Exact_Table, open('Tables/Exact_Table.json', 'w'), indent=4, cls=NpEncoder)
    print('Exact_Table is generated')

    Planter_config['p4 config'] = {}
    Planter_config['p4 config']["model"] = "IF"
    Planter_config['p4 config']["number of features"] = num_features
    Planter_config['p4 config']["number of classes"] = num_classes
    Planter_config['p4 config']["number of trees"] = num_trees
    Planter_config['p4 config']['table name'] = 'LPM_Table.json'
    Planter_config['p4 config']["decision table size"] = len(LPM_Table['decision'].keys())
    Planter_config['p4 config']["code table size"] = []
    for tree in range(num_trees):
        Planter_config['p4 config']["code table size"] += [len(LPM_Table['tree ' + str(tree)].keys())]
    Planter_config['p4 config']["default vote"] = default_vote
    Planter_config['p4 config']["default label"] = default_class
    Planter_config['p4 config']["width of feature"] = feature_width
    Planter_config['p4 config']["width of code"] = code_width_tree_feature
    Planter_config['p4 config']["used columns"] = []
    for i in range(num_features):
        Planter_config['p4 config']["used columns"] += [len(LPM_Table['feature ' + str(i)].keys())]
    Planter_config['p4 config']["width of probability"] = 7
    Planter_config['p4 config']["width of result"] = 8
    Planter_config['p4 config']["standard headers"] = ["ethernet", "Planter", "arp", "ipv4", "tcp", "udp", "vlan_tag"]
    Planter_config['test config'] = {}
    Planter_config['test config']['type of test'] = 'classification'

    json.dump(Planter_config,
              open(Planter_config['directory config']['work'] + '/src/configs/Planter_config.json', 'w'), indent=4,
              cls=NpEncoder)
    print(Planter_config['directory config']['work'] + '/src/configs/Planter_config.json is generated')

    # main()
    return sklearn_y_predict.tolist()


def test_tables(sklearn_test_y, test_X, test_y):
    config_file = 'src/configs/Planter_config.json'
    Planter_config = json.load(open(config_file, 'r'))
    num_features = Planter_config['data config']['number of features']
    num_classes = Planter_config['model config']['number of classes']
    num_trees = Planter_config['model config']['number of trees']
    LPM_Table = json.load(open('Tables/LPM_Table.json', 'r'))
    Exact_Table = json.load(open('Tables/Exact_Table.json', 'r'))

    print('Test the exact feature table, extact code and decision table (feel free if the acc to sklearn is slightly lower than 1)')
    same = 0
    correct = 0
    error = 0
    switch_test_y = []
    for i in range(np.shape(test_X.values)[0]):
        vote_list = np.zeros(num_trees).astype(dtype=int).tolist()
        for tree in range(num_trees):
            code_list = np.zeros(num_features)
            lpm_code_list = np.zeros(num_features)
            input_feature_value = test_X.values[i]

            for f in range(num_features):
                match_or_not = False

                # matcg ternary
                LPM_table = LPM_Table['feature ' + str(f)]
                keys = list(LPM_table.keys())

                mask = []
                action = []
                for count in np.sort(keys):  # For each value in LPM table, check if it matches that separation key
                    if input_feature_value[f] & LPM_table[count][0] == LPM_table[count][0] & LPM_table[count][
                        1]:  # if there is a ternary match
                        mask.append(LPM_table[count][0])  # array of masks
                        action.append(LPM_table[count][2])  # array of actions
                max_mask = max(mask)
                max_index = mask.index(max_mask)
                lpm_code_list[f] = action[max_index][tree]  # Choose the action with the longest prefix match

                # matcg exact
                code_list[f] = Exact_Table['feature ' + str(f)][str(input_feature_value[f])][tree]

            if str(code_list) != str(lpm_code_list):
                print('error in exact to ternary match', code_list, lpm_code_list)
            for key in Exact_Table["tree " + str(tree)]:

                match_or_not = False
                all_True = True
                for code_f in range(num_features):
                    if not Exact_Table["tree " + str(tree)][key]['f' + str(code_f) + ' code'] == code_list[code_f]:
                        all_True = False
                        break
                if all_True:
                    vote_list[tree] = int(Exact_Table["tree " + str(tree)][key]['leaf'])
                    match_or_not = True
                    break
            if not match_or_not:
                vote_list[tree] = Planter_config['p4 config']["default vote"]

        for key in Exact_Table['decision']:
            match_or_not = False
            all_True = True
            for tree_v in range(num_trees):
                if not Exact_Table["decision"][key]['t' + str(tree_v) + ' vote'] == vote_list[tree_v]:
                    all_True = False
                    break
            if all_True:
                switch_prediction = Exact_Table['decision'][key]['class']
                match_or_not = True
                break
        if not match_or_not:
            # print('decision(vote to class) table not matched', vote_list)
            switch_prediction = Planter_config['p4 config']["default label"]
        # print(test_y)

        switch_test_y += [switch_prediction]
        if switch_prediction == test_y[i]:
            correct += 1

        if switch_prediction == sklearn_test_y[i]:
            same += 1
        else:
            error += 1
            
        if i % 1 == 0 and i != 0:
            print(
                '\rswitch_prediction: {}, sklearn: {}, test_y: {}, with acc: {:.3}, with acc to sklearn: {:.4}, M/A format macro f1: {:.3}, macro f1: {:.3}'.format(
                    switch_prediction, sklearn_test_y[i], test_y[i], correct / (i + 1), same / (i + 1),
                    f1_score(switch_test_y[:i], test_y[:i]), f1_score(sklearn_test_y[:i], test_y[:i])),
                end=" ")

    print('\nThe accuracy of the match action format of Random Forest is', correct / np.shape(test_X.values)[0])
    result = classification_report(switch_test_y, test_y, digits=4)
    print('\n', result)
