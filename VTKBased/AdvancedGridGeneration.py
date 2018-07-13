'''
Helper functions for creating some basic vtkGrids

@author Phil Sakievich
@email psakiev@sandia.gov
@date 5/25/2018
'''

import vtk
import numpy as np

def CreateCylindricalGrid(radius, height, nPoints, rotation = (0,0,0), \
                          translation=(0,0,0), indexOrder = ["t","r","z"]):
  '''
  Create a vtkStructured grid of a cylinder
  The default is a cylinder with in the z-direction centered on the 
  origin.  Translation and rotations can be specified
  
  params:
    radius - Radius of grid
    height - height of cylinder
    nPoints - tuple length 3 with sample rate for each dimension

  kword:
    rotation - angle to rotate about the axis' (tuple length 3)
    translation - distance to translate the grid (tuple length 3)
    indexOrder - which order to align the indicies, t=theta, r=radial, z=vertical
                 default is ['t','r','z'] because users will likely want to average
                 over theta first index varies fastest
  '''
  # have to flip ordering to work with meshgrid
  indexOrder = indexOrder[::-1]
  nPoints = nPoints[::-1]  
  # Set up points
  points = vtk.vtkPoints()
  totalNumberOfPoints = 1
  for nX in nPoints:
    totalNumberOfPoints *= nX
    
  points.Allocate(totalNumberOfPoints)
  
  iT = indexOrder.index("t")
  iR = indexOrder.index("r")
  iZ = indexOrder.index("z")
  
  # Determine discretization
  dX=np.ones(3,dtype=float)
  dX[iT] = 2.0*np.pi/float(nPoints[iT])
  if nPoints[iR]>1:
      dX[iR] = radius/float(nPoints[iR]-1)
  if nPoints[iZ]>1:
      dX[iZ] = height/float(nPoints[iZ]-1)
  
  theta_b = np.arange(0, np.pi*2.0, dX[iT])
  radius_b = np.linspace(0,radius,nPoints[iR])
  z_b = np.linspace(0, height, nPoints[iZ])
  
  # fill list based off ordering
  x_b = [[],[],[]]
  x_b[iT]=theta_b
  x_b[iR]=radius_b
  x_b[iZ]=z_b
  
  x_c = np.meshgrid(x_b[0],x_b[1],x_b[2],indexing='ij')
  
  for i in range(3):
      x_c[i]=x_c[i].flatten()
  
  # Assign points with transaltion to cartesian coords
  for n in range(totalNumberOfPoints):
    x = x_c[iR][n]*np.cos(x_c[iT][n])
    y = x_c[iR][n]*np.sin(x_c[iT][n])
    z = x_c[iZ][n]
    points.InsertNextPoint(x,y,z)

  # Create grid
  grid = vtk.vtkStructuredGrid()
  # flip ordering back to make sure dimensions of structured grid are correct
  nPoints= nPoints[::-1]
  grid.SetDimensions(nPoints)
  grid.SetPoints(points)
  # Perform transformations
  tf = vtk.vtkTransform()
  tf.RotateX(rotation[0])
  tf.RotateY(rotation[1])
  tf.RotateZ(rotation[2])
  tf.Translate(translation)
  tff = vtk.vtkTransformFilter()
  tff.SetInputData(grid)
  tff.SetTransform(tf)
  tff.Update()
  return tff.GetStructuredGridOutput()