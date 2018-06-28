
# coding: utf-8

# In[49]:

get_ipython().magic(u'matplotlib notebook')
import FireSymIO
import numpy as np
#from matplotlib import pyplot as plt


# In[2]:

def GenerateData(files):
    spectra=[]
    freq=[]
    x=[]
    m=[]
    c=[]
    for f in files:
        fT,sT,xT,mT,cT=FireSymIO.EnergySpectra(f,Favre=True);
        spectra.append(sT)
        freq.append(fT)
        x.append(xT)
        m.append(mT)
        c.append(cT)
    return freq,spectra,x,m,c


# In[3]:

def GenerateFileList(fPATH,PointIndex):
    fTemplate=r'lines_at_p{}.e'
    return [fPATH+fTemplate.format(i) for i in PointIndex]
    


# In[41]:

def NormedCorrelation(x,Rij):
    #norm=np.mean(np.trace(Rij))
    meanRij=np.zeros(Rij.shape[0])
    tau=meanRij.copy()
    for i in range(Rij.shape[0]):
        tau[i]=np.abs(x[0]-x[i])
        for j in range(i,Rij.shape[0]):
            #normalize by number of instances in the seperation distance
            meanRij[j-i]+=Rij[i][j]/float(Rij.shape[0]-j) 
    normRij=meanRij/meanRij[0]
    return tau,normRij


# In[5]:

get_ipython().run_cell_magic(u'capture', u'', u"'''Numerical Data'''\nfPATH=r'/gpfs1/jchewso/MethaneOldFlame_Coflow/OldFlame_1m_CH4_SMAGcoflow-C01_mixFrac_Test24/solution_LES/'\nfiles=GenerateFileList(fPATH,[3,5,9])\nf1,s1,x1,m1,c1=GenerateData(files)\nfPATH=r'/gpfs1/jchewso/MethaneOldFlame_Coflow_Refine1/OldFlame_1m_CH4_SMAGcoflow-C01_mixFrac_Test24/solution_LES/'\nfiles=GenerateFileList(fPATH,[3,5,9])\nf2,s2,x2,m2,c2=GenerateData(files)\nfPATH=r'/gpfs1/jchewso/MethaneOldFlame_Coflow_Refine1/OldFlame_1m_CH4_DKsgs_mixFrac_Test24/solution_LES/'\nfiles=GenerateFileList(fPATH,[3,5,9])\nf3,s3,x3,m3,c3=GenerateData(files)")


# In[50]:

print len(c1),len(c1[0]),len(c1[0][0]),np.max(c1[0][0]),np.min(c1[0][0])
plt.contour(c1[2][1])
plt.colorbar()
#plt.show()


# In[7]:

'''Experimental Data'''
expPATH=r'/gpfs1/jchewso/MaCFP/macfp-db/Gaseous_Pool_Fires/Sandia_Flames/Experimental_Data/'
expFTEMP=r'Sandia_CH4_1m_Test24_p{}.csv'
expP1=np.loadtxt(expPATH+expFTEMP.format(3),skiprows=1,delimiter=',')
expP2=np.loadtxt(expPATH+expFTEMP.format(5),skiprows=1,delimiter=',')
expP3=np.loadtxt(expPATH+expFTEMP.format(9),skiprows=1,delimiter=',')


# In[92]:

fig,ax=plt.subplots(3,figsize=(8,15))
velDir='RADIAL '
ind=0
#plt.figure()
ax[0].loglog(f1[0],s1[0][ind],label='p3')
ax[0].loglog(f1[1],s1[1][ind],label='p5')
ax[0].loglog(f1[2],s1[2][ind],label='p9')
ax[0].set_title(velDir+'SMAG')
ax[0].legend()
#plt.figure()

ax[1].loglog(f2[0],s2[0][ind],label='p3')
ax[1].loglog(f2[1],s2[1][ind],label='p5')
ax[1].loglog(f2[2],s2[2][ind],label='p9')
ax[1].set_title(velDir+'SMAG REFINE')
ax[1].legend()
#plt.figure()
ax[2].loglog(f3[0],s3[0][ind],label='p3')
ax[2].loglog(f3[1],s3[1][ind],label='p5')
ax[2].loglog(f3[2],s3[2][ind],label='p9')
ax[2].set_title(velDir+'KSGS REFINE')
ax[2].legend()
#plt.show()


# In[64]:

fig,ax=plt.subplots(2,2,figsize=(10,10))
velDir='RADIAL '
ind=0

ax[0,0].plot(x1[0],m1[0][ind],label='p3')
ax[0,0].plot(x1[1],m1[1][ind],label='p5')
ax[0,0].plot(x1[2],m1[2][ind],label='p9')
ax[0,0].set_title(velDir+'Mean SMAG')
ax[0,0].legend()

ax[0,1].plot(x2[0],m2[0][ind],label='p3')
ax[0,1].plot(x2[1],m2[1][ind],label='p5')
ax[0,1].plot(x2[2],m2[2][ind],label='p9')
ax[0,1].set_title(velDir+'Mean SMAG REFINE')
ax[0,1].legend()

