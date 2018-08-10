#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  3 11:37:28 2018
Test resampling operations

@author: psakiev
"""

import ResamplingOperations as ro
import AdvancedGridGeneration as cg
from vtk.numpy_interface import dataset_adapter as dsa
import numpy as np
import unittest

class OperationsFixture(ro.Operations):
    '''
    Class for easy testing of the operations
    '''
    def __init__(self,grid):
        self.data = grid
        self.data_np = dsa.WrapDataObject(self.data)
        
class TestSampleOperations(unittest.TestCase):
    '''
    Class for unit testing the operations 
    '''
    def setUp(self):
        self.radius = 0.5
        self.height = 1.0
        self.NX = (6,5,4)
        self.grid = cg.CreateCylindricalGrid(self.radius, self.height, self.NX)
        self.processor = OperationsFixture(self.grid)
        
    def test_ReshapeArray(self):
        points = self.processor.data_np.GetPoints()
        self.assertEqual(points.shape,(self.NX[0]*self.NX[1]*self.NX[2],3))
        reshapePoints = self.processor.ReshapeArray(points)
        # test reshape indexing matches 
        self.assertEqual(reshapePoints.shape,(self.NX[0],self.NX[1],self.NX[2],3))
        
        for k in range(self.NX[2]):
            for j in range(self.NX[1]):
                for i in range(self.NX[0]):
                    self.assertTrue(
                                     (points[i+j*self.NX[0]+k*self.NX[1]*self.NX[0]]==
                                     reshapePoints[i,j,k]).all())
        self.assertEqual(reshapePoints[:,:,:,0].all(),
                         self.processor.ReshapeArray(points[:,0]).all())
        self.assertTrue(len(points[:,0].shape)==1)
        
    def test_VectorPlanarAverage(self):
        temp = self.processor.data_np.GetPoints()
        vector = temp.copy()
        for i in range(temp.shape[0]):
            r,theta = np.sqrt(temp[i,0]**2+temp[i,1]**2),np.arctan(temp[i,1]/temp[i,0])
            vector[i,0],vector[i,1]=theta,r
        vector_RS = self.processor.ReshapeArray(vector)
        
        # what we want the average to be
        tAvg = np.mean(vector_RS[:,0,0,0])
        rAvg = np.mean(vector_RS[0,:,0,1])
        zAvg = np.mean(vector_RS[0,0,:,2])

        # test generating the average
        rTest = self.processor.SpatialAverage(vector,1)
        tTest = self.processor.SpatialAverage(vector,0)
        zTest = self.processor.SpatialAverage(vector,2)
        
        self.assertEqual(rTest.shape,vector.shape)
        self.assertTrue((rAvg==rTest[:,1]).all())
        self.assertTrue((tAvg==tTest[:,0]).all())
        self.assertTrue((zAvg==zTest[:,2]).all())
        
    def test_ExtractPlane(self):
        temp = self.processor.data_np.GetPoints()
        plane = self.processor.ExtractPlane(temp,0,0)
        self.assertEqual(plane.shape,(self.NX[2]*self.NX[1],3))
        for j in range(self.NX[2]):
            for i in range(self.NX[1]):
                index1 = i+j*self.NX[1]
                index2 = i*self.NX[0]+j*self.NX[0]*self.NX[1]
                p =self.grid.GetPoint(index2)
                self.assertTrue((plane[index1]
                ==
                p ).all(),
                "EXPECT {} ACTUAL {} (I,J)=({},{})".format(p,plane[index1],i,j))
            
        

if __name__ == "__main__":
    unittest.main()