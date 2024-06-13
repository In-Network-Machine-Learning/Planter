# THIS FILE IS PART OF Planter PROJECT
# Planter.py - The core part of the Planter library
#
# THIS PROGRAM IS FREE SOFTWARE TOOL, WHICH MAPS MACHINE LEARNING ALGORITHMS TO DATA PLANE, IS LICENSED UNDER Apache-2.0
# YOU SHOULD HAVE RECEIVED A COPY OF WTFPL LICENSE, IF NOT, PLEASE CONTACT THE FOLLOWING E-MAIL ADDRESSES
#
# Copyright (c) 2020-2021 Changgang Zheng and Riyad Bensoussane
# Copyright (c) Computing Infrastructure Lab, Department of Engineering Science, University of Oxford
# E-mail: changgang.zheng@eng.ox.ac.uk or changgangzheng@qq.com
#
# Functions: This file is a M/A table format converter.
#            Please refer to ./Docs/Planter_User_Document.pdf or further information.

import numpy as np
import math
from collections import Counter

def ten_to_bin(num,count):
    num = bin(num).lstrip('0b')

    if len(num) != count:
        cont = count - len(num)
        num = cont * '0' + num
    return num

def get_mask(count,code_len): #The count input will actually be the bit_num
    return (2**code_len-1)^((2**code_len-1)>>(count+1)) #Bit-Wise AND of ((2^code_len)-1),(((2^code_len)-1)*2^count)
    # The mask will look like this 111110000 for get_mask(4,9) (1s followed by 0s, the change happening at the same bit as prev. function)

def get_value(mask,dict):
    return mask&dict #Bit-wise AND mask with bit_list

def tenary_test(test_value,mask,value):
    return test_value&mask == value&mask #Returns a true or false (checks that the code ANDED with the mask still equals the code)

def Check_Range(table, bit_list, bit_num, action_table):
    upper = bit_list[:bit_num+1] + '1'*(len(bit_list) - bit_num-1) #Fixes all bits upto and including bit_num (from MSB) then 1's
    lower = bit_list[:bit_num+1] + '0'*(len(bit_list) - bit_num-1) #Fixes all bits upto and including bit_num (from MSB) then 0's

    upper_dec = int(upper, 2) #Convert these upper and lower bounds to a decimal number
    lower_dec = int(lower, 2)

    temp_table = {}
    for i in range(lower_dec, upper_dec+1):
        if i in table.keys():
            temp_table[i] = table[i]

    if not temp_table:
        keep = 0
        most_common_action = 404
    else:
        # print(temp_table.values())
        temp_table_for_counter = {}
        for dict in temp_table:
            temp_table_for_counter[dict] = str(temp_table[dict])
        most_common_action, frequency = Counter(temp_table_for_counter.values()).most_common()[0]
        parent_bit_num = bit_num - 1
        keep = 1 # parent action is different from child action, write to table

        for i in range(len(action_table)): #If parent action is as frequent as the most_common_action (there was a tie), choose parent_action
            if action_table[i][0][:parent_bit_num+1] == bit_list[:parent_bit_num+1] and action_table[i][1] == parent_bit_num: #Find row of action table corresponding to parent node on binary tree
                parent_action = action_table[i][2]
                if parent_action == most_common_action:
                    keep = 0
                if Counter(temp_table_for_counter.values())[str(parent_action)] == frequency:
                    most_common_action = parent_action
                    keep = 0  # parent action is the same as child action, don't write to table
                    break
        for dict in temp_table:
            if str(temp_table[dict]) == most_common_action:
                most_common_action = temp_table[dict]
                break

    check = 0

    for i in range(lower_dec, upper_dec):
        k = i+1
        try:
            if table[i] == table[k]:
                pass
            else:
                check = 1 # The actions in that range in the exact match table are not all the same
                break
        except:
            pass
    if upper_dec == lower_dec:
        i = lower_dec


    if check == 0 and i<=np.max(list(table.keys())):

        return True, table[i], keep
    else:
        return False, most_common_action, keep

def write_to_table(LPM_table, bit_list, action, counter, bit_num, code_len):
    bit_list = int(bit_list,2)
    mask = get_mask(bit_num, code_len)
    value = get_value(mask, bit_list)
    LPM_table[counter] = [mask, value, action] #Three columns in LPM table (mask, classification code, action)

    return LPM_table

def write_to_action_table(action_table,bit_list, action, index, bit_num):
    action_table[index] = [bit_list, bit_num, action] #Three columns in LPM table (mask, classification code, action)

    return action_table

def Table_to_LPM_Processor(table, LPM_table, action_table, bit_num, bit_list, code_len, counter, index):
    if bit_num+1 != code_len:
        in_a_range = Check_Range(table, bit_list, bit_num, action_table)
        action = in_a_range[1] #The action could be either 'only action' (True) or most common action (False)
        action_table = write_to_action_table(action_table, bit_list, action, index, bit_num)
        index += 1
        if in_a_range[0] == True: #first iteration/ most common diff from parent action / all values in range share the same action
            if in_a_range[2] == 1: #The action is different from the parent action
                LPM_table = write_to_table(LPM_table, bit_list, action, counter, bit_num, code_len)
                counter += 1
        else: #Not all values in range are the same action
            if in_a_range[2] == 1: #The action is different from the parent action
                LPM_table = write_to_table(LPM_table, bit_list, action, counter, bit_num, code_len)
                counter += 1
            for bit in [0, 1]:
                bit_num += 1
                bit_list = list(bit_list)
                bit_list[bit_num] = bit
                bit_list = ''.join(str(b) for b in bit_list) #Simply replaces that bit_num with that bit
                LPM_table, counter, index = Table_to_LPM_Processor(table, LPM_table, action_table, bit_num, bit_list, code_len, counter, index)
                bit_num -= 1
    else:
        in_a_range = Check_Range(table, bit_list, bit_num, action_table)
        action = in_a_range[1]
        action_table = write_to_action_table(action_table, bit_list, action, index, bit_num)
        index += 1
        if in_a_range[2] == 1:
            LPM_table = write_to_table(LPM_table, bit_list, action, counter, bit_num, code_len)
            counter += 1
            #return LPM_table, counter, index

    return LPM_table, counter, index

