# -*- coding: utf-8 -*-
"""
Created on Tue Oct  5 09:33:29 2021

@author: Alexander

"""

import numpy as np

'''
utiles function
'''
def repair_bmu_loc(bmu_loc_l, mtrx_indx, i):
    bmu_loc_f = np.asarray(bmu_loc_l)
    mtrx_indx = mtrx_indx    
    j1, i1 = bmu_loc_f[mtrx_indx[i][1]] 

    # case [j-1, i]
    j1_tmp = j1 - 1
    i1_tmp = i1
    if j1_tmp<0 : j1_tmp = 0
    tmp_m = [j1_tmp, i1_tmp]
    if np.where((bmu_loc_f==tmp_m).all(axis=1))[0].size == 0:
        bmu_loc_f[mtrx_indx[i][1]] = tmp_m
#        i-=1
        # exit ???
        return bmu_loc_f 
        
    # case [j-1, i-1]
    j1_tmp = j1 - 1
    i1_tmp = i1 - 1
    if j1_tmp<0 : j1_tmp = 0
    if i1_tmp<0 : i1_tmp = 0
    tmp_m = [j1_tmp, i1_tmp]
    if np.where((bmu_loc_f==tmp_m).all(axis=1))[0].size == 0:
        bmu_loc_f[mtrx_indx[i][1]] = tmp_m
#        i-=1
        # exit ???
        return bmu_loc_f 

    # case [j, i-1]
    j1_tmp = j1
    i1_tmp = i1 - 1
    if i1_tmp<0 : i1_tmp = 0
    tmp_m = [j1_tmp, i1_tmp]
    if np.where((bmu_loc_f==tmp_m).all(axis=1))[0].size == 0:
        bmu_loc_f[mtrx_indx[i][1]] = tmp_m
#        i-=1
        # exit ???
        return bmu_loc_f 

    # case [j+1, i-1]
    j1_tmp = j1 + 1
    i1_tmp = i1 - 1
    if j1_tmp>bmu_loc_f[:, 0].max() : j1_tmp = bmu_loc_f[:, 0].max()
    if i1_tmp<0 : i1_tmp = 0
    tmp_m = [j1_tmp, i1_tmp]
    if np.where((bmu_loc_f==tmp_m).all(axis=1))[0].size == 0:
        bmu_loc_f[mtrx_indx[i][1]] = tmp_m
#        i-=1
        # exit ???
        return bmu_loc_f 

    # case [j+1, i]
    j1_tmp = j1 + 1
    i1_tmp = i1
    if j1_tmp>bmu_loc_f[:, 0].max() : j1_tmp = bmu_loc_f[:, 0].max()
    tmp_m = [j1_tmp, i1_tmp]
    if np.where((bmu_loc_f==tmp_m).all(axis=1))[0].size == 0:
        bmu_loc_f[mtrx_indx[i][1]] = tmp_m
#        i-=1
        # exit ???
        return bmu_loc_f 

    # case [j+1, i+1]
    j1_tmp = j1 + 1
    i1_tmp = i1 + 1
    if j1_tmp>bmu_loc_f[:, 0].max() : j1_tmp = bmu_loc_f[:, 0].max()
    if i1_tmp>bmu_loc_f[:, 1].max() : i1_tmp = bmu_loc_f[:, 1].max()
    tmp_m = [j1_tmp, i1_tmp]
    if np.where((bmu_loc_f==tmp_m).all(axis=1))[0].size == 0:
        bmu_loc_f[mtrx_indx[i][1]] = tmp_m
#        i-=1
        # exit ???
        return bmu_loc_f 
    
    # case [j, i+1]
    j1_tmp = j1
    i1_tmp = i1 + 1
    if i1_tmp>bmu_loc_f[:, 1].max() : i1_tmp = bmu_loc_f[:, 1].max()
    tmp_m = [j1_tmp, i1_tmp]
    if np.where((bmu_loc_f==tmp_m).all(axis=1))[0].size == 0:
        bmu_loc_f[mtrx_indx[i][1]] = tmp_m
#        i-=1
        # exit ???
        return bmu_loc_f 

    # case [j-1, i+1]
    j1_tmp = j1 - 1
    i1_tmp = i1 + 1
    if j1_tmp<0 : j1_tmp = 0
    if i1_tmp>bmu_loc_f[:, 1].max() : i1_tmp = bmu_loc_f[:, 1].max()
    tmp_m = [j1_tmp, i1_tmp]
    if np.where((bmu_loc_f==tmp_m).all(axis=1))[0].size == 0:
        bmu_loc_f[mtrx_indx[i][1]] = tmp_m
#        i-=1
        # exit ???
        return bmu_loc_f
    
    return bmu_loc_f
    




''' MAIN block
'''

def correction_bmu_location (bmu_loc):
    
#bmu_loc_np = np.load("array_bmu_loc.npy")
    bmu_loc_np = bmu_loc

    matrx = []
    for i in range(len(bmu_loc_np)):
        row_m = bmu_loc_np[i]
        tmp_m = np.where((bmu_loc_np==row_m).all(axis=1))[0]
        matrx.append(tmp_m)
    
    #trying to do something
#    double_items=[]
    
    for i in range(len(matrx)):
        if matrx[i].shape[0] >1:
            bmu_loc_np = repair_bmu_loc(bmu_loc_np, matrx, i) 
            
    return bmu_loc_np
#np.where((bmu_loc_np==[2, 2]).all(axis=1))[0].size    

