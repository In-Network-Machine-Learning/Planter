# THIS FILE IS PART OF Planter PROJECT
# Planter.py - The core part of the Planter library
#
# THIS PROGRAM IS FREE SOFTWARE TOOL, WHICH MAPS MACHINE LEARNING ALGORITHMS TO DATA PLANE, IS LICENSED UNDER Apache-2.0
# YOU SHOULD HAVE RECEIVED A COPY OF WTFPL LICENSE, IF NOT, PLEASE CONTACT THE FOLLOWING E-MAIL ADDRESSES
#
# E-mail: changgang.zheng@eng.ox.ac.uk or changgangzheng@qq.com
#
# Functions: This file includes logic gate functions.
#            Please refer to ./Docs/Planter_User_Document.pdf or further information.

import math


def swap(a, b):
    temp = a
    a = b
    b = temp

# log(n) solution

def XNOR_with_bits(a, b, num_bits):
    # Make sure a is larger
    if (a < b):
        swap(a, b)
    # counter for count bit and
    #  set bit in xnor num
    count = 0
    # for make new xnor number
    xnornum = 0
    # for set bits in new xnor
    # number
    for _ in range(num_bits):
        # get last bit of a
        a_rem = a & 1
        # get last bit of b
        b_rem = b & 1
        # Check if current two
        # bits are same
        if (a_rem == b_rem):
            xnornum |= (1 << count)
        # counter for count bit
        count = count + 1
        a = a >> 1
        b = b >> 1
    return xnornum

def XNOR(a, b):
    # Make sure a is larger
    if (a < b):
        swap(a, b)
    # counter for count bit and
    #  set bit in xnor num
    count = 0
    # for make new xnor number
    xnornum = 0
    # for set bits in new xnor
    # number
    while (a != 0):
        # get last bit of a
        a_rem = a & 1
        # get last bit of b
        b_rem = b & 1
        # Check if current two
        # bits are same
        if (a_rem == b_rem):
            xnornum |= (1 << count)
        # counter for count bit
        count = count + 1
        a = a >> 1
        b = b >> 1
    return xnornum
