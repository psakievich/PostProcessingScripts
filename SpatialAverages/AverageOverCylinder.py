'''
This file will average results over a cylindrical grid with 
user defined resolution

@author Phil Sakievich
@email psakiev@.sandia.gov
@date 6/28/18
'''

from paraview.simple import *
import sys,os

def ResampleGrid(radius, height, bottomCenter, normal, resolution, pythonPath):
  # create the programmable source
  grid = ProgrammableSource( \
    Script = \
      "import CreateGrids as cg\n" + \
      "output.ShallowCopy(cg.CreateCylindricalGrid({bc},{nrml},{r},{h},{np}))".format(\
      bc = bottomCenter, nrml=normal, r=radius, h=height, np=nPoints), \
    ScriptRequestInformation = \
      "executive = self.GetExecutive()\n" +\
      "outInfo = executive.GetOutputInformation(0)\n" +\
      "outInfo.Set(executive.WHOLE_EXTENT(), 0, {nx}, 0, {ny}, 0, {nz})".format(\
      nx=resolution[0]-1, ny=resolution[1]-1, nz=resolution[2]-1),\
    PythonPath = pythonPath,\
    OutputDataSetType=r"vtkStructuredGrid"
      )
  return grid
