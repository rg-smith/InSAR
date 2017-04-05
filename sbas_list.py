import numpy as np
import matplotlib.pyplot as plt

sp_baseline=1000
t_baseline=200
dat=np.genfromtxt('baseline_table.dat')
names=np.genfromtxt('data.in',dtype=str,usecols=[0])
names1=np.genfromtxt('data.in');names1=names1.reshape(len(names1),1)
if np.shape(dat)[1]==4:
    dat=np.hstack((names1,dat))
fname='align.in'
fname2='intf.in'
# close all plots
plt.close('all')
# for alos
#str_before='IMG-HH-ALPSRP'
#str_after='0730-H1.0__A'
# for envisat, ers
str_before=''
str_after=''

l_file=0
for kk in range(np.shape(dat)[0]):
    l_file=l_file+kk

datfile=np.zeros((l_file,4))
tdiff=np.zeros((np.shape(dat)[0],1));bdiff=np.zeros((np.shape(dat)[0],1))

for kk in range(np.shape(tdiff)[0]):
    tdiff[kk]=np.mean(np.square(dat[kk,2]-dat[:,2]))
    bdiff[kk]=np.mean(np.square(dat[kk,4]-dat[:,4]))
alldiff=tdiff+bdiff
mastloc=np.where(alldiff==np.min(alldiff))
plt.figure();plt.plot(dat[:,2],dat[:,4],'bo',dat[mastloc[0],2],dat[mastloc[0],4],'ro');plt.title('Temporal and spatial baseline with master')
master=(names[mastloc[0][0]])
    
count=-1
names2=np.empty([l_file],dtype='|S5')
names3=np.empty([l_file],dtype='|S5')
for kk in range(np.shape(dat)[0]):
    ival=dat[kk,0]
    t=dat[kk,2]
    b=dat[kk,4]
    for yy in range(kk+1,np.shape(dat)[0]):
        count=count+1
        t2=dat[yy,2]
        b2=dat[yy,4]
        names2[count]=names[kk]
        datfile[count,0]=ival
        datfile[count,1]=dat[yy,0]
        names3[count]=names[yy]
        datfile[count,2]=t2-t
        datfile[count,3]=b2-b

file_list=np.where(np.logical_and(datfile[:,2]<t_baseline,abs(datfile[:,3])<sp_baseline))
f=open(fname,'w')

for kk in range(np.shape(dat)[0]):
    str2=(names[kk])
    f.write(str_before+master+str_after+':'+str_before+str2+str_after+':'+str_before+master+str_after+'\n')
f.close()

f=open(fname2,'w')

for kk in range(np.shape(file_list)[1]):
    index=file_list[0][kk]
    str1=str(datfile[index,0])
    str1=str1[0:len(str1)-2]
    str1=names2[index]
    str2=str(datfile[index,1])
    str2=str2[0:len(str2)-2]
    str2=names3[index]
    f.write(str_before+str1+str_after+':'+str_before+str2+str_after+'\n')
f.close()

plt.figure();plt.hist(datfile[:,2])
plt.figure();plt.hist(datfile[:,3])
plt.figure();plt.plot(datfile[:,2],datfile[:,3],'o')
print('Will produce '+str(np.shape(file_list)[1])+' interferograms')