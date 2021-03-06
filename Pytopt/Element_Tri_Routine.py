"""
Triangular element routine

Inputs:
    ue          -Element displacements
    ex          -Element x coordinates
    ey          -Element y coordinates
    ep[thickness, linear, el_type]
                 thickness  - thickness of the 2D material
                 linear     - True-linear, False-nonlinear
                 el_type    - 2 indicates triangular elements and 3 indicates
                 quad elements.
    mp[E,nu,eps_y]
                 E          - Young's modulus
                 nu         - Poission's ratio
                 eps_y      - Yielding strain for bilinear material model
    materialFun -Material model
    eq          -Body force
Outputs:
    Ke          -Element stiffness matrix
    fint        -Interal force vector
    fext        -External force vector
    stress      -Stress
    epsilon     -Strain
    

Written 2021-05
Made By: Daniel Pettersson & Erik Säterskog
"""


import numpy as np
from scipy.sparse.linalg import spsolve

def Element_Tri_Routine(ue, ex, ey, ep, mp, materialFun, eq=None):


    ptype   = ep[0]         # Which analysis type?
    t       = ep[1]         # Element thickness
    ir      = ep[2]  
    ngp=3                   # Integration rule and number of gauss points


#% If 6th input argument present, assign body load.
    b=np.zeros([2,1])
    
    if not eq is None:
        b[0] = eq[0]
        b[1] = eq[1]
        
# Setup gauss quadrature
    wp, xsi, eta = gauss_quadrature(ir)

#Setup shape functions and its derivatives at each gauss point
    N, dNr = shape_functions(eta, xsi, ngp)

    JT=np.matmul(dNr,np.transpose([ex,ey]))

# Loop over integration points, add the contributions to Ke, fint and fext
    Ke      = np.zeros([6,6])    #Preallocate Ke
    fint    = np.zeros([6,1])    #Preallocate fint
    fext    = np.zeros([6,1])    #Preallocate fext
    stress  = np.zeros([6, ngp]) #Preallocate stress

# Plane strain, selectively reduced integration (Abaqus' method)
    if ptype==3 and ir==2:
        raise Exception('not yet implemented')
        
    if ptype==2: #Plane strain
        
        for i in range(0,ngp):
            indx=np.transpose([ 2*i, 2*i+1 ])
            detJ=np.linalg.det(JT[indx,:])
            if detJ < 1e-10:
                print('Jacobideterminant equal or less than zero!')
                
            dNx=spsolve(JT[indx,:],dNr[indx,:])
        
#       Extract values of B(xsi, eta) at current gauss point            
            B = np.zeros([3,6])
            
            B[0,0:ngp*2:2]= dNx[0,:]
            B[1,1:ngp*2:2]= dNx[1,:]
            B[2,0:ngp*2:2]= dNx[1,:]
            B[2,1:ngp*2:2]= dNx[0,:]


#Extract shape function N(xsi, eta) at current gauss point
            N2=np.zeros([2,6])

            N2[0,np.ix_([0,2,4])] = N[i,:]
            N2[1,np.ix_([1,3,5])]  = N[i,:]
        
#Calculate strain at current gauss point
            epsilon = np.zeros([6,])
            epsilon[np.ix_([0,1,3])] = np.matmul(B,ue)
            
#Calculate material response at current gauss point
            [sigma, dsde] = materialFun(epsilon,mp)

                
            stress[:, i] = sigma.reshape(6,)   #Save stress for current gauss point
        
#Calculate the gauss point's contribution to element stiffness and forces
            Dm=dsde[np.ix_([0, 1, 3],[0, 1, 3])]                               # Components for plane strain
            Ke=Ke+np.matmul(np.matmul(B.T,Dm),B)*detJ*wp[i]*t                  # Stiffness contribution
            fint=fint+np.matmul(B.T,sigma[np.ix_([0,1,3])])*wp[i]*detJ*t       # Internal force vector 
            fext=fext+np.matmul(N2.T,b)*detJ*wp[i]*t                           # External force vector
    
    else:
        raise Exception('Only plane strain ep(1)=ptype=2 allowed (unless ep(2)=2, then ep(1)=3 is allowed)');
    
    
    return Ke, fint, fext, stress[:,0],epsilon

def gauss_quadrature(ir):
# Setup gauss quadrature
    if ir==1:
        gp=np.zeros(2)
        g1=1/3
        w1=1/2
        gp=[ g1, g1 ]
        w= [ w1, w1 ]
    elif ir==2:
        gp=np.zeros([3,2])
        w=np.zeros([3,2])
        g1=1/6
        g2=2/3
        w1=1/6
        gp[:,0]=np.transpose([g1, g2, g1])
        gp[:,1]=np.transpose([g1, g1, g2])
            
        w[:,0]=np.transpose([ w1, w1, w1])
        w[:,1]=np.transpose([ w1, w1, w1])
            
    elif ir==3:
        raise Exception('NOT YET IMPLEMENTED')
    else:
        raise Exception('Invalid integration rule. ir = 1, 2 or 3')

    wp=w[:,0]
    xsi=gp[:,0]
    eta=gp[:,1]

    return wp, xsi, eta

def shape_functions(eta, xsi, ngp):

    N=np.zeros([np.size(xsi),3])
    dNr=np.zeros([ngp*2,3])
    
    r2=ngp*2
    N[:,0]=1-eta-xsi 
    N[:,1]=xsi
    N[:,2]=eta  

    dNr[0:r2:2,0]=-1
    dNr[0:r2:2,1]=1
    dNr[0:r2:2,2]=0   
    
    dNr[1:r2+1:2,0]=-1   
    dNr[1:r2+1:2,1]=0
    dNr[1:r2+1:2,2]=1
    

    return N, dNr





