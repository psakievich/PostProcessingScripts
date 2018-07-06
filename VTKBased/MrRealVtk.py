# -*- coding: utf-8 -*-
"""
Created on Wed Nov  9 13:30:09 2016
Class for interacting with vtk files where all data is R space
@author: psakievi
"""
import modred as mr
import numpy as np
from vtk import vtkStructuredGrid, vtkXMLStructuredGridReader, \
    vtkXMLStructuredGridWriter
from vtk.numpy_interface import dataset_adapter as dsa

class MrVtkVector(mr.Vector):
    def __init__(self,vtkStrGrid):
        self.data=vtkStrGrid
    def __mul__(self,scalar):
        new_data=vtkStructuredGrid()
        new_data.DeepCopy(self.data)
        math_me=dsa.WrapDataObject(self.data)
        math_new=dsa.WrapDataObject(new_data)
        numFlds=len(math_me.PointData.keys())
        for i in range(numFlds):
            math_new.PointData[i][:]=math_me.PointData[i][:]*scalar
        return MrVtkVector(new_data)
    def __add__(self, other):
        """Return an object that is self+other for all fields 
        """
        new_data=vtkStructuredGrid()
        new_data.DeepCopy(self.data)
        math_me=dsa.WrapDataObject(self.data)
        math_data=dsa.WrapDataObject(new_data)
        math_other=dsa.WrapDataObject(other.data)
        numFlds=len(math_me.PointData.keys())
        for i in range(numFlds):
            math_data.PointData[i][:]= \
                math_me.PointData[i][:]+ \
                math_other.PointData[i][:]

        return MrVtkVector(new_data)
    def inner_product(self,other):
        weighted_me=self.weighted_copy()
        math_me=dsa.WrapDataObject(weighted_me.data)
        math_other=dsa.WrapDataObject(other.data)
        numFlds=len(math_me.PointData.keys())
        IP=0.0
        for i in range(numFlds):
            IP=IP+np.vdot(np.transpose(math_me.PointData[i][:]), \
                math_other.PointData[i][:])
        return IP
    def power(self,power):
        new_data=vtkStructuredGrid()
        new_data.DeepCopy(self.data)
        math_me=dsa.WrapDataObject(self.data)
        math_new=dsa.WrapDataObject(new_data)
        numFlds=len(math_me.PointData.keys())
        for i in range(numFlds):
            math_new.PointData[i][:]=math_me.PointData[i][:]**power
        return MrVtkVector(new_data)
class MrVtkVecHandle(mr.VecHandle):
    def __init__(self, vec_path, base_handle=None, scale=None):
        mr.VecHandle.__init__(self,base_handle,scale)
        self.vec_path=vec_path
        
    def _get(self):
        reader=vtkXMLStructuredGridReader()
        reader.SetFileName(self.vec_path)
        reader.Update()
        return(MrVtkVector(reader.GetOutput()))
        
    def _put(self,vec):
        writer=vtkXMLStructuredGridWriter()
        writer.SetInputData(vec.data)
        writer.SetFileName(self.vec_path)
        writer.Write()

def point_product(v1,v2):
    new_data=vtkStructuredGrid()
    new_data.DeepCopy(v1.data)
    mv1=dsa.WrapDataObject(v1.data)
    mv2=dsa.WrapDataObject(v2.data)
    mvN=dsa.WrapDataObject(new_data)
    numFlds=len(mv1.PointData.keys())
    for i in range(numFlds):
        mvN.PointData[i][:]=mv1.PointData[i][:]*mv2.PointData[i][:]
    return MrVtkVector(new_data)
def point_division(v1,v2):
    new_data=vtkStructuredGrid()
    new_data.DeepCopy(v1.data)
    mv1=dsa.WrapDataObject(v1.data)
    mv2=dsa.WrapDataObject(v2.data)
    mvN=dsa.WrapDataObject(new_data)
    numFlds=len(mv1.PointData.keys())
    for i in range(numFlds):
        mvN.PointData[i][:]=mv1.PointData[i][:]/mv2.PointData[i][:]
    return MrVtkVector(new_data)
