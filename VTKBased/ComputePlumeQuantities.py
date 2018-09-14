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

def ComputePlumeQOI(fileList,timeFile,outFile,tAvgStart=5.0):
    """ Compute Plume QOI for time > 5 sec
    """
    # compute average
    tsteps = np.loadtxt(timeFile)
    start = np.argmax(tsteps>tAvgStart)
    stop = len(fileList)
    print start,stop
    deltaT = tsteps[stop-1]-tsteps[start]
    # timestep weighting ignores first step
    weights = tsteps.copy()
    for i in range(start,stop):
        if i>0:
            weights[i]-=tsteps[i-1]
        else:
            weights[i] = 0.0
    weights /= deltaT

    grid = ro.StructuredGridProcessing(fileList[start])
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

    U = grid.GetField("velocity_")
    Rho = grid.GetField("density")
    URho = U * Rho
    U *= weights[start]
    Rho *= weights[start]
    URho *= weights[start]

    for i in range(start+1,stop):
        grid.UpdateFileName(fileList[i])
        tU = grid.GetField("velocity_")
        tRho = grid.GetField("density")
        U += tU*weights[i]
        Rho += tRho *weights[i]
        URho += tU*tRho*weights[i]

    Ucyl=cart_to_cyl(U)
    URhoCyl = cart_to_cyl(URho)
    Ucyl = grid.SpatialAverage(Ucyl,0)
    URhoCyl = grid.SpatialAverage(URhoCyl,0)
    Rho = grid.SpatialAverage(Rho,0)
    U = cyl_to_cart(Ucyl)
    URho = cyl_to_cart(URhoCyl)
    Uf = URho/Rho

    # compute fluc terms
    uu = U[:,0].copy()*0.0
    vv = uu.copy()*0.0
    ww = uu.copy()*0.0
    uv = uu.copy()*0.0
    uw = uu.copy()*0.0
    vw = uu.copy()*0.0
    bprod = uu.copy()*0.0
    temp = uu.copy()*0.0
    diss = temp.copy()

    def kronDelta(a,b):
        if a == b:
            return 1.0
        else:
            return 0.0

    # create and process fluctuations
    for k in range(start,stop):
        grid.UpdateFileName(fileList[k])
        uf=grid.GetField("velocity_")-Uf
        grid.InsertField(uf,'vel_fluc')
        dufdx = grid.Gradient('vel_fluc')
        dudx = grid.Gradient("velocity_")
        tRho = grid.GetField("density")
        mu = grid.GetField("viscosity")
        uu += uf[:,0]**2*tRho*weights[k]
        vv += uf[:,1]**2*tRho*weights[k]
        ww += uf[:,2]**2*tRho*weights[k]
        uv += uf[:,0]*uf[:,1]*tRho*weights[k]
        uw += uf[:,0]*uf[:,2]*tRho*weights[k]
        vw += uf[:,1]*uf[:,2]*tRho*weights[k]
        bprod += uf[:,2]*tRho*weights[k]
        for i in range(3):
            for j in range(3):
                temp += (mu*((dudx[:,i,j]+dudx[:,j,i])
                        -2.0/3.0*kronDelta(i,j)*dudx[:,i,j])
                        *0.5*(dufdx[:,i,j]+dufdx[:,j,i])
                        )
        diss += temp*weights[k]

    # Spatial averages
    uu = grid.SpatialAverage(uu,0)
    vv = grid.SpatialAverage(vv,0)
    ww = grid.SpatialAverage(ww,0)
    uv = grid.SpatialAverage(uv,0)
    uw = grid.SpatialAverage(uw,0)
    vw = grid.SpatialAverage(vw,0)
    bprod = grid.SpatialAverage(bprod,0)*-9.81
    diss = grid.SpatialAverage(diss,0)#/Rho

    grid.InsertField(Uf,"Uf")
    #grid.WriteResultGrid("temp1.vts")

    #cartesian coords
    dUfdx = grid.Gradient("Uf")

    production = dUfdx[:,0,0]*uu\
                   +(dUfdx[:,0,1] + dUfdx[:,1,0])*uv\
                   +(dUfdx[:,0,2] + dUfdx[:,2,0])*uw \
                   +dUfdx[:,1,1]*vv \
                   +(dUfdx[:,1,2] + dUfdx[:,2,1])*vw\
                   +dUfdx[:,2,2]*ww

    NX = grid.data.GetDimensions()
    # More practially, create a plane and output the averaged QOI
    sPlane = cg.CreateCylindricalGrid(0.5,1.0,(NX[1],NX[2],1), indexOrder=['r','z','t'])
    plane_np = dsa.WrapDataObject(sPlane)
    plane_np.PointData.append(grid.ExtractPlane(Ucyl,0,0),"velMean")
    plane_np.PointData.append(grid.ExtractPlane(grid.SpatialAverage(production,0),0,0),"tkeP")
    plane_np.PointData.append(grid.ExtractPlane(bprod,0,0),"bP")
    plane_np.PointData.append(grid.ExtractPlane(diss,0,0),"dissipation")
    writer = vtk.vtkXMLStructuredGridWriter()
    writer.SetInputData(sPlane)
    writer.SetFileName(outFile)
    writer.Write()