ax[1,0].plot(x3[0],m3[0][ind],label='p3')
ax[1,0].plot(x3[1],m3[1][ind],label='p5')
ax[1,0].plot(x3[2],m3[2][ind],label='p9')
ax[1,0].set_title(velDir+'Mean KSGS REFINE')
ax[1,0].legend()

ax[1,1].plot(expP1.T[0],expP1.T[1],label='p3')
ax[1,1].plot(expP2.T[0],expP2.T[1],label='p5')
ax[1,1].plot(expP3.T[0],expP3.T[1],label='p9')
ax[1,1].set_title(velDir+'Mean EXP')
ax[1,1].legend()


# In[89]:

#compare
fig,ax=plt.subplots(3,figsize=(8,15))
velDir='RADIAL '
ind=0
titles=[velDir+'p3',velDir+'p5',velDir+'p9']
for i in range(3):
    ax[i].loglog(f1[i],s1[i][ind],label='SMAG')
    ax[i].loglog(f2[i],s2[i][ind],label='SMAG R')
    ax[i].loglog(f3[i],s3[i][ind],label='KSGS R')
    ax[i].set_title(titles[i])
    ax[i].legend()


# In[91]:

#compare
fig,ax=plt.subplots(3,figsize=(8,15))
velDir='RADIAL '
ind=0
titles=[velDir+'Mean p3',velDir+'Mean p5',velDir+'Mean p9']
exp=[expP1,expP2,expP3]
for i in range(3):
    ax[i].plot((x1[i]-x1[0][0])-0.5,m1[i][ind],label='SMAG')
    ax[i].plot((x2[i]-x2[0][0])-0.5,m2[i][ind],label='SMAG R')
    ax[i].plot((x3[i]-x3[0][0])-0.5,m3[i][ind],label='KSGS R')
    ax[i].plot(exp[i].T[0],exp[i].T[1],'-o',label='EXP')
    ax[i].set_title(titles[i])
    ax[i].legend()


# In[90]:

fig,ax=plt.subplots(3,figsize=(8,15))
velDir='AXIAL '
ind=1

ax[0].loglog(f1[0],s1[0][ind],label='p3')
ax[0].loglog(f1[1],s1[1][ind],label='p5')
ax[0].loglog(f1[2],s1[2][ind],label='p9')
ax[0].set_title(velDir+'SMAG')
ax[0].legend()

ax[1].loglog(f2[0],s2[0][ind],label='p3')
ax[1].loglog(f2[1],s2[1][ind],label='p5')
ax[1].loglog(f2[2],s2[2][ind],label='p9')
ax[1].set_title(velDir+'SMAG REFINE')
ax[1].legend()

ax[2].loglog(f3[0],s3[0][ind],label='p3')
ax[2].loglog(f3[1],s3[1][ind],label='p5')
ax[2].loglog(f3[2],s3[2][ind],label='p9')
ax[2].set_title(velDir+'KSGS REFINE')
ax[2].legend()


# In[83]:

fig,ax=plt.subplots(2,2,figsize=(10,10))
velDir='AXIAL '
ind=1

ax[0,0].plot(x1[0],m1[0][ind],label='p3')
ax[0,0].plot(x1[1],m1[1][ind],label='p5')
ax[0,0].plot(x1[2],m1[2][ind],label='p9')
ax[0,0].set_title(velDir+'Mean SMAG')
ax[0,0].legend()

ax[0,1].plot(x2[0],m2[0][ind],label='p3')
ax[0,1].plot(x2[1],m2[1][ind],label='p5')
ax[0,1].plot(x2[2],m2[2][ind],label='p9')
ax[0,1].set_title(velDir+'Mean SMAG REFINE')
ax[0,1].legend()

ax[1,0].plot(x3[0],m3[0][ind],label='p3')
ax[1,0].plot(x3[1],m3[1][ind],label='p5')
ax[1,0].plot(x3[2],m3[2][ind],label='p9')
ax[1,0].set_title(velDir+'Mean KSGS REFINE')
ax[1,0].legend()

ax[1,1].plot(expP1.T[0],expP1.T[2],label='p3')
ax[1,1].plot(expP2.T[0],expP2.T[2],label='p5')
ax[1,1].plot(expP3.T[0],expP3.T[2],label='p9')
ax[1,1].set_title(velDir+'Mean EXP')
ax[1,1].legend()


# In[86]:

#compare
fig,ax=plt.subplots(3,figsize=(8,15))
velDir='AXIAL '
ind=1
titles=[velDir+'p3',velDir+'p5',velDir+'p9']
for i in range(3):
    ax[i].loglog(f1[i],s1[i][ind],label='SMAG')
    ax[i].loglog(f2[i],s2[i][ind],label='SMAG R')
    ax[i].loglog(f3[i],s3[i][ind],label='KSGS R')
    ax[i].set_title(titles[i])
    ax[i].legend()

