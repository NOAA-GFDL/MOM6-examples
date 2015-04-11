
from scipy.interpolate import interp1d
from midas.rectgrid import *
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, cm
import netCDF4 as nc


# In[161]:

lat0=-65.
lon0=-300.
lenlat=125.
lenlon=360.
nlon=360*2
nlat=500*2
mercator=supergrid(nlon,nlat,'mercator','degrees',lat0,lenlat,lon0,lenlon,cyclic_x=True)
mercator.grid_metrics()
#get_ipython().magic(u'matplotlib inline')
phi=mercator.y[:,0]
dphi=phi[1:]-phi[0:-1]
plt.plot(phi[1:],2.0*dphi)
plt.title('Mercator N/S resolution')


# In[162]:

#get_ipython().magic(u'matplotlib inline')
phi=mercator.y[:,0]
dphi=phi[1:]-phi[0:-1]
jind=np.where(phi>-20.)[0][0]
jind=jind+np.mod(jind,2)
phi=phi[0:jind]
dphi=dphi[0:jind]
N=26
phi_s = phi[-1]
dphi_s = dphi[-1]
phi_e = -10.
dphi_e = 0.2
nodes = [0,1,N-2,N-1]
phi_nodes = [phi_s,phi_s+dphi_s,phi_e-dphi_e,phi_e]
f2=interp1d(nodes,phi_nodes,kind=3)
jInd2=np.arange(N)
phi2=f2(jInd2)
dphi2=phi2[1:]-phi2[0:-1]
phi=np.concatenate((phi[0:-1],phi2))
dphi=phi[1:]-phi[0:-1]

N=56
phi_s = phi[-1]
phi2=np.linspace(phi_s,0,N)
dphi2=phi2[1:]-phi2[0:-1]
PHI=np.concatenate((phi[0:-1],phi2))
PHI=np.concatenate((PHI[0:-1],-PHI[::-1]))

DPHI=PHI[1:]-PHI[0:-1]
plt.plot(PHI[1:],2*DPHI)


# In[163]:

LAMBDA=np.linspace(lon0,lon0+360.,nlon+1)
jind=np.where(PHI>-78.)[0][0]
jind=jind+np.mod(jind,2)
jind2=np.where(PHI>60.)[0][0]
jind2=jind2+np.mod(jind2,2)

PHI2=PHI[jind:jind2-1]
DPHI2=PHI2[1:]-PHI2[0:-1]
x,y = np.meshgrid(LAMBDA,PHI2)
gridB = supergrid(xdat=x,ydat=y,axis_units='degrees',cyclic_x=True)
gridB.grid_metrics()
gridB.write_nc('flor_gridB.nc')


# In[164]:

ny_ncap=155
phi_tps = PHI2[-1]
dphi_tps = DPHI2[-1]
nodes = [0,1,ny_ncap-2,ny_ncap-1]
phi_tp_nodes = [phi_tps,phi_tps+dphi_tps,89.9,90.]
ftp=interp1d(nodes,phi_tp_nodes,kind=3)
jInd2=np.arange(ny_ncap)
phitp=ftp(jInd2)
dphitp=phitp[1:]-phitp[0:-1]
plt.plot(phitp[0:-1],2*dphitp)
plt.title('Model N/S Arctic resolution (prior to transform)')


# In[165]:

lat0_tp = PHI2[-1]
XTP,YTP=np.meshgrid(LAMBDA,phitp)
gridC=supergrid(xdat=XTP,ydat=YTP,axis_units='degrees',tripolar_n=True)
gridC.grid_metrics()
gridC.write_nc('flor_gridC.nc')


### Combine grids

# In[166]:

f=nc.Dataset('flor_gridB.nc')
g=nc.Dataset('flor_gridC.nc')

y1=f.variables['y'][:]
y2=g.variables['y'][:]
y=np.concatenate((y1,y2[1:,:]),axis=0)

dy1=f.variables['dy'][:]
dy2=g.variables['dy'][:]
dy=np.concatenate((dy1,dy2),axis=0)

x1=f.variables['x'][:]
x2=g.variables['x'][:]
x=np.concatenate((x1,x2[1:,:]),axis=0)

dx1=f.variables['dx'][:]
dx2=g.variables['dx'][:]
dx=np.concatenate((dx1,dx2[1:,:]),axis=0)


area1=f.variables['area'][:]
area2=g.variables['area'][:]
area=np.concatenate((area1,area2),axis=0)

angle_dx1=f.variables['angle_dx'][:,:]
angle_dx2=g.variables['angle_dx'][:-1,:]
angle_dx=np.concatenate((angle_dx1,angle_dx2),axis=0)

