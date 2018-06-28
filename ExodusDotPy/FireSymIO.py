import sys
sys.path.append(r"/projects/seacas/linux/current/lib")
import numpy as np
import exodus
#from matplotlib import pyplot as plt
#FPATH=(r'/gpfs1/jchewso/MethaneOldFlame_Coflow'+
#       r'/OldFlame_1m_CH4_SMAGcoflow-C01_mixFrac_Test24'+
#       r'/solution_LES/')
#FNAME=r'lines_at_p3.e'
def ShiftSpace(x,sf=1.1):
    x[0][0:256]-=x[0][0]*sf
    x[1][0:256]-=x[1][0]*sf
    x[2][0:256]-=x[2][0]*sf

    x[0][256:512]-=x[0][256]*sf
    x[1][256:512]-=x[1][256]*sf
    x[2][256:512]-=x[2][256]*sf

    x[0][512:768]-=x[0][512]*sf
    x[1][512:768]-=x[1][512]*sf
    x[2][512:768]-=x[2][512]*sf

    x[0][768:1024]-=x[0][768]*sf
    x[1][768:1024]-=x[1][768]*sf
    x[2][768:1024]-=x[2][768]*sf
    return x

def CalcRadialVel(x,vx,vy):
    #1 Normalize Position vector
    xMag=np.sqrt(x[0]**2+x[1]**2)+1e-12
    xNorm=np.array([x[0]/xMag,x[1]/xMag])

    #2 Dot Product
    vLine=vx.copy()
    for i in range(vx.shape[0]):
      vLine[i]=xNorm[0]*vx[i]+xNorm[1]*vy[i]
    return vLine

def ReshapeVals(x,vals,nLines=4):
    shape=vals[0].shape
    xLine=x[0][0:shape[1]/nLines]
    order=xLine.argsort()
    xLine=xLine[order]
    for i in range(len(vals)):
        vals[i]=vals[i].reshape(shape[0]*nLines,shape[1]/nLines)
        for j in range(vals[i].shape[0]):
            vals[i][j]=vals[i][j][order]
    return xLine,vals


def EnergySpectra(fName,timeStart=10,verbose=False,Favre=True):
    '''READ FILE'''
    x,vx,vy,vz,mfrac,density=ImportExodus(fName,timeStart=timeStart,verbose=verbose)
    '''SHIFT DATA'''
    x=ShiftSpace(x)
    '''PROJECT RESULTS'''
    vLine=CalcRadialVel(x,vx,vy)
    '''Reshape and sort variables'''
    #pack variables of interest into a list
    #for ReshapeVals function
    variables=[vLine,vz,density]
    xLine,variables=ReshapeVals(x,variables)
    #Unpack list
    vLine,vz,density=variables

    '''CALCULATE MEAN'''
    #1 Calc Favre
    mDensity=np.mean(density,axis=0)
    if Favre:
    	mVLine=np.mean(vLine*density,axis=0)/mDensity
        mVz=np.mean(vz*density,axis=0)/mDensity
    else:
        mVLine=np.mean(vLine,axis=0)
        mVz=np.mean(vz,axis=0)

    '''CALCULATE FLUC'''
    fVLine=vLine-mVLine
    fVz=vz-mVz
    '''COMPUTE SPATIAL CORRELATIONS'''
    vlRij=np.zeros([fVLine.shape[1],fVLine.shape[1]])
    vzRij=vlRij.copy()
    for i in range(fVLine.shape[0]):
        a=np.array([fVLine[i]])
        b=np.array([fVz[i]])
        vlRij+=np.matmul(a.T,a)
        vzRij+=np.matmul(b.T,b)
    vlRij/=float(fVLine.shape[0])
    vzRij/=float(fVz.shape[0])

    '''TAKE FFT'''
    #1 Storage for FFT coefficients
    fftVLine=np.empty(xLine.shape,dtype=np.complex)
    fftVz=fftVLine.copy()
    #2 Take FFT
    fftVLine=np.fft.fft(fVLine)
    fftVz=np.fft.fft(fVz)
    #3 shift zero frequency to center
    fftVLine=np.fft.fftshift(fftVLine)
    fftVz=np.fft.fftshift(fftVz)
    #4 scale by fft size
    fftVLine/=xLine.shape[-1]
    fftVz/=xLine.shape[-1]
    fftFreq=np.fft.fftfreq(xLine.shape[-1],1.0/xLine.shape[-1])
    fftFreq=np.fft.fftshift(fftFreq)
    #5 Compute Energy and Phase
    energyR=np.abs(fftVLine)**2
    spectraR=np.mean(energyR,axis=0)
    energyZ=np.abs(fftVz)**2
    spectraZ=np.mean(energyZ,axis=0)
    spectra=[spectraR,spectraZ]
    mean=[mVLine,mVz]
    corr=[vlRij,vzRij]
    return fftFreq, spectra,xLine,mean,corr


