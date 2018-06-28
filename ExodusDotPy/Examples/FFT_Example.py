import FireSymIO 
import numpy as np
from matplotlib import pyplot as plt

FPATH=(r'/gpfs1/jchewso/MethaneOldFlame_Coflow'+ 
       r'/OldFlame_1m_CH4_SMAGcoflow-C01_mixFrac_Test24'+ 
       r'/solution_LES/')
FNAME=r'lines_at_p3.e'
fName=FPATH+FNAME

'''READ FILE'''
x,vx,vy,vz,mfrac=FireSymIO.ImportExodus(fName,timeStart=10,verbose=True)

print (vx.shape)

'''PROJECT RESULTS'''
#1 Normalize Position vector
xMag=np.sqrt(x[0]**2+x[1]**2+1e-12)
xNorm=np.array([x[0]/xMag,x[1]/xMag])
#2 Create Planar vector
vPlanar=np.array([vx,vy])
#3 Dot Product
vLine=vx.copy()
for i in range(vPlanar.shape[1]):
  vLine[i,:]=xNorm[0]*vPlanar[0,i,:]+xNorm[1]*vPlanar[1,i,:] 

'''CALCULATE MEAN'''
#1 Reshape the array
shape=vLine.shape
vLine= vLine.reshape(shape[0]*4,shape[1]/4)
lineShape=vLine.shape
print("The shape of the line dataset is:",lineShape)
xLine=x[0][0:shape[1]/4]
#2 Calc Mean
mVLine=np.mean(vLine,axis=0)
plt.plot(xLine,mVLine)
plt.title("Mean")
plt.xlabel("X")
plt.ylabel("$V_{line}$")

'''CALCULATE FLUC'''
fVLine=vLine-mVLine
plt.figure()
for i in range(20):
   plt.plot(xLine,fVLine[i],'o')
plt.title("First 20 Fluctuations")

'''TAKE FFT'''
#1 Storage for FFT coefficients
fftVLine=np.empty(lineShape,dtype=np.complex)
#2 Take FFT
fftVLine=np.fft.fft(fVLine)
#3 shift zero frequency to center
fftVLine=np.fft.fftshift(fVLine)
#4 scale by fft size
fftVLine/=lineShape[-1]
fftFreq=np.fft.fftfreq(lineShape[-1],1.0/lineShape[-1])
fftFreq=np.fft.fftshift(fftFreq)
#5 Compute Energy and Phase
energy=np.abs(fftVLine)**2
spectra=np.mean(energy,axis=0)
plt.figure()
plt.plot(fftFreq,spectra,'-*')
plt.title("Spectra")
plt.ylabel("$|\hat{u}^2|$")
plt.xlabel("$f$")
phase=np.angle(fftVLine)
mPhase=np.mean(phase,axis=0)
plt.figure()
plt.plot(fftFreq,mPhase,'-*')
plt.title("Phase")
plt.ylabel(r"$\phi$")
plt.xlabel("$f$")
plt.show()


