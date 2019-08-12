"""
Demo of averaging over a spatial dimension for 
parallel data sets

To use make sure your dataset is selected in ParaView before running
(i.e it needs to be the active source)

This script assumes your data set can be decomposed using
slabs in the (d+1)%3 direction where d is the dimension
you will be averaging across.

If the dimensions are too large then this could be modified
to use pencil decomposition, but has not been tested

author: @psakiev
email: psakiev@sandia.gov
date: 8/2/2019
"""

"""
###############################################
#  ----- BEGIN USER INPUT ----
###############################################
"""
import os
pythonPathAppend =  os.environ["HOME"]+r'/soft/PostProcessingScripts/VTKBased'
samplingDimensions = [40, 10, 10]
sampleSpacing = [0.25,1,1]
sampleOrigin = [1.0,0,0]
averagingDirection = 1
collapseToPlane = False

"""
###############################################
#  ----- END USER INPUT ----
###############################################
"""

from paraview.simple import *

dataSet = GetActiveSource()

sampleGrid = ProgrammableSource()
sampleGrid.OutputDataSetType = 'vtkImageData'
sampleGrid.PythonPath = "\"{path}\"".format(path=pythonPathAppend)
sampleGrid.ScriptRequestInformation = """import DomainDecomposition
executive = self.GetExecutive()
dims = {sampleDims}
DomainDecomposition.StandardRequestInformation(executive, dims)
""".format(sampleDims=samplingDimensions)
sampleGrid.Script = """import DomainDecomposition
executive = self.GetExecutive()
extent = DomainDecomposition.GetSubExtent(executive,{splitPath})
output.SetExtent(*extent)
output.SetSpacing(*{spacing})
output.SetOrigin(*{origin})""".format(splitPath = [(averagingDirection+1)%3],
        spacing = sampleSpacing, origin = sampleOrigin)

resample = ResampleWithDataset(Input = dataSet, Source = sampleGrid)
resample.CellLocator = 'Static Cell Locator'
resample.UpdatePipeline()
Show(resample)

averageOperator = ProgrammableFilter(Input = resample)
averageOperator.PythonPath = sampleGrid.PythonPath
averageOperator.OutputDataSetType = 'vtkImageData'
averageOperator.RequestInformationScript = """import numpy as np
import DomainDecomposition as DD

executive = self.GetExecutive()
outInfo = executive.GetOutputInformation(0)
inInfo = executive.GetInputInformation(0,0)
inExtent = np.array(inInfo.Get(executive.WHOLE_EXTENT()))
self.averageAxis = {aa}
if self.averageAxis > 2 or self.averageAxis <0:
    raise Exception("averageAxis must be 0,1 or 2")
if {c2p}:
    if self.averageAxis == 0:
        inExtent[0:2]=0
    elif self.averageAxis ==1: 
        inExtent[2:4] = 0
    elif self.averageAxis ==2:
        inExtent[4:6] = 0
    else:
        raise Exception("averageAxis must be 0,1 or 2")

globDims = inExtent[1::2]+1
DD.StandardRequestInformation(executive, globDims)""".format(aa = averagingDirection,
        c2p = collapseToPlane)
averageOperator.RequestUpdateExtentScript = """ pass """
averageOperator.Script = """import vtk
import numpy as np
from vtk.numpy_interface import dataset_adapter as dsa
import DomainDecomposition as DD

executive = self.GetExecutive()
my_extent = DD.GetSubExtent(executive, [(self.averageAxis+1)%3])

# Do operations on the grid
outputGrid = self.GetOutput()
outputGrid.SetExtent(my_extent)

inputGrid = self.GetInput()
inputMath = dsa.WrapDataObject(inputGrid)
outputMath = dsa.WrapDataObject(outputGrid)

spatialDims = inputMath.GetDimensions()
totalDims = np.product(spatialDims)
arraySize = totalDims / spatialDims[self.averageAxis]

for key in inputMath.PointData.keys():
    if key.find('vtk') is not -1:
        continue
    array = inputMath.PointData[key]
    orgShape = array.shape
    reshape = arraySize
    if len(array.shape) == 2:
        dArray = [d for d in spatialDims[::-1]]
        dArray.append(array.shape[1])
        array = array.reshape(dArray, order='C')
        newArray = np.mean(array, axis=2-self.averageAxis,keepdims=True)
        if not {c2p}:
            b = np.ones(dArray)
            newArray = b*newArray
            reshape = orgShape[0]
        newArray = dsa.numpyTovtkDataArray(
            newArray.ravel(order='A').reshape(
            reshape,orgShape[1]), array_type=10)
    if len(array.shape) == 1:
        array = array.reshape(spatialDims[::-1])
        newArray = np.mean(array,axis=2-self.averageAxis,keepdims=True)
        if not {c2p}:
            b = np.ones(spatialDims[::-1])
            newArray = b* newArray
        newArray = dsa.numpyTovtkDataArray(newArray.flatten(order='A'), array_type=10)
    newArray.SetName(key)
    outputMath.PointData.AddArray(newArray)""".format(c2p=collapseToPlane)

HideAll()
Show(averageOperator)