def Greedy(LPM_table,code_len):
    interm_table = {}
    for i in range(len(LPM_table)):
        mask = ten_to_bin(LPM_table[i][0],code_len)
        if mask[code_len-1] == '1': #If LSB of the mask is 1, then possibly remove that mask
            if np.random.rand() < 1:
                interm_table[i] = LPM_table[i]
        else:
            interm_table[i] = LPM_table[i]
    return interm_table

def LPM_algorithm(LPM_table,table):

    counts = 0
    correct_match = 0
    keys = list(LPM_table.keys()) #The index of the entries in the new LPM table
    separation_value = list(table.keys())

    for dict in np.sort(separation_value):
        mask = []
        action = []
        counts += 1
        error_switch = True
        for count in np.sort(keys): # For each value in LPM table, check if it matches that separation key
            if dict & LPM_table[count][0] == LPM_table[count][0] & LPM_table[count][1]: #if there is a ternary match
                mask.append(LPM_table[count][0]) #array of masks
                action.append(LPM_table[count][2]) #array of actions
        max_mask = max(mask)
        max_index = mask.index(max_mask)
        max_action = action[max_index] #Choose the action with the longest prefix match

        if table[dict] == max_action: #check the chosen action is the correct action
                    correct_match += 1
                    error_switch = False

        if error_switch == True: #If the incorrect action was chosen print 'error' and the table number
            print("error: ",dict)

        print('\r{}th testing sample with correct matches: {} % and {} errors.'.format( counts,   100*correct_match / counts ,
              counts - correct_match),end=" " )

def Table_to_sep_val(table):
    separation_value_input = list(table.keys())
    Table={} # Create an empty array called 'table', to fill
    initial = sorted(separation_value_input, reverse=True)[0] # Select the separation value with the highest value
    for dict in sorted(separation_value_input, reverse=True): # For each separation value in descending order
        if dict == initial: #If the separation value is the first (and highest value key)
            Table[dict] = table[dict]
            lasat_lable = table[dict]
        if table[dict] != lasat_lable:
            Table[dict] = table[dict]
            lasat_lable = table[dict]
        if dict == 0:
            Table[dict] = table[dict] # When you get to the end of the for loop, the last value in table and final key is 0
    #This for-loop selects all feature values at bounderies and puts them in Table
    #For instance if the first 20 actions of the exact match table were 112111112111211121111121 then Table would be 1121212121 in reverse order
    #Selects the value before the value change

    separation_value = list(Table.keys()) #Selects index of seperation values (starting from highest e.g 99,98,86,77,56,29,6,1)

    return separation_value, separation_value_input

def generate_test_exact_table(entry):
    table = {}
    type = 0

    for i in range(entry):

        if np.random.rand() < 0.9:
            x = np.random.rand()
            if x > 0.26:
                type = 1
            elif x < 0.33:
                type = 2
            else:
                type = 0

        table[i] = type
    return table


def Table_to_LPM(table, code_len):
    LPM_table = {}
    action_table = {}
    bit_num = 0
    # code_len = int(np.ceil(math.log(np.max(list(table.keys())), 2)) + 1)  # may need np.int
    bit_list = '0' * code_len

    LPM_table, _, _ = Table_to_LPM_Processor(table, LPM_table, action_table, bit_num, bit_list, code_len, 0, 0)

    separation_value, separation_value_input = Table_to_sep_val(table)

    print('Input table has: ', len(separation_value_input), 'entries and: ', len(separation_value), ' different ranges and output LPM entry has', len(list(LPM_table.keys())))

    match = 0
    counts = 0
    correct_match = 0
    keys = list(LPM_table.keys())
    separation_value = list(table.keys())

    for dict in np.sort(separation_value):
        counts += 1
        error_switch = True

        mask = []
        action = []

        for count in np.sort(keys):  # For each value in LPM table, check if it matches that separation key
            if dict & LPM_table[count][0] == LPM_table[count][0] & LPM_table[count][1]:  # if there is a ternary match
                mask.append(LPM_table[count][0])  # array of masks
                action.append(LPM_table[count][2])  # array of actions
        try:
            max_mask = max(mask)
            max_index = mask.index(max_mask)
            max_action = action[max_index]  # Choose the action with the longest prefix match
            match += 1
        except Exception as e:
            max_action = 0

        if table[dict] == max_action:
            correct_match += 1
            error_switch = False


        if error_switch == True:
            print("error: ", dict)

        print('\r{}th testing sample with correct matches: {} % and {} errors.'.format(counts, 100 * correct_match / counts, counts - correct_match), end=" ")
    return LPM_table



if __name__ == "__main__":
    np.random.seed(1)
    table = generate_test_exact_table(2000)

    code_len = int(np.ceil(math.log(np.max(list(table.keys())),2))+1) #may need np.int
    LPM_table = Table_to_LPM(table, code_len)

    LPM_table = Greedy(LPM_table,code_len)

    separation_value, separation_value_input = Table_to_sep_val(table)


    LPM_algorithm(LPM_table, table)
