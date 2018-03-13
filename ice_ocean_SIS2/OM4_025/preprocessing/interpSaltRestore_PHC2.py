#!/usr/bin/env python

from midas.rectgrid import *
import netCDF4 as nc
import numpy as np

sgrid=supergrid(file='ocean_hgrid.nc')
grid=quadmesh(supergrid=sgrid,cyclic=True)
fnam='PHC2_salx.2004_08_03.corrected.nc'
grid_in=quadmesh(fnam,var='SALT',cyclic=True)
S=state(fnam,grid=grid_in,fields=['SALT'])
S.rename_field('SALT','salt')
vd=S.var_dict['salt']
#vd['tax_data']=[15., 45.,76.,106.,136.,168.,198.,228.,258.,288.,320.,350.]
#vd['dates']=nc.num2date(vd['tax_data'],units='days since 1900-01-01 00:00:00',calendar='julian')
#vd['tbax_data'][0]=0. # align start date
#vd['date_bounds']=nc.num2date(vd['tbax_data'],units='days since 1900-01-01 00:00:00',calendar='julian')
#vd['calendar']='julian'
#vd['Z']=None
SM=S.horiz_interp('salt',target=grid,src_modulo=True)
SM.var_dict['salt']['xax_data']=grid.x_T[0,:]
SM.var_dict['salt']['yax_data']=grid.y_T[:,grid.im/4]
SM.salt=np.ma.filled(SM.salt,0.)
fnam_out='salt_restore_PHC2.nc'
SM.write_nc(fnam_out,fields=['salt'])
