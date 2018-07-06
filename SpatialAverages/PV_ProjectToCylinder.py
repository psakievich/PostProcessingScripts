'''
Example of how to create programable source in paraview
and resample your dataset.
In this case the key feature is going from unstructured
to a structured grid format for post-processing

Additional filters can be applied on top of this in paraview
if desired however for point by point analysis it might be 
simpler to just work in pure vtk.  

See VTKBased directory for examples on how to do this.

@author Phil Sakievich
@email psakiev@sandia.gov
@genesisdate 7/6/2018
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