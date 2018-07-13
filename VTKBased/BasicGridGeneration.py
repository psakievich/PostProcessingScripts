'''
Helper functions for creating some basic vtkGrids

@author Phil Sakievich
@email psakiev@sandia.gov
@date 5/25/2018
'''

import vtk
import numpy as np

def CreateCylindricalGrid(radius, height, nPoints):
  '''
  Create a vtkStructured grid of a cylinder
  
  params:
    bottomCenter - tuple length 3 that holds the coordinates at bottom 
                   center of the cylinder
    radius - Radius of grid
    height - height of cylinder
    nPoints - tuple length 3 with sample rate for each dimension
    
  TODO: add suport for arbitrary orientation of the cylinder
  TODO: add to a class that has a helper function for getting angle
  '''
  # Set up points
  points = vtk.vtkPoints()
  points.SetNumberOfPoints = nPoints
  totalNumberOfPoints = 1
  for nX in nPoints:
    totalNumberOfPoints *= nX
  points.Allocate(totalNumberOfPoints)
  # Determine discretization
  dX = [ \
     2.0*np.pi/float(nPoints[0]), \
     radius/float(nPoints[1]-1), \
     height/float(nPoints[2]-1)]
  # Assign points with theta with theta as the contiguous direction
  for nZ in range(nPoints[2]):
    z = dX[2]*nZ
    for nR in range(nPoints[1]):
      for nT in range(nPoints[0]):
        theta = nT*dX[0]
        x = nR*dX[1]*np.cos(theta)
        y = nR*dX[1]*np.sin(theta)
        points.InsertNextPoint(x,y,z)
  # Create grid and return it
  grid = vtk.vtkStructuredGrid()
  grid.SetDimensions(nPoints)
  grid.SetPoints(points)
  return grid