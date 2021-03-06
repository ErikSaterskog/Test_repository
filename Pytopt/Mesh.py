"""
Creates the mesh. Triangular or quad elements are used.

Input:
    g       -Geometrical object
    elsize  -aproximate element size
    
Output:
    coords  -Coordinates of nodes
    edof    -Element degree of freedom
    dofs    -degree of freedoms
    bdofs   -boundary degree of freedoms
    

Written 2021-05
Made By: Daniel Pettersson & Erik Säterskog
"""

import calfem.mesh as cfm

class Mesh:
    
    def __init__(self,g,elsize):
        self.mesh = cfm.GmshMesh(g)
        self.mesh.dofs_per_node = 2  
        self.mesh.el_size_factor = elsize  
        
    def tri(self):
        self.mesh.el_type = 2
        
        coords, edof, dofs, bdofs, elementmarkers = self.mesh.create()
        return coords, edof, dofs, bdofs
        
    def quad(self):
        self.mesh.el_type = 3
         
        coords, edof, dofs, bdofs, elementmarkers = self.mesh.create()
        return coords, edof, dofs, bdofs
    
