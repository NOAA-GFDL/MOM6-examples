import numpy
import netCDF4
from hashlib import sha1

# Open Davies dataset in netcdf form see https://github.com/adcroft/convert_Davies_2013
nc = netCDF4.Dataset('convert_Davies_2013/ggge20271-sup-0003-Data_Table1_Eq_lon_lat_Global_HF.nc','r')

# Read dataset cell-center locations and mean heat flow (W/m2)
lat,lon = nc.variables['lat'][:], nc.variables['lon'][:]
mean_HF = nc.variables['mean_HF']
print('Hash of Davies heat flow: ', sha1(mean_HF[:]).hexdigest())

# Supergrid for OM4_025 (generated locally)
gf = netCDF4.Dataset('ocean_hgrid.nc','r')

# Read super grid node locations
xf,yf = gf.variables['x'][:], gf.variables['y'][:]

def linterp(lat,lon,Q,yf,xf):
    "Regrids Q with bi-linear interpolation from (lat,lon) to (yf,xf)"
    ni,nj = numpy.shape(lon)[0], numpy.shape(lat)[0]
    xi, yj = (numpy.mod(xf+180.,360))*(ni/360.), (yf+90.)*(nj/180.) # Floating point coords 0<=xi<=ni, 0<=yj<=nj
    wx,wy = numpy.mod(xi+0.5,1.), numpy.mod(yj+0.5,1.) # Weights
    # Calculate indices of model nodes within dataset (takes advantage of uniform resolution of dataset)
    indw, inds = numpy.floor(xi-0.5).astype(int), numpy.floor(yj-0.5).astype(int) # i,j of node to west, south
    inde, indn = numpy.floor(xi+0.5).astype(int), numpy.floor(yj+0.5).astype(int) # i,j of node to east, north
    indw, inde = numpy.mod(indw, ni), numpy.mod(inde, ni) # Periodic in x
    indn = numpy.minimum(indn, nj-1) # Leads to PCM representation for yj>0.5 in northern row
    return (wy*wx*Q[indn,inde] + (1-wy)*(1-wx)*Q[inds,indw]) + (wy*(1-wx)*Q[indn,indw] + (1-wy)*wx*Q[inds,inde])

# Interpolate to super-grid
hff = linterp(lat,lon,mean_HF[:],yf,xf) # Heat flux on fine grid nodes

# Integrate with Trapezoidal rule to model grid
hf = 0.5*hff[1::2,:]+0.25*(hff[:-1:2,:]+hff[2::2,:])
hf = 0.5*hf[:,1::2]+0.25*(hf[:,:-1:2]+hf[:,2::2])
print('Hash of re-gridded heat flow: ', sha1(hf[:]).hexdigest())

# Create geothermal netcdf file
with netCDF4.Dataset('geothermal_davies2013_v1.nc', 'w', format='NETCDF3_64BIT') as newfile:
    newfile.title = 'Geothermal heat flow from Davies, 2013, re-gridded to OM4_025'
    newfile.reference = nc.reference
    newfile.reference_url = nc.reference_url
    #newfile.history = numpy.compat.asstr(nc.history[:])+'\nRegridded using Jupyter notebook at https://github.com/NOAA-GFDL/MOM6-examples/blob/dev/master/ice_ocean_SIS2/OM4_025/preprocessing/'
    dj = newfile.createDimension('j', hf.shape[0])
    di = newfile.createDimension('i', hf.shape[1])
    vj = newfile.createVariable('j','f',('j',))
    vj.long_name = 'Grid j-index'
    vi = newfile.createVariable('i','f',('i',))
    vi.long_name = 'Grid i-index'
    vh = newfile.createVariable('geothermal_hf','f',('j','i',))
    vh.long_name = mean_HF.long_name
    vh.standard_name = mean_HF.standard_name
    vh.units = mean_HF.units
    vh.cell_methods = mean_HF.cell_methods
    vh.sha1 = sha1(hf).hexdigest()
    vj[:] = numpy.arange(0.5,hf.shape[0])
    vi[:] = numpy.arange(0.5,hf.shape[1])
    vh[:] = hf[:]
