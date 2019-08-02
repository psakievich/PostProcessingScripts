"""
This module contains common functions for doing domain
decomposition and mpi support in VTK pipelines

author @psakiev
email psakiev@sandia.gov

"""

import vtk
import numpy as np

def GetSubExtent(executive, splitPath):
    """
    This will return a parallel extent for each rank. It
    should be called in the RequestData call (script in
    ParaView programmable filters and sources)

    executive - the vtkExecutive required for this.  For
                a vtkAlgorithm one should pass self.GetExecutive()

    splitPath - the path you wish to split the data set along i.e.
                [0] is the x direction, [0,1] is a pencil split along 
                the x-y direction, [0,1,2] is block split x-y-z
    """
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
    extCont.SetSplitPath(4, splitPath)
    extCont.SetWholeExtent(outInfo.Get(executive.WHOLE_EXTENT()))
    extCont.SetNumberOfPieces(nranks)
    extCont.SetPiece(rank)
    extCont.PieceToExtent()
    outInfo.Set(executive.UPDATE_EXTENT(),
            extCont.GetExtent(), 6)
    
    return extCont.GetExtent()

def StandardRequestInformation(executive, globalDims):
    """
    This is a standard RequestInformation call
    for generating structured grids in parallel.
    
    globalDims - the total dimensions desired for the grid
    """
    outInfo = executive.GetOutputInformation(0)
    outInfo.Set(executive.WHOLE_EXTENT(), 0, globalDims[0]-1,
            0, globalDims[1]-1,
            0, globalDims[2]-1)
    outInfo.Set(vtk.vtkAlgorithm.CAN_PRODUCE_SUB_EXTENT(), 1)