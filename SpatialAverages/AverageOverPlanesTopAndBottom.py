'''
Average data over plane at specified locations
derivative of AverageOverPlanes.py
Will out put two files.  One each for top and bottom of 
a channel with profiles vs wall distance
Should be run with pvpython or pvbatch

@author Phil Sakievich
@email  psakiev@sandia.gov
@date   5/7/2018
'''
import paraview.simple as pvs

class AverageOverPlanes:
  def __init__(self, inputFileName):
    self.fileName = inputFileName

  def ReadInput(self,readerFunction=pvs.ExodusIIReader ):
    '''
    Get reader and abstract so differen file types can be used
    by changing the keyword readerFunction
    '''
    self.reader = readerFunction(FileName=self.fileName)
    try:
      self.reader.SelectAllVariables()
      self.reader.UpdatePipeline()
      tsteps = self.reader.TimestepValues
      self.reader.UpdatePipeline(max(tsteps))
    except:
      # pass for now.  If this is ever used better excpetion
      # handeling can be implemented
      pass

  def CreatePipeline(self):
    '''
    Create slice and integration filters
    different slices can be saved by adjusting the
    slice filter's position
    '''
    self.slice = pvs.Slice(Input = self.reader)
    self.integrator = pvs.IntegrateVariables(Input = self.slice)
    self.integrator.DivideCellDataByVolume = True

  def SetSliceLocation(self, origin, normal):
    '''
    Move slice location and upddate pipline
    '''
    self.slice.SliceType.Origin = origin
    self.slice.SliceType.Normal = normal
    self.slice.UpdatePipeline()

  def FetchData(self):
    '''
    Return averaged data as a dictionary with variable names as keys
    '''
    data = pvs.paraview.servermanager.Fetch(self.integrator)
    try:
      area = data.GetCellData().GetArray("Area").GetValue(0)
      num_arrays = data.GetPointData().GetNumberOfArrays()
      results = {}
      for i in range(num_arrays):
        array = data.GetPointData().GetArray(i)
        dims = array.GetDataSize()
        for j in range(dims):
          name = array.GetName()
          if dims > 1:
            name += str(j+1)
          results[name] = array.GetValue(j)/area
      return results
    except Exception as e:
      print "Profile point is probably not within domain.  Try adjusting precision."
      print "Actual excpetion is: ", e
      exit()

if __name__ == '__main__':
  import numpy as np
  from numpy.polynomial.chebyshev import chebgauss

  print "Starting program"

  fileIn = "/gpfs1/spdomin/hexTetPaper/channelFlow/postProcess/results/wale_wedge6.e"
  fileBottom = "profile_bottom.dat"
  fileTop = "profile_top.dat"
  nPoints = 100
  rho = 1.0
  mu = 2.531646e-3
  #  create non uniform spacing with Gauss-Chebyshev polynomials
  #  double the spaceing because we will only use half the points for the biasing
  y, w = chebgauss(2*nPoints)
  # transform the data so y \in (0:2)
  y *= -1.0
  y += 1.0
  # only use the half quadrature for biasing effect
  vertical_locations = np.array(y.copy(),ndmin=2).T

  # generate y+ values
  yp = vertical_locations/mu*rho
  origins = [(0,val,0) for val in y]
  normal = (0,1,0)

  PostProcessor = AverageOverPlanes(fileIn)
  PostProcessor.ReadInput()
  PostProcessor.CreatePipeline()
  PostProcessor.SetSliceLocation(origins[0],normal)

  data = PostProcessor.FetchData()
  header_values = sorted(data.keys())
  my_header_str ="position, y+"

  for name in header_values:
    my_header_str += ", " + name

  # Bottom profile saves vs wall normal distance
  results = np.array([data.get(key) for key in header_values],ndmin=2)
  print "Profile {num} processed.".format(num=0)

  for i in range(1,nPoints):
    PostProcessor.SetSliceLocation(origins[i],normal)
    data = PostProcessor.FetchData()
    temp = np.array([data.get(key) for key in header_values] ,ndmin=2)
    results = np.append(results,temp,axis=0)
    print "Profile {num} processed.".format(num=i)

  results = np.concatenate((vertical_locations[0:nPoints],yp[0:nPoints],results),axis=1)
  np.savetxt(fileBottom,results,delimiter=",",header=my_header_str)
  print "Data saved to {filename}.".format(filename=fileBottom)

  # Top profile saved vs wall normal distance
  PostProcessor.SetSliceLocation(origins[nPoints],normal)
  data = PostProcessor.FetchData()
  results = np.array([data.get(key) for key in header_values],ndmin=2)
  print "Profile {num} processed.".format(num=nPoints)
  for i in range(nPoints+1,2*nPoints):
    PostProcessor.SetSliceLocation(origins[i],normal)
    data = PostProcessor.FetchData()
    temp = np.array([data.get(key) for key in header_values] ,ndmin=2)
    results = np.append(results,temp,axis=0)
    print "Profile {num} processed.".format(num=i)

  results = np.concatenate((vertical_locations[nPoints:2*nPoints],yp[0:nPoints][::-1],results),axis=1)
  np.savetxt(fileTop,results,delimiter=",",header=my_header_str)
  print "Data saved to {filename}.".format(filename=fileTop)
