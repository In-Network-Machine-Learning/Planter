# THIS FILE IS PART OF Planter PROJECT
# Planter.py - The core part of the Planter library
#
# THIS PROGRAM IS FREE SOFTWARE TOOL, WHICH MAPS MACHINE LEARNING ALGORITHMS TO DATA PLANE, IS LICENSED UNDER Apache-2.0
# YOU SHOULD HAVE RECEIVED A COPY OF WTFPL LICENSE, IF NOT, PLEASE CONTACT THE FOLLOWING E-MAIL ADDRESSES
#
# E-mail: changgang.zheng@eng.ox.ac.uk or changgangzheng@qq.com
#
# Functions: This file realises normalization functions.
#            Please refer to ./Docs/Planter_User_Document.pdf or further information.

import numpy as np

def Single_MaxMinNormalization(x, min_x, max_x):
    """[0,1] normaliaztion"""
    x = (x - min_x) / (max_x - min_x)
    return x

def MaxMinNormalization_with_scale(x, scale):
    """[0,1] normaliaztion"""
    x = (scale*(x - np.min(x)) / (np.max(x) - np.min(x))).astype(int)
    return x

def MaxMinNormalization(x):
    """[0,1] normaliaztion"""
    x = (x - np.min(x)) / (np.max(x) - np.min(x))
    return x

def Single_ZscoreNormalization(sigle_x , x_m, x_std):
    """Z-score normaliaztion"""
    sigle_x = (sigle_x - x_m) / x_std
    return sigle_x

def ZscoreNormalization(x):
    """Z-score normaliaztion"""
    x = (x - np.mean(x)) / np.std(x)
    return x

