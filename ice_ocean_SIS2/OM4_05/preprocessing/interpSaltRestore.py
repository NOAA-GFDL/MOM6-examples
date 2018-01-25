#!/usr/bin/env python

from midas.rectgrid import *
import netCDF4 as nc
import numpy as np

sgrid=supergrid(file='ocean_hgrid.nc')
grid=quadmesh(supergrid=sgrid,cyclic=True)
fnam='woa13_decav_s_0-10m.mon_01v2.nc'
grid_in=quadmesh(fnam,var='s_u10a',cyclic=True)
S=state(fnam,grid=grid_in,fields=['s_u10a'])
S.rename_field('s_u10a','salt')
vd=S.var_dict['salt']
vd['dates']=nc.num2date(vd['tax_data'],units='days since 1900-01-01 00:00:00',calendar='julian')
vd['tbax_data'][0]=0. # align start date
vd['date_bounds']=nc.num2date(vd['tbax_data'],units='days since 1900-01-01 00:00:00',calendar='julian')
vd['calendar']='julian'
vd['Z']=None
SM=S.horiz_interp('salt',target=grid,src_modulo=True)
SM.var_dict['salt']['xax_data']=grid.x_T[0,:]
SM.var_dict['salt']['yax_data']=grid.y_T[:,grid.im/4]
SM.salt=np.ma.filled(SM.salt,0.)
fnam_out='salt_restore.nc'
SM.write_nc(fnam_out,fields=['salt'])
