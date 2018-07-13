# -*- coding: utf-8 -*-
"""
Example script for resampling from exodus to vtkStructuredGrid
and perform averaging operations in cylindrical coordinates

@author Phil Sakievich
@email psakiev@sandia.gov
@genesisdate 7/3/2018
"""

import vtk
import AdvancedGridGeneration as cg
from vtk.numpy_interface import dataset_adapter as dsa
import vtk.numpy_interface.algorithms as algs
import numpy as np

class ResampleProcessing:
    '''
    This class allows you to resample an exodus file with a vtkStructuredGrid
    perform operations on the dataset,and save files of the data
    '''
    def __init__(self,exodusFileName, structuredGrid):
        '''
        Initialize with path to exodus file and the structured grid you wish
        to resample over
        '''
        self.eReader = vtk.vtkExodusIIReader()
        self.eReader.SetFileName(exodusFileName)
        self.grid = structuredGrid 
    def Initialize(self,variableList=None):
        '''
        Read the exodus data and resample the dataset onto the specified grid
        '''
        self.eReader.UpdateInformation()
        if variableList is None:
            self.eReader.SetAllArrayStatus(vtk.vtkExodusIIReader.NODAL, True)
        else:
            for var in variableList:
                self.eReader.SetNodeSetArrayStatus(var, True)
        self.tSteps = self.eReader.GetOutputInformation(0).\
            Get(vtk.vtkStreamingDemandDrivenPipeline.TIME_STEPS())
        self.resample = vtk.vtkResampleWithDataSet()
        self.resample.SetInputData(self.grid)
        self.resample.SetSourceConnection(self.eReader.GetOutputPort())
        self.resample.Update()
        self.data = self.resample.GetOutput()
        self.data_np = dsa.WrapDataObject(self.data)
    def GetTimeSteps(self):
        '''
        Get a lits of times that are in the exodus dataset
        '''
        try:
            return self.tSteps
        except:
            print "Must run Initialize first"
            return []
    def GetKeys(self):
        '''
        Get a list of the fields that are in the exodus dataset
        '''
        try:
            return self.data_np.PointData.keys()
        except:
            print "Must run Initialize first"
            return []
    def SetTimeStep(self,time):
        '''
        Set the simulation to the specified time
        '''
        self.resample.UpdateTimeStep(time)
        self.resample.Update()
    def GetField(self,name):
        '''
        Return a pointer to the name of the field specfied
        '''
        ind=self.data_np.PointData.keys().index(name)
        return self.data_np.PointData.GetArray(ind)
    def InsertField(self,array,name):
        '''
        Add a new field with the specified name
        Note that the dimensions of the array must match the arrays in 
        the underlying dataset
        '''
        self.data_np.PointData.append(array,name)
    def WriteResultGrid(self,fileOutName):
        '''
        Write the current structured grid with resampled and added fields
        to the specified file
        '''
        writer = vtk.vtkXMLStructuredGridWriter()
        writer.SetInputData(self.data)
        writer.SetFileName(fileOutName)
        writer.Write()
    def SpatialAverage(self,array, direction, weights=None):
        '''
        Average over the dimension specified by direction.
        direction should be in fortran ordering in terms of 
        the structured grid index.
        Weights can be specified if the grid spacing is not
        uniform
        '''
        direction = abs(direction-2)
        shapeOrg = array.shape
        dims = self.data.GetDimensions()[::-1]
        result = self.ReshapeArray(array, weights)
        mean = np.mean(result,axis=direction)
        if direction == 0:
            for i in range(dims[0]):
                result[i] = mean
        if direction == 1:
            for i in range(dims[1]):
                result[:,i] = mean
        if direction == 2:
            for i in range(dims[2]):
                result[:,:,i] = mean
        return result.reshape(shapeOrg,order='C')
    def Gradient(self,name):
        '''
        return the gradient of the specified field
        '''
        ind=self.data_np.PointData.keys().index(name)
        return algs.gradient(self.data_np.PointData.GetArray(ind))
    def ReshapeArray(self,array, weights=None):
        shapeOrg = array.shape
        result = array.copy()
        if weights is not None:
            result *= weights
        dims = self.data.GetDimensions()[::-1]
        if len(shapeOrg) == 1:
            newShape=dims
        else:
            newShape = [shapeOrg[v] for v in range(len(shapeOrg)-1,0,-1)]
            for i in range(2,-1,-1):
                newShape.append(dims[i])
            newShape = newShape[::-1]
        return result.reshape(newShape,order='C')
    def ExtractPlane(self,array,outPlaneDirection,index):
        '''
        Extract a plane from a 3d array
        outPlaneDirection is index for the normal direction (direction not in the plane)
        index is the disrecte index associated with the particular plane of interest
        '''
        outPlaneDirection = abs(outPlaneDirection-2)
        array_new = self.ReshapeArray(array)
        dims = self.data.GetDimensions()[::-1]
        orgShape = array.shape
        newShape = [orgShape[i] for i in range(len(orgShape)-1,0,-1)]
        if outPlaneDirection == 0:
            newShape.append(dims[1]*dims[2])
            return array_new[index].reshape(newShape[::-1])
        elif outPlaneDirection == 1:
            newShape.append(dims[0]*dims[2])
            return array_new[:,index].reshape(newShape[::-1])
        elif outPlaneDirection ==2:
            newShape.append(dims[1]*dims[0])
            return array_new[:,:,index].reshape(newShape[::-1])
        
if __name__ == "__main__":
    radius = 0.5
    height = 1.0
    NX = (64,20,20)

    strucGrid = cg.CreateCylindricalGrid(radius, height, NX)
    exodusFile = r"/gpfs1/psakiev/PVResampleDatasetBug/exodus.e"
    
    d = ResampleProcessing(exodusFile,strucGrid)
    d.Initialize()
    tStep=d.GetTimeSteps()
    d.SetTimeStep(tStep[-1])
    keys = d.GetKeys()
    velMean = d.SpatialAverage(d.GetField("velocity_"),0)
    d.InsertField(velMean,"velMean")
    velFluc = d.GetField("velocity_")-velMean
    d.InsertField(velFluc,"velFluc")
    d.WriteResultGrid("mean2.vts")
    
    sPlane = cg.CreateCylindricalGrid(radius,height,(NX[1],NX[2],1), indexOrder=['r','z','t'])
    plane_np = dsa.WrapDataObject(sPlane)
    plane_np.PointData.append(d.ExtractPlane(velMean,0,0),"velMean")
    writer = vtk.vtkXMLStructuredGridWriter()
    writer.SetInputData(sPlane)
    writer.SetFileName("plane.vts")
    writer.Write()
    

    
    
    