#### import the simple module from the paraview
from paraview.simple import *
import os
import numpy as np
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

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
    intPad = int(np.log10(nProcs))+1
    pattern = "%s.{nproc}.%0{intpad}i".format(nproc=nProcs,intpad=intPad)
    fileNames = [pattern % (fileBase,i) for i in range(nProcs)]
  reader =  ExodusIIReader(FileName = fileNames)
  reader.SelectAllVariables()
  reader.UpdatePipeline()
  return reader

# Need to write file names and number of procs in file data.txt as:
# result exodus file
# number of procs for result
# gold exodus file
# number of procs for gold file
#
# Right now the convention is to place this file in the same directory as
# the actual files and call the script from that directory
#
pwd = os.environ["PWD"]
inputs = open(pwd+"/data.txt",'r')
lines = inputs.readlines()
inputs.close()

resultFile=lines[0].strip()
goldFile=lines[2].strip()
resultProc=int(lines[1])
goldProc=int(lines[3])

if resultProc <=1:
  resultProc = None

if goldProc <=1:
  goldProc = None

resultReader = ReadExodus(resultFile, resultProc)
goldReader = ReadExodus(goldFile, goldProc)

renderResult = GetActiveViewOrCreate('RenderView')
Show(resultReader,renderResult)

layout = GetLayout()
pvMajor = paraview.servermanager.vtkSMProxyManager.GetVersionMajor()
pvMinor = paraview.servermanager.vtkSMProxyManager.GetVersionMinor()
if pvMajor<=5 and pvMinor <= 6:
  layout.SplitVertical(2,0.5)
else
  view = GetActiveView()
  layout.SplitViewVertical(view)

renderGold = CreateView('RenderView')
layout.AssignView(2,renderGold)
Show(goldReader,renderGold)
