"""
Demo of averaging over a spatial dimension for 
parallel data sets

To use make sure your dataset is selected in ParaView before running
(i.e it needs to be the active source)

This script assumes your data set can be decomposed using
slabs in the (d+1)%3 direction where d is the dimension
you will be averaging across.

!!!If your sampling in the parallel decomposition direction
is less than the number of processors then paraview will
revert to pencil/block decomposition and your results will
be incorrect.!!!!

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
import numpy as np
samplingDimensions = np.array([1001, 1001, 101])
averagingDirection = 2
collapseToPlane = False

"""
###############################################
#  ----- END USER INPUT ----
###############################################
"""

from paraview.simple import *
pythonPathAppend =  ""#os.environ["HOME"]+r'/soft/PostProcessingScripts/VTKBased'

dataSet = GetActiveSource()
bounds  = np.array(dataSet.GetDataInformation().GetBounds())
deltas = bounds[1::2]-bounds[0::2]
sampleSpacing = deltas/(samplingDimensions-1)
sampleOrigin = np.array([0.0,0,0])

sampleGrid = ProgrammableSource()
sampleGrid.OutputDataSetType = 'vtkImageData'
sampleGrid.PythonPath = "\"{path}\"".format(path=pythonPathAppend)
sampleGrid.ScriptRequestInformation = """
executive = self.GetExecutive()
dims = {sampleDims}
def StandardRequestInformation(executive, globalDims):
    outInfo = executive.GetOutputInformation(0)
    outInfo.Set(executive.WHOLE_EXTENT(), 0, globalDims[0]-1,
            0, globalDims[1]-1,
            0, globalDims[2]-1)
    outInfo.Set(vtk.vtkAlgorithm.CAN_PRODUCE_SUB_EXTENT(), 1)
StandardRequestInformation(executive, dims)
""".format(sampleDims=np.array2string(samplingDimensions, separator=','))
sampleGrid.Script = """
import numpy as np
def GetSubExtent(executive, splitPath):
    controller = vtk.vtkMultiProcessController.GetGlobalController()
    if not controller:
        rank = 0
        nranks = 1
    else:
        rank = controller.GetLocalProcessId()
        nranks = controller.GetNumberOfProcesses()
    
    outInfo = executive.GetOutputInformation(0)
    
    wholeExtent = np.array(outInfo.Get(executive.WHOLE_EXTENT()))
    globDims = wholeExtent[1::2]-wholeExtent[0::2]+1
    extCont = vtk.vtkExtentTranslator()
    extCont.SetSplitPath(len(splitPath), splitPath)
    extCont.SetWholeExtent(outInfo.Get(executive.WHOLE_EXTENT()))
    extCont.SetNumberOfPieces(nranks)
    extCont.SetPiece(rank)
    extCont.PieceToExtent()
    outInfo.Set(executive.UPDATE_EXTENT(),
            extCont.GetExtent(), 6)
    
    return extCont.GetExtent()
executive = self.GetExecutive()
extent = GetSubExtent(executive,{splitPath})
output.SetExtent(*extent)
output.SetSpacing(*{spacing})
output.SetOrigin(*{origin})""".format(splitPath = [(averagingDirection+1)%3],
        spacing = np.array2string(sampleSpacing, separator=','), 
        origin = np.array2string(sampleOrigin, separator=','))

resample = ResampleWithDataset(Input = dataSet, Source = sampleGrid)
resample.CellLocator = 'Static Cell Locator'
resample.UpdatePipeline()
Show(resample)

averageOperator = ProgrammableFilter(Input = resample)
averageOperator.PythonPath = sampleGrid.PythonPath
averageOperator.OutputDataSetType = 'vtkImageData'
averageOperator.RequestInformationScript = """import numpy as np

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
def StandardRequestInformation(executive, globalDims):
    outInfo = executive.GetOutputInformation(0)
    outInfo.Set(executive.WHOLE_EXTENT(), 0, globalDims[0]-1,
            0, globalDims[1]-1,
            0, globalDims[2]-1)
    outInfo.Set(vtk.vtkAlgorithm.CAN_PRODUCE_SUB_EXTENT(), 1)
StandardRequestInformation(executive, globDims)""".format(aa = averagingDirection,
        c2p = collapseToPlane)
averageOperator.RequestUpdateExtentScript = """pass"""
averageOperator.Script = """import vtk
import numpy as np
from vtk.numpy_interface import dataset_adapter as dsa

executive = self.GetExecutive()
def GetSubExtent(executive, splitPath):
    controller = vtk.vtkMultiProcessController.GetGlobalController()
    if not controller:
        rank = 0
        nranks = 1
    else:
        rank = controller.GetLocalProcessId()
        nranks = controller.GetNumberOfProcesses()
    
    outInfo = executive.GetOutputInformation(0)
    
    wholeExtent = np.array(outInfo.Get(executive.WHOLE_EXTENT()))
    globDims = wholeExtent[1::2]-wholeExtent[0::2]+1
    extCont = vtk.vtkExtentTranslator()
    extCont.SetSplitPath(len(splitPath), splitPath)
    extCont.SetWholeExtent(outInfo.Get(executive.WHOLE_EXTENT()))
    extCont.SetNumberOfPieces(nranks)
    extCont.SetPiece(rank)
    extCont.PieceToExtent()
    outInfo.Set(executive.UPDATE_EXTENT(),
            extCont.GetExtent(), 6)
    
    return extCont.GetExtent()
my_extent = GetSubExtent(executive, [(self.averageAxis+1)%3])

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

