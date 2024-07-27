import gmsh
import sys
import math
import os

gmsh.initialize()

#------------------------------parameters-------------------------------------#
L0 = 1.00
L1 = 0.30
L2 = 0.20
Htop =0.5
#adjustable parameters
h0 = 0.05 # adjust height of duct
h1 = 0.05 # adjust height of b on ramp
h2 = 0.15 # adjust height of c on ramp
h3 = 0.30
theta = math.radians(10) # to adjust dip of cowl 
r = 0.15

#----------------------------creating geometry----------------------------------#

# Points defining the hypersonic inlet domain
lc = 1e-2/2
i1=gmsh.model.geo.addPoint(0.0 , 0.0, 0.0, lc) #a
b1=gmsh.model.geo.addPoint(L0/3 , h1, 0.0, lc) #b
b2=gmsh.model.geo.addPoint(2*L0/3 , h2, 0.0, lc) #c
b3=gmsh.model.geo.addPoint(L0 , h3, 0.0, lc) #s
b4=gmsh.model.geo.addPoint(L0+L1 , h3, 0.0, lc) #e 
o1=gmsh.model.geo.addPoint(L0+L1+L2 , 0.95*h3, 0.0, lc) #f 
i2=gmsh.model.geo.addPoint(0.0 , h3, 0.0, lc) #g
c1=gmsh.model.geo.addPoint(L0-r*math.cos(theta) , h3+h0-r*math.sin(theta), 0.0, lc) #h 
c2=gmsh.model.geo.addPoint(L0 , h3+h0, 0.0, lc) #i
c3=gmsh.model.geo.addPoint(L0+L1 , h3+h0, 0.0, lc) #j
o2=gmsh.model.geo.addPoint(L0+L1+L2 , h3+h0, 0.0, lc) #k
i3=gmsh.model.geo.addPoint(0.0 , Htop, 0.0, lc) #l
t=gmsh.model.geo.addPoint(L0-r , Htop, 0.0, lc) #m

# lines joining the points
gmsh.model.geo.addLine(i1,i2,1) #inlet 
gmsh.model.geo.addLine(i2,i3,2) #inlet
gmsh.model.geo.addLine(o1,o2,3) #outlet
gmsh.model.geo.addLine(i3,t,4) #top
gmsh.model.geo.addLine(c1,t,5) #invis
gmsh.model.geo.addBSpline([i1,b1,b2,b2,b3,b4,o1],6) #body
gmsh.model.geo.addBSpline([c1,c2,c3,o2],7) #cowl

#establishing connections of lines
gmsh.model.geo.addCurveLoop([6,3,-7,5,-4,-2,-1], 1)

#creating 2D domain surface from the lines
gmsh.model.geo.addPlaneSurface([1], 1)


#dummy geometries for meshing
#gmsh.model.geo.addLine(c1,b4,100)

gmsh.model.geo.synchronize()

