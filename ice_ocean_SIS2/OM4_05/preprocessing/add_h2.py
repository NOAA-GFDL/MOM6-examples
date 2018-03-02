import netCDF4 as nc
import numpy as np

f=nc.Dataset('ocean_topog.nc','a')
rgH2=f.createVariable('h2','f4',('ny','nx'))
rgH2.units='m^2'
rgH2.standard_name='Variance of sub-grid scale topography'
rgH2[:] = f.variables['std'][:]**2
f.sync()
f.close()



