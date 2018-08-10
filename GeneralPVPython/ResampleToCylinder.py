'''
Example on how to Resample an exouds file as specified by user
to a cylindrical grid.

Outputs a file for each timestep in the file

@author Phil Sakievich
@email psakiev@sandia.gov
@genesisdate 8/10/2018
'''

from paraview.simple import *
import sys, os
sys.path.append(os.environ["HOME"]+r"/PostProcessingScripts/GeneralPVPython")
import GeneralIO
import numpy as np

renderView = GetActiveViewOrCreate("RenderView")
# stuff for createing a structured grid to resample on
# via programmable source
radius = 0.5
height = 1.0
nPoints = (20,10,10)
pPath = os.environ["HOME"]+r"/PostProcessingScripts/VTKBased"

# Additional user inputs
oFileBaseName = os.environ["PWD"]+"/resampleTest"
eFileBaseName = r"/gpfs1/psakiev/PVResampleDatasetBug/exodus.e"
eNumProcs = None
firstTimeStep = 46

# create the programmable source
grid = ProgrammableSource( \
  Script = \
    "import AdvancedGridGeneration as cg\n" + \
    "output.ShallowCopy(cg.CreateCylindricalGrid({r},{h},{np}))".format(\
    r=radius, h=height, np=nPoints), \
  ScriptRequestInformation = \
    "executive = self.GetExecutive()\n" +\
    "outInfo = executive.GetOutputInformation(0)\n" +\
    "outInfo.Set(executive.WHOLE_EXTENT(), 0, {nx}, 0, {ny}, 0, {nz})".format(\
    nx=nPoints[0]-1, ny=nPoints[1]-1, nz=nPoints[2]-1),\
  PythonPath = "'{PATH}'".format(PATH=pPath),\
  OutputDataSetType=r"vtkStructuredGrid"
    )
viewGrid=Show(grid,renderView)
viewGrid.SetRepresentationType("Surface With Edges")

# unstructured data set
exodus = GeneralIO.ReadExodus(eFileBaseName, eNumProcs)
tsteps = exodus.TimestepValues
np.savetxt(oFileBaseName+"_tsteps.txt",tsteps,delimiter=",")

# now do the resampling
resample = ResampleWithDataset(\
  Input = exodus, \
  Source = grid \
#  PassPointArrays = True \
  )
Hide(grid)
resampleView=Show(resample,renderView)
resampleView.SetRepresentationType("Surface")

# write out new data as timeseries
writer = GeneralIO.WriteGeneral(XMLStructuredGridWriter,resample,oFileBaseName,returnWriter=True)
writer.Filenamesuffix = "_%.3d"
writer.Firsttimestep = firstTimeStep
writer.Writetimestepsasfileseries = True
writer.UpdatePipeline()