#domain boundaries 
gmsh.model.addPhysicalGroup(1, [1,2], name="inlet")
gmsh.model.addPhysicalGroup(1, [3], name="outlet")
gmsh.model.addPhysicalGroup(1, [6], name="body")
gmsh.model.addPhysicalGroup(1, [7], name="cowl")
gmsh.model.addPhysicalGroup(1, [4], name="top")
gmsh.model.addPhysicalGroup(1, [5], name="invis")
'''
#-----------------------------set mesh fields------------------------------------#
#global mesh size scaling factor (without changing the above definitions)
gmsh.option.setNumber("Mesh.MeshSizeFactor", 2);

# Say we would like to obtain mesh elements with size lc/100 near curve y and
# point x, and size lc elsewhere. To achieve this, we can use two fields:
# "Distance", and "Threshold". We first define a Distance field (`Field[1]') on
# points x and on curve y. This field returns the distance to point x and to
# (1000 equidistant points on) curve y.
gmsh.model.mesh.field.add("Distance", 1)
#gmsh.model.mesh.field.setNumbers(1, "PointsList", [i1,b1,b2,b3,b4,o1,o2,c1,c2,c3,t,i2,i3])
gmsh.model.mesh.field.setNumbers(1, "CurvesList", [1,2,4,5,100])
gmsh.model.mesh.field.setNumber(1, "Sampling", 1e2)

# We then define a `Threshold' field, which uses the return value of the
# `Distance' field 1 in order to define a simple change in element size
# depending on the computed distances
# SizeMax -                     /------------------
#                              /
#                             /
#                            /
# SizeMin -o----------------/
#          |                |    |
#        Point         DistMin  DistMax
gmsh.model.mesh.field.add("Threshold", 2)
gmsh.model.mesh.field.setNumber(2, "InField", 1)
gmsh.model.mesh.field.setNumber(2, "SizeMin", lc/10)
gmsh.model.mesh.field.setNumber(2, "SizeMax", lc)
gmsh.model.mesh.field.setNumber(2, "DistMin", lc/10)
gmsh.model.mesh.field.setNumber(2, "DistMax", lc*5)

#mesh the body boundary
gmsh.model.mesh.field.add("Distance", 3)
gmsh.model.mesh.field.setNumbers(3, "CurvesList", [6,7])
gmsh.model.mesh.field.setNumber(3, "Sampling", 1e4)
gmsh.model.mesh.field.add("Threshold", 4)
gmsh.model.mesh.field.setNumber(4, "InField", 3)
gmsh.model.mesh.field.setNumber(4, "SizeMin", lc/50)
gmsh.model.mesh.field.setNumber(4, "SizeMax", lc/2)
gmsh.model.mesh.field.setNumber(4, "DistMin", lc/50)
gmsh.model.mesh.field.setNumber(4, "DistMax", lc*5)

gmsh.model.mesh.field.add("Distance", 5)
gmsh.model.mesh.field.setNumbers(5, "CurvesList", [3])
gmsh.model.mesh.field.setNumber(5, "Sampling", 10)
gmsh.model.mesh.field.add("Threshold", 6)
gmsh.model.mesh.field.setNumber(6, "InField", 5)
gmsh.model.mesh.field.setNumber(6, "SizeMin", lc/30)
gmsh.model.mesh.field.setNumber(6, "SizeMax", lc)
gmsh.model.mesh.field.setNumber(6, "DistMin", lc/50)
gmsh.model.mesh.field.setNumber(6, "DistMax", lc*5)

#setting background mesh
gmsh.model.mesh.field.add("Min", 10)
gmsh.model.mesh.field.setNumbers(10, "FieldsList", [2,4,6])
gmsh.model.mesh.field.setAsBackgroundMesh(10)


#def meshSizeCallback(dim, tag, x, y, z, lc):
 #   return min(lc, 0.02 * x + 0.01)
#gmsh.model.mesh.setSizeCallback(meshSizeCallback)
# They can also be set for individual surfaces, e.g. for using `MeshAdapt' on
# surface 1:
#gmsh.model.mesh.setAlgorithm(2, 33, 1)
# To generate a curvilinear mesh and optimize it to produce provably valid
# curved elements  
#msh.option.setNumber("Mesh.ElementOrder", 2)
# gmsh.option.setNumber("Mesh.HighOrderOptimize", 2)
# The `setTransfiniteCurve()' meshing constraints explicitly specifies the
# location of the nodes on the curve. For example, the following command forces
# 20 uniformly placed nodes on curve 2 (including the nodes on the two end
# points):
#gmsh.model.geo.mesh.setTransfiniteCurve(2, 20)
# Finally, we put 30 nodes following a geometric progression on curve 1
# (reversed) and on curve 3: Put 30 points following a geometric progression
gmsh.model.geo.mesh.setTransfiniteCurve(1, 30, "Progression", -1.2)
gmsh.model.geo.mesh.setTransfiniteCurve(3, 30, "Progression", 1.2)
# The `setTransfiniteSurface()' meshing constraint uses a transfinite
# interpolation algorithm in the parametric plane of the surface to connect the
# nodes on the boundary using a structured grid. If the surface has more than 4
# corner points, the corners of the transfinite interpolation have to be
# specified by hand:
gmsh.model.geo.mesh.setTransfiniteSurface(1, "Left", [1, 2, 3, 4])
# To create quadrangles instead of triangles, one can use the `setRecombine'
# constraint:
gmsh.model.geo.mesh.setRecombine(2, 1)
# When the surface has only 3 or 4 points on its boundary the list of corners
# can be omitted in the `setTransfiniteSurface()' call:
# # Finally we apply an elliptic smoother to the grid to have a more regular
# mesh:
gmsh.option.setNumber("Mesh.Smoothing", 100)


gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
#gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
#gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)


# Finally, while the default "Frontal-Delaunay" 2D meshing algorithm
# (Mesh.Algorithm = 6) usually leads to the highest quality meshes, the
# "Delaunay" algorithm (Mesh.Algorithm = 5) will handle complex mesh size fields
# better - in particular size fields with large element size gradients:'''
gmsh.option.setNumber("Mesh.Algorithm", 8)

# If we'd had several surfaces, we could have used the global option "Mesh.RecombineAll":
gmsh.option.setNumber("Mesh.RecombineAll", 1)

# We can then generate a 2D mesh...
gmsh.model.mesh.generate(2)
#gmsh.model.mesh.refine()

#-------------------------export mesh files and view-----------------------------#

# if physical groups are defined, Gmsh will export in the output mesh file 
# only those elements that belong to at least one physical group. 
# To force Gmsh to save all elements, 
gmsh.option.setNumber("Mesh.SaveAll", 1)
# ... and save it to disk
gmsh.write('inlet.cgns')
gmsh.write('inlet.su2')


# To visualize the model we can run the graphical user interface with
# `gmsh.fltk.run()'. Here we run it only if "-nopopup" is not provided in the
# command line arguments:
if '-nopopup' not in sys.argv:
    gmsh.fltk.run()    
    
gmsh.finalize()

#--------------------------------------------------------------------------------#
