import numpy as np
from scipy import io
import matplotlib.pyplot as plt
from osgeo import gdal

def calc_tm(flist):

    fnames=np.genfromtxt(flist,dtype='str')
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
    dates=full
    return tm,dates

def sbas_linear(Tm,phase_s,r_ref,az_ref):

# least squares solution for pixel time series
# SBAS least squares
# at Each pixel, we solve for velocity at (n-1) time inverval

    import numpy as np
    n=np.shape(Tm)[1]+1;
    
    nr_s,naz_s,na = np.shape(phase_s);
    velocity=np.zeros((nr_s,naz_s,n-1));
    error=np.zeros(np.shape(velocity));
    
    Tminv=np.linalg.pinv(Tm)
    print(np.shape(Tminv))
    
    for jj in range(naz_s):
        print(jj);
#        print('test')
        for ii in range(nr_s):
            d=phase_s[ii,jj,:]-phase_s[r_ref,az_ref,:];
            d=np.reshape(d,(len(d),1))
#            print('test')
#            print(np.shape(d))
            #velocity(ii,jj,:)=Tm\d;
            v=np.matrix(Tminv)*np.matrix(d);
#            print(np.shape(v))
            velocity[ii,jj,:]=np.reshape(v,(1,1,len(v)));
            err=abs(Tm*v-d);
            err1=Tminv*err
            error[ii,jj,:]=np.reshape(err1,(1,1,len(err1)));
    
    return velocity,error

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

    
def posfromvel(velocity,dates,lambd=5.6):
# calculates the position, in cm, from velocity (in radians/day), and the dates,
# in decyear format
    sizex,sizey,t = np.shape(velocity);
    t = t+1;
    pos = np.zeros((sizex,sizey,t));
    days = np.round(np.diff(dates)*365.25);
    velocity = velocity*lambd/(4*np.pi); 
    for tt in range(1,t):
        pos[:,:,tt] = pos[:,:,tt-1]+velocity[:,:,tt-1]*days[tt-1];
    return pos

def calc_mean_vel(pos,dates):
    sizey,sizex,_=np.shape(pos)
    meanvel=np.zeros((sizey,sizex))
    for yy in range(sizey):
        for xx in range(sizex):
            p=pos[yy,xx,:]
            A=np.hstack((np.ones((len(dates),1)),np.reshape(dates,(len(dates),1))))
            invA=np.linalg.pinv(A)
            coeffs=np.matrix(invA)*np.matrix(np.reshape(p,(len(p),1)))
            meanvel[yy,xx]=coeffs[1]
    return meanvel

def saveraster(data,drivername,fname,gtr,proj,datatype):
    driver = gdal.GetDriverByName(drivername)
    size=np.shape(data)
    outRaster = driver.Create(fname, size[1], size[0], 1, datatype)
    outRaster.SetGeoTransform(gtr)
    outRaster.SetProjection(proj)
    outBand = outRaster.GetRasterBand(1) 
    outBand.WriteArray(data,0,0)

def correlate_baseline(phase,igram_list,names_fname,baseline_dat_fname,col=4):
    # this calculates the correlation between phase and baseline at each pixel. if correlation 
    # is high, there are DEM errors.
    # make a list with names of igrams, make a list of names of individual sar scenes
    dat=np.genfromtxt(baseline_dat_fname)
    dat2=np.genfromtxt(igram_list,dtype='str')
    sp_baseline=dat[:,col]
    name=np.genfromtxt(names_fname,dtype='str')
    sp_baseline_full=np.zeros(np.shape(dat2))
    for kk in range(np.shape(sp_baseline_full)[0]):
        i1=dat2[kk].split(':')[0];i2=dat2[kk].split(':')[1]
        ind1=np.where(name==i1);ind2=np.where(name==i2)
        sp_baseline_full[kk]=sp_baseline[ind1[0][0]]-sp_baseline[ind2[0][0]]
    sizey,sizex,_=np.shape(phase)
    coeff=np.zeros((sizey,sizex))
    for yy in range(sizey):
        for xx in range(sizex):
            p=phase[yy,xx,:]
            A=np.hstack((np.ones((len(sp_baseline_full),1)),np.reshape(sp_baseline_full,(len(sp_baseline_full),1))))
            invA=np.linalg.pinv(A)
            coeffs=np.matrix(invA)*np.matrix(np.reshape(p,(len(p),1)))
            coeff[yy,xx]=coeffs[1]
            p_est=coeffs[1]*sp_baseline_full
            phase[yy,xx,:]=phase[yy,xx,:]-p_est
    return sp_baseline_full,coeff,phase
