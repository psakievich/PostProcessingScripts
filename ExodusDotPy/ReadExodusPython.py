import sys
sys.path.append(r"/projects/seacas/linux/current/lib")
import numpy as np
import exodus

def ReadExodus(fName, tstart, variables,shape=None):
  data = exodus.exodus(fName, array_type='numpy')
  times_whole = data.get_times()
  time_indicies = np.where(times_whole >= tstart)[0]
  coordinates = data.get_coords()
  if shape is None:
    shape = len(coordinates[0])
  shape_x = [len(coordinates)]
  shape_t = [len(time_indicies)]
  for item in shape:
    shape_x.append(item)
    shape_t.append(item)
  x = np.empty(shape_x)
  for i in range(len(coordinates)):
    x[i]=coordinates[i].reshape(shape)
  results = {}
  for name in variables:
    # see about allowing more than scalar by getting size of variable some how
    results[name] = np.zeros(shape_t) 
  for i, time_step in enumerate(time_indicies):
    for name in variables:
        results.get(name)[i] = data.get_node_variable_values(name, time_step+1).reshape(shape)
  return x, results

def CorrectIndex(x,v):
  order = x[0][0].argsort()
  ndim, nlines, npoints = x.shape
  keys = v.keys()
  ntstep = v.get(keys[0]).shape[0]
  for i in range(ndim):
    for j in range(nlines):
      x[i][j] = x[i][j][order]
  for name in keys:
    for j in range(ntstep):
      for k in range(nlines):
         v.get(name)[j,k] = v.get(name)[j,k][order]
  return x,v

