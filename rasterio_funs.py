from osgeo import gdal
import os
import numpy as np
import matplotlib.pyplot as plt
from glob import glob
from scipy import io
from osgeo import osr
from rasterio.warp import reproject
import rasterio
from rasterio.plot import show
from rasterio import Affine

def loadraster(rastername):
    ds=gdal.Open(rastername)
    band=ds.GetRasterBand(1)
    data=band.ReadAsArray()
    # gtr=ds.GetGeoTransform()
    return data, ds

def saveraster(data,fname,lon,lat,xres,yres,drivername='GTiff',epsg='4326',datatype=6):
    driver = gdal.GetDriverByName(drivername)
    size=np.shape(data)
    sr = osr.SpatialReference()
    sr.SetProjection ("EPSG:"+epsg)
    sr_wkt = sr.ExportToWkt()
    outRaster = driver.Create(fname, size[1], size[0], 1, datatype)
    gtr=(lon,xres,0.0,lat,0.0,-yres)
    outRaster.SetGeoTransform(gtr)
    outRaster.SetProjection(sr_wkt)
    outBand = outRaster.GetRasterBand(1) 
    outBand.WriteArray(data,0,0)
    
def saveraster_rasterio(data,fname,lon,lat,xres,yres,drivername='GTiff',epsg=4326,datatype='float32',bands=1):
    transform=Affine(xres,0.0,lon,0.0,-yres,lat)
    # data_new=np.reshape(data,(bands,data.shape[0],data.shape[1]))
    crs=rasterio.crs.CRS.from_epsg(epsg)
    with rasterio.open(
            fname,'w',driver=drivername,
            height=data.shape[0],
            width=data.shape[1],
            count=bands,
            dtype=datatype,
            crs=crs,
            transform=transform) as dst:
        dst.write(np.float32(data),bands)
        
def reproject_rasterio(src,dest):
    dat,transform=reproject(rasterio.band(src,1),dest.read(1),
              dst_crs=dest.crs,dst_resolution=dest.res,
              dst_transform=dest.transform,
              dst_nodata=np.nan)
    return(dat,transform)

