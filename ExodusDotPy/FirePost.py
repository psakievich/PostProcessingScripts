import numpy as np

def AddLineVelocity(x, v, nameNew='line_vel',nameHoriz1='x_vel',nameHoriz2='y_vel'):
    x_mag = np.sqrt(x[0]**2 + x[1]**2)
    x_norm = np.abs(x[0:2]/x_mag)
    v[nameNew] = v.get(nameHoriz1)[:] * x_norm[0] + v.get(nameHoriz2)[:] * x_norm[1]

def GetExperimentalData(point, fStart=615, fEnd=1470, FPATH="experimental_data/",\
                        fNameFormat='rg{:04d}zeros.dat', NX=129, NY=105):
    '''
    Get experimental profiles at a given point over a series of files.
    The data is stored in a *csv file. The user specifies a veritcal
    location where they would like the to see the profile, and a search is
    done to find the index that is closest to the desired point.

    Inputs:

    point - the veritcal location for the desired profile.
    fStart - index for the first file in the time series
    fEnd -  index for the last file in the time series
    FPATH - location of the files.  This should have a format specification for the time index
    NX, NY - spatial dimensions of the underlying grid in the file

    Returns:

    x - spatial locations
    v - dictionary with entries
         'line_velocity' corresponding to horizontal velocity
         'z_velocity' correspondint to vertical velocity
         'label' characteristic information about the data set
    '''
    temp=np.zeros([fEnd-fStart,1,NX])
    v={}
    v['line_vel']=temp.copy()
    v['z_vel']=temp.copy()
    x=np.zeros([3,1,NX]) #match dimensions of other dataset
    coord_not_alloc = True
    for i in xrange(fEnd-fStart):
        data=np.loadtxt(FPATH+fNameFormat.format(i+fStart),delimiter=',',\
                        skiprows=1,usecols=(0,1,2,3))
        if coord_not_alloc:
            y=data.T[1].reshape(NY,NX).T[0]
            p = np.searchsorted(y,point)
            x[0,0]=data.T[0].reshape(NY,NX)[p]
            x[2,0]=data.T[1].reshape(NY,NX)[p]
            coord_not_alloc = False
        v.get('line_vel')[i,0]=data.T[2].reshape(NY,NX)[p]
        v.get('z_vel')[i,0]=data.T[3].reshape(NY,NX)[p]
    v['label']="EXP y={}".format(x[2,0,p])
    return x, v

def GetExperimentalDataPoints(points, fStart, fEnd, FPATH, \
                              fNameFormat='rg{:04d}zeros.dat',NX=129, NY=105):
    '''
    Same as GetExperimentalPoint except multiple points should be specified
    in a format that can be indexed i.e [] is a valid operator
    Much faster for pulling multiple points

    Returns:

    x_t - list containing spatial locations at each point
    v_t - list containing dictionaries for velocity information at each point
    '''
    x_total = []
    v_total = []
    coord_not_alloc = []
    p=[]
    temp=np.zeros([fEnd-fStart,1,NX])
    num_points = len(points)
    for i in range(num_points):
        v={}
        v['line_vel']=temp.copy()
        v['z_vel']=temp.copy()
        x=np.zeros([3,1,NX]) #match dimensions of other dataset
        x_total.append(x)
        v_total.append(v)
        coord_not_alloc.append( True)
    for i in xrange(fEnd-fStart):
        data=np.loadtxt(FPATH+fNameFormat.format(i+fStart),delimiter=',', \
                        skiprows=1,usecols=(0,1,2,3))
        for j in range(num_points):
            if coord_not_alloc[j]:
                y=data.T[1].reshape(NY,NX).T[0]
                p.append(np.searchsorted(y,points[j]))
                #print FPATH
                #print "P={}, y={}".format(points[j],p[j])
                x_total[j][0,0]=data.T[0].reshape(NY,NX)[p[j]]
                x_total[j][2,0]=data.T[1].reshape(NY,NX)[p[j]]
                v_total[j]['label']="PIV y={}".format(y[p[j]])
                coord_not_alloc[j] = False
            v_total[j].get('line_vel')[i,0]=data.T[2].reshape(NY,NX)[p[j]]
            v_total[j].get('z_vel')[i,0]=data.T[3].reshape(NY,NX)[p[j]]

    return x_total, v_total

def GetTKE(v, symmetry = True):
    '''
    Compute mean velocity profiles, fluctuation fields and turbulent kinetic energy

    Input:

    v - velocity dictionary

    Output: No return value

    v (modified with additional terms)
    '''
    #Reynolds Average
    v['z_mean'] = np.mean(np.mean(v.get('z_vel'),axis=0),axis=0)
    v['line_mean'] = np.mean(np.mean(v.get('line_vel'),axis=0),axis=0)
    if symmetry:
        v.update({'line_mean':0.5*(v.get('line_mean')-v.get('line_mean')[::-1])})
        v.update({'z_mean':0.5*(v.get('z_mean')+v.get('z_mean')[::-1])})
    v['z_fluc'] = v.get('z_vel') - v.get('z_mean')
    v['line_fluc'] = v.get('line_vel') - v.get('line_mean')
    v['line_f^2'] = np.mean(np.mean(v.get('line_fluc')**2,axis=0),axis=0)
    v['z_f^2'] = np.mean(np.mean(v.get('z_fluc')**2,axis=0),axis=0)
    v['tke'] = 0.5 * np.mean(np.mean(v.get('z_fluc')**2 + 2.0 * v.get('line_fluc')**2,axis=0),axis=0)
    v['inplane tke'] = 0.75 * np.mean(np.mean(v.get('z_fluc')**2 + v.get('line_fluc')**2,axis=0),axis=0)
    if symmetry:
        v.update({'line_f^2':0.5*(v.get('line_f^2')+v.get('line_f^2')[::-1])})
        v.update({'z_f^2':0.5*(v.get('z_f^2')+v.get('z_f^2')[::-1])})
        v.update({'tke':0.5*(v.get('tke')+v.get('tke')[::-1])})
        v.update({'inplane tke':0.5*(v.get('inplane tke')+v.get('inplane tke')[::-1])})