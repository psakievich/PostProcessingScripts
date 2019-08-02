#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 20:24:27 2018

@author: psakiev
"""

import AdvancedGridGeneration as cg
import ResamplingOperations as ro
import vtk

if __name__ == "__main__":
    # set up sampling grid
    radius = 0.5
    height = 1.0
    NX = (10,10,10)
    strucGrid = cg.CreateCylindricalGrid(radius, height, NX)
    
    # perform resampling
    exodusFile = r"/gpfs1/psakiev/PVResampleDatasetBug/exodus.e"
    d = ro.ResampleProcessing(exodusFile,strucGrid)
    d.Initialize()
    tStep=d.GetTimeSteps()
    nSteps=5
    keys = d.GetKeys()
    writer = vtk.vtkXMLStructuredGridWriter()
    writer.SetNumberOfTimeSteps(nSteps)
    ext = writer.GetDefaultFileExtension()
    writer.SetFileName("testing."+ext)
    writer.SetInputData(d.data)
    writer.Start()
    for i in range(nSteps):
        print "time is {}".format(tStep[i])
        d.SetTimeStep(tStep[i])
        writer.WriteNextTime(tStep[i])
    writer.Stop()
    
    reader = vtk.vtkXMLStructuredGridReader()
    reader.SetFileName(writer.GetFileName())
    reader.Update()
    
    print "reader number of timesteps",reader.GetNumberOfTimeSteps()
    print "reader number of points",reader.GetNumberOfPoints()
    print "reader number of point arrays",reader.GetNumberOfPointArrays()