#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 14:04:04 2018

@author: psakiev
"""

import ResamplingOperations as ro
import vtk
from vtk.numpy_interface import dataset_adapter as dsa
import AdvancedGridGeneration as cg
import numpy as np

nFiles = 48
baseFile = "data_{}.vts"
inputFiles = [baseFile.format(i) for i in range(nFiles)]
start = 4
stop = nFiles

# compute average
tsteps = np.loadtxt("tsteps.txt")
weights = np.ones(len(tsteps))/float(stop-start) #TODO temporal weights

grid = ro.StructuredGridProcessing(inputFiles[0])
points = grid.data_np.GetPoints()
x,y = (points[:,0],points[:,1])
r = np.sqrt(x**2+y**2)

# jacobian terms
drdx = x/r #cos(theta)
drdy = y/r #sin(theta)
dthetadx = -drdy/r #-sin(theta)/r
dthetady = drdx/r #cos(theta)/r

def u_tran(vec):
    copy = vec.copy()
    copy[:,0]=vec[:,0]*drdx+vec[:,1]*drdy
    copy[:,1]=vec[:,0]*dthetadx+vec[:,1]*dthetady
    return copy

U = grid.GetField("velocity_")*weights[0]
Rho = grid.GetField("density")*weights[0]

for i in range(start+1,stop):
    grid.UpdateFileName(inputFiles[i])
    U += grid.GetField("velocity_")*weights[i]
    Rho += grid.GetField("density")*weights[i]

U = grid.SpatialAverage(U,0)
Rho = grid.SpatialAverage(Rho,0)

# compute fluc terms
uu = U[:,0].copy()*0.0
vv = uu.copy()
ww = uu.copy()
uv = uu.copy()
uw = uu.copy()
vw = uu.copy()

# time average loop
for i in range(start,stop):
    grid.UpdateFileName(inputFiles[i])
    u=grid.GetField("velocity_")-U
    uu += u[:,0]**2*weights[i]
    vv += u[:,1]**2*weights[i]
    ww += u[:,2]**2*weights[i]
    uv += u[:,0]*u[:,1]*weights[i]
    uw += u[:,0]*u[:,2]*weights[i]
    vw += u[:,1]*u[:,2]*weights[i]

# Spatial averages
uu = grid.SpatialAverage(uu,0)
vv = grid.SpatialAverage(vv,0)
ww = grid.SpatialAverage(ww,0)
uv = grid.SpatialAverage(uv,0)
uw = grid.SpatialAverage(uw,0)
vw = grid.SpatialAverage(vw,0)
    
# all done with file iterations so treat grid as a constant
grid.InsertField(U,"U")
grid.InsertField(Rho,"Rho")    

# transformations
Ucyl = u_tran(U)

#cartesian coords
dUdx = grid.Gradient("U")

production = dUdx[:,0,0]*uu\
               +(dUdx[:,0,1] + dUdx[:,1,0])*uv\
               +(dUdx[:,0,2] + dUdx[:,2,0])*uw \
               +dUdx[:,1,1]*vv \
               +(dUdx[:,1,2] + dUdx[:,2,1])*vw\
               +dUdx[:,2,2]*ww
               
NX = grid.data.GetDimensions()
# More practially, create a plane and output the averaged QOI
sPlane = cg.CreateCylindricalGrid(0.5,1.0,(NX[1],NX[2],1), indexOrder=['r','z','t'])
plane_np = dsa.WrapDataObject(sPlane)
plane_np.PointData.append(grid.ExtractPlane(Ucyl,0,0),"velMean")
plane_np.PointData.append(grid.ExtractPlane(grid.SpatialAverage(production,0),0,0),"tkeP")
writer = vtk.vtkXMLStructuredGridWriter()
writer.SetInputData(sPlane)
writer.SetFileName("plane.vts")
writer.Write()