# -*- coding: utf-8 -*-
"""
Example script for resampling from exodus to vtkStructuredGrid
and perform averaging operations in cylindrical coordinates

@author Phil Sakievich
@email psakiev@sandia.gov
@genesisdate 7/3/2018
"""

import vtk
import CreateGrids as cg
import CreateGrids_1 as cg1
from vtk.numpy_interface import dataset_adapter as dsa
import numpy as np
reload(cg1)

'''
TODO: Projection to cylindrical coordinates
TODO: Time averaging
TODO: Fluctuations
TODO: Energy Terms
TODO: Average output on a plane or whole domain
'''

if __name__ == "__main__":
    radius = 0.5
    height = 1.0
    NX = (64,20,20)

    strucGrid = cg1.CreateCylindricalGrid(radius, height, NX)
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
    resample.UpdateTimeStep(tSteps[-1])
    resample.Update()
    data = resample.GetOutput()
    data_math = dsa.WrapDataObject(data)
    
    # Add mean
    keys_org = data_math.PointData.keys()
    index = 0
    for key in keys_org:
        key_mean = "mean_"+key
        key_fluc = "fluc_"+key
        meanArray = data_math.PointData.GetArray(index).copy()
        flucArray = meanArray.copy()
        for i in range(NX[1]*NX[2]):
            # loop over r-z locations and write the mean
            # data is contiguous in theta direction
            if (len(meanArray.shape)==1):
                meanArray[i*NX[0]:(i+1)*NX[0]]=np.mean(\
                          data_math.PointData.GetArray(index)[i*NX[0]:(i+1)*NX[0]]\
                          )
                flucArray[i*NX[0]:(i+1)*NX[0]]-=meanArray[i*NX[0]:(i+1)*NX[0]]
            elif (len(meanArray.shape)==2):
                for j in range(meanArray.shape[-1]):
                    meanArray.T[j,i*NX[0]:(i+1)*NX[0]]=np.mean(\
                                data_math.PointData.GetArray(index).T[j,i*NX[0]:(i+1)*NX[0]]\
                                )
                    flucArray.T[j,i*NX[0]:(i+1)*NX[0]]-=meanArray.T[j,i*NX[0]:(i+1)*NX[0]]
            else:
                print "Skipping array "+key+" because it has more than 2 vtk indicies"
        data_math.PointData.append(meanArray,key_mean)
        data_math.PointData.append(flucArray,key_fluc)
        index+=1
        print(index,key,key_mean,key_fluc)
    
    
    
    # write data for each time step
    writer = vtk.vtkXMLStructuredGridWriter()
    writer.SetInputData(data)
    writer.SetFileName("mean.vts")
    writer.Write()
    
    
    