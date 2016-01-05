#!/usr/bin/env python

import netCDF4 as nc
import numpy as np

f=nc.Dataset('sgridA.nc')
g=nc.Dataset('sgridB.nc')
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

fout=nc.Dataset('ocean_hgrid.nc','w',format='NETCDF3_CLASSIC')

ny=area.shape[0]; nx = area.shape[1]
nyp=ny+1; nxp=nx+1

print 'ny,nx= ',ny,nx

nyp=fout.createDimension('nyp',nyp)
nxp=fout.createDimension('nxp',nxp)
ny=fout.createDimension('ny',ny)
nx=fout.createDimension('nx',nx)
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
anglev[:]=angle_dx            

fout.sync()
fout.close()
