# -*- coding: utf-8 -*-
# make a list of .grd files with year, day of each SAR scene in the filename separated by a '_'
fname='list.txt'

import numpy as np

fnames=np.genfromtxt(fname,dtype='str')
datenum1=np.zeros(np.shape(fnames));datenum2=np.zeros(np.shape(fnames));

f=open('filelist_dec.txt','w')
for kk in range(np.shape(fnames)[0]):
    nm=fnames[kk].split('_')
    datenum1[kk]=int(nm[0][0:4])+float(nm[0][4:7])/365;
    datenum2[kk]=int(nm[1][0:4])+float(nm[1][4:7])/365;
    f.write(str(datenum1[kk])+':'+str(datenum2[kk])+'\n')
f.close()
full=np.unique(np.hstack((datenum1,datenum2)))
days=np.round(np.diff(full)*365)
daymat=np.tile(days,[np.shape(fnames)[0],1])
tm=np.zeros(np.shape(daymat))

f=open('tm.out','w')
for kk in range(np.shape(fnames)[0]):
    ind1=np.where(datenum1[kk]==full)[0][0]
    ind2=np.where(datenum2[kk]==full)[0][0]
    tm[kk,ind1:ind2]=daymat[kk,ind1:ind2]
    for xx in range(np.shape(tm)[1]):
        f.write(str(tm[kk,xx])+' ');
    f.write('\n')
f.close()

f=open('dates.txt','w')
for kk in range(np.shape(full)[0]):
    f.write(str(full[kk])+'\n')
f.close()