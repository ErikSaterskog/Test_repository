"""
Selection routine for the different material models.

A numerical calculation of the constitutive matrix is also included


Written 2021-05
Made By: Daniel Pettersson & Erik Säterskog
"""

import numpy as np
from Pytopt import Material_Elastic, Material_Bilinear, Material_ModifiedHooke

def Elastic(eps,mp):
    return Material_Elastic.elastic(eps,mp) 

def ModifiedHooke(eps,mp):
    return Material_ModifiedHooke.mod_hooke(eps,mp)

def Bilinear(eps,mp):
    return Material_Bilinear.Bilinear(eps,mp)

def numD(eps,sig,mp,mat):
    delta = 1e-7
    D = np.zeros([6,6])
    for i in range(0,6):
        eps2 = eps.copy()
        eps2[i] = eps[i] + delta
        sig2 = mat(eps2,mp)[0]
        
        D[i,:] = (sig2-sig)/delta
    return D
    