fout=nc.Dataset('supergrid.nc','w',format='NETCDF3_CLASSIC')

ny=area.shape[0]; nx = area.shape[1]
nyp=ny+1; nxp=nx+1

fout.createDimension('nyp',nyp)
fout.createDimension('nxp',nxp)
fout.createDimension('ny',ny)
fout.createDimension('nx',nx)
string=fout.createDimension('string',255)    

tile=fout.createVariable('tile','S1',('string'))
yv=fout.createVariable('y','f8',('nyp','nxp'))
xv=fout.createVariable('x','f8',('nyp','nxp'))    
yv.units='degrees'
xv.units='degrees'
yv[:]=y
xv[:]=x

tile[0:4]='tile1'
dyv=fout.createVariable('dy','f8',('ny','nxp'))
dyv.units='meters'
dyv[:]=dy
dxv=fout.createVariable('dx','f8',('nyp','nx'))
dxv.units='meters'
dxv[:]=dx
areav=fout.createVariable('area','f8',('ny','nx'))
areav.units='m2'
areav[:]=area
anglev=fout.createVariable('angle_dx','f8',('nyp','nxp'))
anglev.units='degrees'
print nxp,nyp
print angle_dx.shape
anglev[:]=angle_dx            

fout.sync()
fout.close()


### Load the final supergrid and create a model grid

# In[167]:

sgrid=supergrid(file='supergrid.nc',cyclic_x=True,tripolar_n=True)
grid=quadmesh(supergrid=sgrid)
print 'Total number of i grid points = ',grid.im
print 'Total number of j grid points = ',grid.jm
print 'Closest grid point to the equator =',grid.lath[np.where(np.abs(grid.lath)<0.2)[0]]


# In[168]:

aiso1=grid.dyh[:,0]/grid.dxh[:,0]
aiso2=1.0/aiso1
aiso = np.maximum(aiso1,aiso2)
#plt.plot(grid.lath,aiso1,color='b')
#plt.plot(grid.lath,aiso2,color='g')
plt.plot(grid.lath,aiso,color='c')

plt.plot([grid.lath[0],grid.lath[-1]],[1.,1.],'r--')
plt.xlim(-80,50)
plt.ylim(0.25,3)
plt.title('Grid Anisotropy (nd)')


# In[169]:

#get_ipython().magic(u'matplotlib inline')
print grid.x_T.min(),grid.x_T.max()
plt.pcolormesh(grid.x_T,grid.y_T,grid.dxh*grid.dyh)
plt.xlim(-300,60)
plt.ylim(-90,90)
plt.title('Cell Area')
plt.colorbar()


# In[172]:

wd=6667000.
ht=6667000.
m =  Basemap(projection='stere',width=wd,height=ht,lon_0=0.0,lat_ts=70.,lat_0=90.,resolution='l')
xx=grid.x_T.copy()
yy=grid.y_T.copy()
xx[xx<-180]=xx[xx<-180]+360.
xplt,yplt=m(xx,yy,inverse=False)
aiso = grid.dyh/grid.dxh
aiso = np.maximum(aiso,1.0/aiso)
cf=m.contourf(xplt,yplt,aiso,np.linspace(1.0,3,10))
#m.contourf(xplt,yplt,aiso)
#cl=m.contour(xplt,yplt,aiso,np.linspace(1.0,2.0,10),colors='k')
#plt.clabel(cl)
m.drawcoastlines()
plt.title('Tripolar Anisotropy')
plt.colorbar(cf)


# In[171]:

wd=6667000.
ht=6667000.
m =  Basemap(projection='stere',width=wd,height=ht,lon_0=0.0,lat_ts=70.,lat_0=90.,resolution='l')
xx=grid.x_T
yy=grid.y_T
xx[xx<-180]=xx[xx<-180]+360.
xplt,yplt=m(xx,yy,inverse=False)
cf=m.contourf(xplt,yplt,grid.dxh*grid.dyh/1.e9,np.arange(0.1,3.6,.1),extend='both')
m.drawcoastlines()
m.drawparallels(np.arange(50.,90.,10.))
m.drawmeridians(np.arange(-180.,180.,15.))
plt.title('Tripolar grid cell Area')
plt.colorbar(cf)


# In[ ]:

ingrid=quadmesh('GEBCO_08_v2.nc',var='depth',simple_grid=True,cyclic=True)
TOPO=state('GEBCO_08_v2.nc',grid=ingrid,fields=['depth'])
TOPO.rename_field('depth','topo')
TOPO.var_dict['topo']['Ztype']='Fixed'
fnam = 'topog_gebco.nc'
R=TOPO.subtile('topo',target=grid)
R.write_nc(fnam,['mean','max','min','std','count'])


# In[ ]:



