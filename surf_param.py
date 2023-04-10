# -*- coding: utf-8 -*-
"""
Created on Fri Apr  7 16:06:30 2023

@author: Alexander
"""

import scipy.stats as sci_st

'''
functions for calculation amplitude parameters of roughness
'''


def get_Sa(data2D):
    data = data2D
    return data.mean()

def get_Ssk(data2D):
    data = data2D
    return sci_st.skew(data, axis = None)

def get_Sku(data2D):
    data = data2D
    return sci_st.kurtosis(data, axis = None)

def get_Sq(data2D):
    data = data2D
    return data.std()

'''
would be better to add the functions for calculation areal parameters
???

'''