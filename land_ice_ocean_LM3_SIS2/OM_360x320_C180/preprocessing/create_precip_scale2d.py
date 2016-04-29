# IPython log file

from midas.rectgrid import *
import matplotlib.pyplot as plt
import netCDF4 as nc
import numpy as np

f=nc.Dataset('precip_factor.nc','w',format='NETCDF3_CLASSIC')
x=np.linspace(0.,360.,721)
y=np.linspace(-90.,90.,361)
X,Y=np.meshgrid(x,y)
sgrid=supergrid(xdat=X, ydat=Y, cyclic_x=True)
grid=quadmesh(supergrid=sgrid)
f.createDimension('lon',grid.im)
f.createDimension('lat',grid.jm)
timed=f.createDimension('time',0)
timev=f.createVariable('time','f8',('time'))
lonv=f.createVariable('lon','f8',('lon'))
latv=f.createVariable('lat','f8',('lat'))
timev.calendar='julian'
timev.modulo='yes'
timev.units='days since 1900-01-01 00:00:00'
timev.cartesian_axis='T'
lonv.units='degrees_E'
lonv.modulo='yes'
lonv.cartesian_axis='X'
latv.units='degrees_N'
latv.cartesian_axis='Y'
lonv[:]=grid.lonh
latv[:]=grid.lath
precip_scale = np.ones(grid.wet.shape)
precip_scale[grid.y_T>40]=np.cos((grid.y_T[grid.y_T>40.]-40.)*np.pi/180.)
v=f.createVariable('precip_factor','f8',('time','lat','lon'))
v[0,:]=precip_scale
timev[0]=0.
f.sync()
f.close()

