#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 12:15:07 2018

Example of how to resample data from one mesh to another
Geometry should be conformal, but node/element count can vary
Run in parallel with pvbatch

syntax 

script fileData fdNP fileMesh fmNP fileOut

fileData - file containing the data
fdNP     - number of processores the fileData is decomposed on
fileMesh - file containint the new mesh to interpolate to
fmNP     - number of processors the fileMesh is decomposed on
 fileOut - resultant file desired
      
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!paths for files should be absolute!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

@author: psakiev
"""

from paraview.simple import *
import sys
import math

def ReadExodus(fileBase, nProcs=None):
  '''
  Read in an exodus file or decomposed file

  Params:
    fileBase  - The base file name ("fluid.e") or the fileName
  Keywords:
    nProcs  -  If None (default) then fileBase is fileName otherwise
               it's the niumber of processors that are used to decompose
               the file
  '''
  if nProcs is None:
    fileNames = fileBase
  else:
    intPad = int(math.log10(nProcs))+1
    pattern = "%s.{nproc}.%0{intpad}i".format(nproc=nProcs,intpad=intPad)
    fileNames = [pattern % (fileBase,i) for i in range(nProcs)]
  reader =  ExodusIIReader(FileName = fileNames)
  reader.SelectAllVariables()
  reader.UpdatePipeline()
  return reader

fileData, fdNP, fileMesh, fmNP, fileOut = sys.argv[1:6]
fdNP= int(fdNP)
fmNP = int(fmNP)

print "fileData = {fd}\n fileMesh = {fm}\n fileOut = {fo}\n".format(
        fd=fileData,fm=fileMesh,fo=fileOut
        )
if fdNP <= 1:
    fdNP = None
if fmNP <= 1:
    fmNP = None
    
print fdNP, fmNP

data = ReadExodus(fileData,nProcs=fdNP)
mesh = ReadExodus(fileMesh, nProcs=fmNP)

resample = ResampleWithDataset(Input=data,Source=mesh)

writer = ExodusIIWriter(Input = resample)
writer.FileName = fileOut
writer.UpdatePipeline()