plt.show()


# In[84]:

#compare
fig,ax=plt.subplots(3,figsize=(8,15))
velDir='AXIAL '
ind=1
titles=[velDir+'Mean p3',velDir+'Mean p5',velDir+'Mean p9']
exp=[expP1,expP2,expP3]
for i in range(3):
    ax[i].plot((x1[i]-x1[0][0])-0.5,m1[i][ind],label='SMAG')
    ax[i].plot((x2[i]-x2[0][0])-0.5,m2[i][ind],label='SMAG R')
    ax[i].plot((x3[i]-x3[0][0])-0.5,m3[i][ind],label='KSGS R')
    ax[i].plot(exp[i].T[0],exp[i].T[2],'-o',label='EXP')
    ax[i].set_title(titles[i])
    ax[i].legend()


# In[85]:

fig,ax=plt.subplots(3,figsize=(8,15))
labList=['p3','p5','p9']
velDir="RADIAL "
ind=0
corrVrC1=[]
corrVrC2=[]
corrVrC3=[]
TauVrC1=[]
TauVrC2=[]
TauVrC3=[]

i=0
for C in c1:
    tau,rii=NormedCorrelation(x1[0],C[ind])
    corrVrC1.append(rii)
    TauVrC1.append(np.trapz(rii,x=x1[0]))#(np.mean(rii)/np.abs(x1[0][0]-x1[0][1]))
    ax[0].plot(tau,rii,label=labList[i])
    i+=1
ax[0].legend()
ax[0].set_title(velDir+"SMAG")

i=0
for C in c2:
    tau,rii=NormedCorrelation(x1[0],C[ind])
    corrVrC2.append(rii)
    TauVrC2.append(np.trapz(rii,x=x1[0]))#(np.mean(rii)/np.abs(x1[0][0]-x1[0][1]))
    ax[1].plot(tau,rii,label=labList[i])
    i+=1
ax[1].legend()
ax[1].set_title(velDir+"SMAG R")

i=0
for C in c3:
    tau,rii=NormedCorrelation(x1[0],C[ind])
    corrVrC3.append(rii)
    TauVrC3.append(np.trapz(rii,x=x1[0]))#(np.mean(rii)/np.abs(x1[0][0]-x1[0][1]))
    ax[2].plot(tau,rii,label=labList[i])
    i+=1
ax[2].legend()
ax[2].set_title(velDir+"DKSGS R")


# In[82]:

fig,ax=plt.subplots(3,figsize=(8,15))
labList=['p3','p5','p9']
velDir="AXIAL "
ind=1
corrVzC1=[]
corrVzC2=[]
corrVzC3=[]
TauVzC1=[]
TauVzC2=[]
TauVzC3=[]

i=0
for C in c1:
    tau,rii=NormedCorrelation(x1[0],C[ind])
    corrVzC1.append(rii)
    TauVzC1.append(np.trapz(rii,x=x1[0]))#(np.mean(rii)/np.abs(x1[0][0]-x1[0][1]))
    ax[0].plot(tau,rii,label=labList[i])
    i+=1
ax[0].legend()
ax[0].set_title(velDir+"SMAG")

i=0
for C in c2:
    tau,rii=NormedCorrelation(x1[0],C[ind])
    corrVzC2.append(rii)
    TauVzC2.append(np.trapz(rii,x=x1[0]))#(np.mean(rii)/np.abs(x1[0][0]-x1[0][1]))
    ax[1].plot(tau,rii,label=labList[i])
    i+=1
ax[1].legend()
ax[1].set_title(velDir+"SMAG R")

i=0
for C in c3:
    tau,rii=NormedCorrelation(x1[0],C[ind])
    corrVzC3.append(rii)
    TauVzC3.append(np.trapz(rii,x=x1[0]))#(np.mean(rii)/np.abs(x1[0][0]-x1[0][1]))
    ax[2].plot(tau,rii,label=labList[i])
    i+=1
ax[2].legend()
ax[2].set_title(velDir+"DKSGS R")


# In[46]:

#print x1[0][1]-x1[0][0],1.0/(256-1),np.mean(corrVrC1[0]),np.mean(corrVrC1[0])*255,np.trapz(corrVrC1[0],x=x1[0])
print "RADIAL VELOCITY INTEGRAL LENGTH SCALE (CM)"
print "  ","    SMAG    ","   SMAG_R   ","    DKSGS_R     " 
for i in range(3):
    print "{}".format(labList[i]),TauVrC1[i]*100,TauVrC2[i]*100,TauVrC3[i]*100
print " "
print "AXIAL VELOCITY INTEGRAL LENGTH SCALE (CM)"
print "  ","    SMAG    ","   SMAG_R   ","    DKSGS_R     " 
for i in range(3):
    print "{}".format(labList[i]),TauVzC1[i]*100,TauVzC2[i]*100,TauVzC3[i]*100


# In[ ]:



