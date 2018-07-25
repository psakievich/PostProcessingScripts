#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 23:04:02 2018

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
    nSteps=len(tStep)
    keys = d.GetKeys()
    writer = vtk.vtkXMLStructuredGridWriter()
    #writer.SetNumberOfTimeSteps(nSteps)
    ext = writer.GetDefaultFileExtension()
    writer.SetInputData(d.data)
    f=open("tsteps.txt","w")
    #writer.Start()
    for i in range(nSteps):
        writer.SetFileName("data_{}.".format(i)+ext)
        print "time is {}".format(tStep[i])
        d.SetTimeStep(tStep[i])
        writer.Write()
        f.write(str(tStep[i])+"\n")
    #writer.Stop()
    f.close()