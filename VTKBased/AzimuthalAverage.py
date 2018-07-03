# -*- coding: utf-8 -*-
"""
Resample from exodus to vtkStructuredGrid
and perform averaging operations in cylindrical coordinates

@author Phil Sakievich
@email psakiev@sandia.gov
@genesisdate 7/3/2018
"""

import vtk
import CreateGrids as cg
#import MrRealVtk as mrv
#from vtk.numpy_interface import dataset_adapter as dsa

#class ResampleData:
#    '''
#    This class manages the interface for resampling datasets
#    with vtkResampleWithDataset
#    '''
#    def __init__():
#    def SetResampleGrid(self, resampleGrid):
#        '''
#        Supply a grid for which you wish to resample
#        '''
#    def GetTimesteps():
#    def SetTimestep();
        

if __name__ == "__main__":
    radius = 0.5
    height = 1.0
    NX = (20,10,10)
    base = (0,0,0)
    
    strucGrid = cg.CreateCylindricalGrid(base, radius, height,NX)
    exodusFile = r"/gpfs1/psakiev/PVResampleDatasetBug/exodus.e"
    
    eReader = vtk.vtkExodusIIReader()
    eReader.SetFileName(exodusFile)
    eReader.UpdateInformation()
    eReader.SetAllArrayStatus(vtk.vtkExodusIIReader.NODAL,True)
    tSteps = eReader.GetOutputInformation(0). \
        Get(vtk.vtkStreamingDemandDrivenPipeline.TIME_STEPS())
    
    resample = vtk.vtkResampleWithDataSet()
    resample.SetInputData(strucGrid)
    resample.SetSourceConnection(eReader.GetOutputPort())
    
    writer = vtk.vtkXMLStructuredGridWriter()
    
    # write data for each time step
    for i in range(len(tSteps)):
        resample.UpdateTimeStep(tSteps[i])
        writer.SetInputData(resample.GetOutput())
        writer.SetFileName("test_{istep}.vts".format(istep=i))
        writer.Write()
    
    
    