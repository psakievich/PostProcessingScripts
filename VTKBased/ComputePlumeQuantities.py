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
start = 0
stop = nFiles

# compute average
tsteps = np.loadtxt("tsteps.txt")
deltaT = tsteps[stop-1]-tsteps[start]
# timestep weighting ignores first step
weights = tsteps.copy()
for i in range(start,stop):
    if i>0:
        weights[i]-=tsteps[i-1]
    else:
        weights[i] = 0.0
weights /= deltaT

grid = ro.StructuredGridProcessing(inputFiles[start])
points = grid.data_np.GetPoints()
x,y = (points[:,0],points[:,1])
r = np.sqrt(x**2+y**2)
theta = np.arctan2(y,x)
where_nans = np.isnan(theta)
theta[where_nans]=0.0

# jacobian terms
drdx = np.cos(theta)#x/r #cos(theta)
drdy = np.sin(theta)#y/r #sin(theta)
dthetadx = -drdy/r #-sin(theta)/r
dthetady = drdx/r #cos(theta)/r

def cart_to_cyl(vec):
    copy = vec.copy()
    copy[:,0]=vec[:,0]*drdx+vec[:,1]*drdy
    copy[:,1]=vec[:,0]*dthetadx+vec[:,1]*dthetady
    return copy
def cyl_to_cart(vec):
    copy=vec.copy()
    copy[:,0]=vec[:,0]*drdx-r*drdy*vec[:,1]
    copy[:,1]=vec[:,0]*drdy+r*drdx*vec[:,1]
    return copy

U = grid.GetField("velocity_")*weights[start]
Rho = grid.GetField("density")*weights[start]

for i in range(start+1,stop):
    grid.UpdateFileName(inputFiles[i])
    U += grid.GetField("velocity_")*weights[i]
    Rho += grid.GetField("density")*weights[i]
    
Ucyl=cart_to_cyl(U)
Ucyl = grid.SpatialAverage(Ucyl,0)
U = cyl_to_cart(Ucyl)
Rho = grid.SpatialAverage(Rho,0)    


# compute fluc terms
uu = U[:,0].copy()*0.0
vv = uu.copy()*0.0
ww = uu.copy()*0.0
uv = uu.copy()*0.0
uw = uu.copy()*0.0
vw = uu.copy()*0.0
bprod = uu.copy()*0.0

# time average loop
for i in range(start,stop):
    grid.UpdateFileName(inputFiles[i])
    u=grid.GetField("velocity_")-U
    rho = grid.GetField("density")-Rho
    uu += u[:,0]**2*weights[i]
    vv += u[:,1]**2*weights[i]
    ww += u[:,2]**2*weights[i]
    uv += u[:,0]*u[:,1]*weights[i]
    uw += u[:,0]*u[:,2]*weights[i]
    vw += u[:,1]*u[:,2]*weights[i]
    bprod += u[:,2]*rho*weights[i]

# Spatial averages
uu = grid.SpatialAverage(uu,0)
vv = grid.SpatialAverage(vv,0)
ww = grid.SpatialAverage(ww,0)
uv = grid.SpatialAverage(uv,0)
uw = grid.SpatialAverage(uw,0)
vw = grid.SpatialAverage(vw,0)
bprod = grid.SpatialAverage(bprod,0)*-9.81

grid.InsertField(U,"U")
grid.InsertField(Rho,"Rho")
grid.InsertField(Ucyl,"Ucyl")

grid.WriteResultGrid("temp1.vts")

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
plane_np.PointData.append(grid.ExtractPlane(bprod,0,0),"bP")
writer = vtk.vtkXMLStructuredGridWriter()
writer.SetInputData(sPlane)
writer.SetFileName("plane.vts")
writer.Write()