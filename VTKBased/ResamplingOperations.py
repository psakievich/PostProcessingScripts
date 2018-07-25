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

class Operations:
    '''
    Parent class for handling operations on structured grids
    '''
    def GetKeys(self):
        '''
        Get a list of the fields that are in the exodus dataset
        '''
        try:
            return self.data_np.PointData.keys()
        except:
            print "Must run Initialize first"
            return []

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

class ResampleProcessing(Operations):
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
    def SetTimeStep(self,time):
        '''
        Set the simulation to the specified time
        '''
        self.resample.UpdateTimeStep(time)
        self.resample.Update()
        self.data = self.resample.GetOutput()
    def GetTimeSteps(self):
        '''
        Get a lits of times that are in the exodus dataset
        '''
        try:
            return self.tSteps
        except:
            print "Must run Initialize first"
            return []

class StructuredGridProcessing(Operations):
    '''
    Calls for performing operations on data in *.vts files
    '''
    def __init__(self,fileName):
        self.reader = vtk.vtkXMLStructuredGridReader()
        self.reader.SetFileName(fileName)
        self.reader.Update()
        self.data = self.reader.GetOutput()
        self.data_np = dsa.WrapDataObject(self.data)
    def UpdateFileName(self,fileName):
        self.reader.SetFileName(fileName)
        self.reader.Update()
        self.data = self.reader.GetOutput()

if __name__ == "__main__":
    # set up sampling grid
    radius = 0.5
    height = 1.0
    NX = (64,64,64)
    strucGrid = cg.CreateCylindricalGrid(radius, height, NX)
    
    # perform resampling
    exodusFile = r"/gpfs1/psakiev/PVResampleDatasetBug/exodus.e"
    d = ResampleProcessing(exodusFile,strucGrid)
    d.Initialize()
    tStep=d.GetTimeSteps()
    d.SetTimeStep(tStep[-1])
    keys = d.GetKeys()
    
    # note that we should also do time averaging, but this is an example
    velMean = d.SpatialAverage(d.GetField("velocity_"),0)
    d.InsertField(velMean,"velMean")
    velFluc = d.GetField("velocity_")-velMean
    d.InsertField(velFluc,"velFluc")
    
    # compute a turbulence quantity
    dUdx = d.Gradient("velMean")
    uu = d.SpatialAverage(velFluc[:,0]**2,0)
    vv = d.SpatialAverage(velFluc[:,1]**2,0)
    ww = d.SpatialAverage(velFluc[:,2]**2,0)
    uv = d.SpatialAverage(velFluc[:,0]*velFluc[:,1],0)
    uw = d.SpatialAverage(velFluc[:,0]*velFluc[:,2],0)
    vw = d.SpatialAverage(velFluc[:,1]*velFluc[:,2],0)
    production = dUdx[:,0,0]*uu\
               +(dUdx[:,0,1] + dUdx[:,1,0])*uv\
               +(dUdx[:,0,2] + dUdx[:,2,0])*uw \
               +dUdx[:,1,1]*vv \
               +(dUdx[:,1,2] + dUdx[:,2,1])*vw\
               +dUdx[:,2,2]*ww
               
    # Add these new fields back into the resampled dataset and write a file
    d.InsertField(velFluc,"velFluc")
    d.InsertField(production,"tkeProd")
    d.WriteResultGrid("mean2.vts")

    # More practially, create a plane and output the averaged QOI
    sPlane = cg.CreateCylindricalGrid(radius,height,(NX[1],NX[2],1), indexOrder=['r','z','t'])
    plane_np = dsa.WrapDataObject(sPlane)
    plane_np.PointData.append(d.ExtractPlane(velMean,0,0),"velMean")
    plane_np.PointData.append(d.ExtractPlane(d.SpatialAverage(production,0),0,0),"tkeP")
    writer = vtk.vtkXMLStructuredGridWriter()
    writer.SetInputData(sPlane)
    writer.SetFileName("plane.vts")
    writer.Write()
