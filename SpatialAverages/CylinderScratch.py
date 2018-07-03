'''
This shows the bug for writing a structured grid in parallel
when the writer has a ResampleToDataset filter as a source
The resulting pvts file appears to have some corruption that
generates a segfault when it is read.

I was unable to find any glaring errors via visual inspection of the xml files
'''

from paraview.simple import *
import sys, os
#import CreateGrids as cg

renderView = GetActiveViewOrCreate("RenderView")

# stuff for createing a structured grid to resample on
# via programmable source
radius = 0.5
height = 1.0
bottomCenter = (0,0,0)
nPoints = (20,10,10)

# create the programmable source
grid = ProgrammableSource( \
  Script = \
    "import CreateGrids as cg\n" + \
    "output.ShallowCopy(cg.CreateCylindricalGrid({bc},{r},{h},{np}))".format(\
    bc = bottomCenter, r=radius, h=height, np=nPoints), \
  ScriptRequestInformation = \
    "executive = self.GetExecutive()\n" +\
    "outInfo = executive.GetOutputInformation(0)\n" +\
    "outInfo.Set(executive.WHOLE_EXTENT(), 0, {nx}, 0, {ny}, 0, {nz})".format(\
    nx=nPoints[0]-1, ny=nPoints[1]-1, nz=nPoints[2]-1),\
  PythonPath = 'r"/gpfs1/psakiev/PVResampleDatasetBug"',\
  OutputDataSetType=r"vtkStructuredGrid"
    )
viewGrid=Show(grid,renderView)
viewGrid.SetRepresentationType("Surface With Edges")
# write the programable source
#writer1 = XMLPStructuredGridWriter(Input=grid)
#writer1.FileName = "baseGrid.pvts"
#writer1.UpdatePipeline()
# read this file with no segfault issues
#reader1 = XMLPartitionedStructuredGridReader(FileName = "baseGrid.pvts")
#reader1.UpdatePipeline()

# unstructured data set
exodusFilename = r"/gpfs1/psakiev/PVResampleDatasetBug/exodus.e"
exodus = ExodusIIReader(FileName = exodusFilename)
exodus.SelectAllVariables()
exodus.UpdatePipeline()

# now do the resampling
resample = ResampleWithDataset(\
  Input = exodus, \
  Source = grid \
#  PassPointArrays = True \
  )
Hide(grid)
resampleView=Show(resample,renderView)
resampleView.SetRepresentationType("Surface")
# Write the data
#writer2 = XMLPStructuredGridWriter(Input=resample)
#writer2.FileName = "resample.pvts"
#writer2.UpdatePipeline() 
#wait = input("Type a number to see the seg fault occur")
# Try to read the data
#reader2 = XMLPartitionedStructuredGridReader(FileName="resample.pvts")
# Seg fault occurs when we try to access any member of the reader object
#reader2.UpdatePipeline()