'''
Generalized fucntions for extracting data in
using paraview

author  @psakiev
data started 5/11/18

'''
from paraview.simple import ExodusIIReader, XMLMultiBlockDataWriter, MergeBlocks, \
  XMLPUnstructuredGridWriter


def ReadExodus(fileBase, nProcs=None):
  import numpy as np
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

def WriteGeneral(writerType, source, fileOut, returnWriter=False):
  '''
  Write a dataset from a user supplied writer object

  params:
    writerType - paraview simple writer object
    source - object to write from
    fileOut - filename for the output
  Keywords:
    returnWriter - if true return the writer, if false
                   just dump the file
                   Warning - if false it will generate
                   a new writer at each instance
                   not really recommended for use repeatedly
  '''
  writer = writerType(Input = source)
  writer.FileName = fileOut
  if returnWriter:
    return writer
  writer.UpdatePipeline()

def WriteMultiBlock(source, fileOut, returnWriter=False):
  '''
  Write a dataset as a multiblock

  params:
    source - object to write from
    fileOut - filename for the output
  Keywords:
    returnWriter - if true return the writer, if false
                   just dump the file
                   Warning - if false it will generate
                   a new writer at each instance
                   not really recommended for use repeatedly
  '''
  writer = XMLMultiBlockDataWriter(Input = source)
  writer.FileName = fileOut
  if returnWriter:
    return writer
  writer.UpdatePipeline()

def WriteUnstructured(source, fileOut, returnWriter=False):
  '''
  Write data as an unstructured grid

  params:
    source - object to write from
    fileOut - filename for the output
  keywords:
    returnWriter - if true return the writer, if false
                   just dump the file
                   Warning - if false it will generate
                   a new writer at each instance
                   not really recommended for use repeatedly
  '''
  mergeBlocks = MergeBlocks(Input = source)
  writer = XMLPUnstructuredGridWriter(Input = source)
  writer.FileName = fileOut
  if returnWriter:
    return writer
  writer.UpdatePipeline()