def ImportExodus(fName,timeStart=0,verbose=False):
   '''
   Function to import exodus file containing line data
   Inputs:
      fName-path and file name to desired file
      timeStart- start time for pullling data
      verbose - print extra information
   Outputs:
      x - position
      xvel,yvel,zvel
      mfrac
   '''
   data=exodus.exodus(fName,array_type='numpy')
   try:
       """check the exodus file contents """
       if (verbose):
         print "Exodus file has title:", data.title()
         print "Exodus file has", data.num_dimensions(), "dimensions"
         print "Exodus file has", data.num_nodes(), "nodes"
         print "Exodus file has", data.num_elems(), "elements"
         print "Exodus file has", data.num_blks(), "blocks"
         print "Exodus file has", data.num_node_sets(), "node sets"
         print "Exodus file has", data.num_times(), "time steps"

       # get time and block ids
       times_whole = data.get_times()
       blocks = data.get_elem_blk_ids()

       # print block id
       blocks = data.get_elem_blk_ids()
       if (verbose):
         print "Block id"
         for block in blocks:
            print "\tblock id = ", block

       # get coordinates
       coordinates = data.get_coords()
       if(verbose):
         print "Local Node Id 1 has coordinates:", coordinates[0][0], coordinates[1][0], coordinates[2][0]
       nn = (data.num_nodes() - 1)
       if(verbose):
         print "Local Node Id", data.num_nodes(), "has coordinates:", coordinates[0][nn], coordinates[1][nn], coordinates[2][nn]

       # print variable names
       if(verbose):
         print "Nodal Variable Names"
       nodeVarNames = data.get_node_variable_names()

       if(verbose):
          for name in nodeVarNames:
             print "\t" + name

       # create numpy arrays to store data.
       # since we are taking statistics we need only look at the data once the plume is fully developed
       time_start = timeStart
       time_indices = np.where(times_whole > time_start)[0]
       time_size = time_indices.size
       times = times_whole[time_indices]
       mfrac = np.zeros((time_size, coordinates[0].size))
       xvel = np.zeros((time_size, coordinates[0].size))
       yvel = np.zeros((time_size, coordinates[0].size))
       zvel = np.zeros((time_size, coordinates[0].size))
       density=mfrac.copy()

       # get data and store in numpy arrays
       for i, time_step in enumerate(time_indices):
           t = times_whole[time_step]
           #print("Processing data: Time {}, Time Step {}".format(t, time_step+1))
           try:
             mfrac[i] = data.get_node_variable_values("mixture_fraction",time_step+1)
           except:
             pass
           try:
             xvel[i] = data.get_node_variable_values("x_vel",time_step+1)
           except:
             pass
           try:
             yvel[i] = data.get_node_variable_values("y_vel",time_step+1)
           except:
             pass
           try:
             zvel[i] = data.get_node_variable_values("z_vel",time_step+1)
           except:
             pass
           try:
             density[i] = data.get_node_variable_values("density",time_step+1)
           except:
             pass

       # close file
       data.close()

   except:
       #close file
       print "Unexpected error:"
       data.close()

   # save coordinates in variable x
   x = coordinates
   return x,xvel,yvel,zvel,mfrac,density
