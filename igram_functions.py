#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from osgeo import gdal
import numpy as np
from scipy.interpolate import NearestNDInterpolator
from scipy.interpolate import interp2d
#import matplotlib.pyplot as plt

def loadraster(rastername):
    ds=gdal.Open(rastername)
    band=ds.GetRasterBand(1)
    data=band.ReadAsArray()
    gtr=ds.GetGeoTransform()
    return data, gtr

def load_igrams(flist):
    files=np.genfromtxt(flist,dtype='str')
    dat1,gtr=loadraster(files[0])
    y,x=np.shape(dat1)
    dat=np.zeros((y,x,len(files)))
    yy=np.linspace(gtr[3],gtr[3]+gtr[5]*y,y)
    xx=np.linspace(gtr[0],gtr[0]+gtr[1]*x,x)
    xx,yy=np.meshgrid(xx,yy)
    for kk in range(len(files)):
        dat[:,:,kk],_=loadraster(files[kk])
    return dat,xx,yy

def rebin(a,shape):
    sh=shape[0],a.shape[0]//shape[0],shape[1],a.shape[1]//shape[1]
    return a.reshape(sh).mean(-1).mean(1)

def saveraster(data,drivername,fname,gtr,proj,datatype):
    driver = gdal.GetDriverByName(drivername)
    size=np.shape(data)
    outRaster = driver.Create(fname, size[1], size[0], 1, datatype)
    outRaster.SetGeoTransform(gtr)
    outRaster.SetProjection(proj)
    outBand = outRaster.GetRasterBand(1) 
    outBand.WriteArray(data,0,0)


def interp(dat,filt,method):
    yl,xl=np.shape(dat)
    x = np.linspace(0,xl,xl);y = np.linspace(0,yl,yl)
    xx, yy = np.meshgrid(x, y);
    pts=np.hstack((np.reshape(xx[filt],(np.sum(filt),1)),np.reshape(yy[filt],(np.sum(filt),1))))
    z=np.reshape(dat[filt],(np.sum(filt),1))
    if method=='nearest':
        fn=NearestNDInterpolator(pts,z)
        interpd=fn(xx,yy)[:,:,0]
    else:
        fn=interp2d(pts[:,0],pts[:,1],z,kind='linear')
        interpd=fn(xx,yy)[:,:,0]
    return interpd

def remove_ramp(phase,filt):
    yl,xl=np.shape(phase)
    x = np.linspace(0,xl,xl);y = np.linspace(0,yl,yl)
    xx, yy = np.meshgrid(x, y);
    A=np.hstack((np.reshape(xx[filt],(np.sum(filt),1)),np.reshape(yy[filt],(np.sum(filt),1)),np.ones((np.sum(filt),1))))
    z=np.reshape(phase[filt],(np.sum(filt),1))
    invA=np.linalg.pinv(A)
    coeffs=np.matrix(invA)*np.matrix(z)
    ramp=np.multiply(xx,coeffs[0])+np.multiply(yy,coeffs[1])+coeffs[2]
    deramped=phase-ramp
    return deramped,ramp

def make_meshgrid(fname):
    ds=gdal.Open(fname)
    gtr=ds.GetGeoTransform()
    nx=ds.RasterXSize;ny=ds.RasterYSize
    xmin=gtr[0];xmax=gtr[0]+gtr[1]*nx;ymax=gtr[3];ymin=gtr[3]+gtr[5]*ny
    x=np.linspace(xmin,xmax,nx);y=np.linspace(ymax,ymin,ny)
    xx, yy = np.meshgrid(x, y);
    return xx,yy