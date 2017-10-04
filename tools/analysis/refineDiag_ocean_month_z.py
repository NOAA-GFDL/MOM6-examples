#!/usr/bin/env python

import argparse
import m6toolbox
import netCDF4 as nc
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
from verticalvelocity import calc_w_from_convergence
from strait_transport_timeseries import sum_transport_in_straits
##-- RefineDiag Script for CMIP6
##
##   Variables we intend to provide in z-coordinates:
##
##     msftyyz    -> vmo  (ocean_z)  * both 0.25 and 0.5 resolutions
##     msftyzmpa  -> vhGM (ocean_z)  * applies only to 0.5 resolution
##     msftyzsmpa -> vhml (ocean_z)  * both 0.25 and 0.5 resolutions
##
##
##   Variables we intend to provide in rho-coordinates:
##   (potenital density referenced to 2000 m)
##
##     msftyrho    -> vmo
##     msftyrhompa -> vhGM           * applies only to 0.5 resolution
##
##
##   2-D variables we intent to provide:
##
##     hfy  ->  T_ady_2d + ndiff_tracer_trans_y_2d_T   * T_ady_2d needs to be converted to Watts (Cp = 3992.)
##                                                       ndiff_tracer_trans_y_2d_T already in Watts
##                                                       advective term in both 0.25 and 0.5 resolutions
##                                                       diffusive term only in 0.5 resolution
##
##     hfx  -> same recipie as above, expect for x-dimension
##     hfbasin -> summed line of hfy in each basin
##
##
##   Outstanding issues
##     1.) regirdding of vh, vhGM to rho-corrdinates
##     2.) vhGM and vhML units need to be in kg s-1
##     2.) save out RHO_0 and Cp somewhere in netCDF files to key off of
##
##
##   CMIP variables that will NOT be provided:
##
##     hfbasinpmadv, hfbasinpsmadv, hfbasinpmdiff, hfbasinpadv
##     (We advect the tracer with the residual mean velocity; individual terms cannot be diagnosed)
##
##     htovgyre, htovovrt, sltovgyre, sltovovrt
##     (Code for offline calculation not ready.)
##
##--

def run():
    parser = argparse.ArgumentParser(description='''CMIP6 RefineDiag Script for OM4''')
    parser.add_argument('infile', type=str, help='''Input file''')
    parser.add_argument('-b','--basinfile', type=str, default='', required=True, help='''File containing OM4 basin masks''')
    parser.add_argument('-s','--straitdir', type=str, default='', required=True, help='''Directory containing output for straits''')
    parser.add_argument('-o','--outfile', type=str, default=None, help='''Output file name''')
    parser.add_argument('-r','--refineDiagDir', type=str, default=None, help='''Path to refineDiagDir defined by FRE workflow)''')
    args = parser.parse_args()
    main(args)

def main(args):
    nc_misval = 1.e20
    #-- Define Regions and their associated masks
    #   Note: The Atlantic should include other smaller bays/seas that are
    #         included in the definition used in meridional_overturning.py

    region = np.array(['atlantic_arctic_ocean','indian_pacific_ocean','global_ocean'])

    #-- Read basin masks
    f_basin = nc.Dataset(args.basinfile)
    basin_code = f_basin.variables['basin'][:]

    atlantic_arctic_mask = basin_code * 0.
    atlantic_arctic_mask[(basin_code==2) | (basin_code==4) | (basin_code==6) | (basin_code==7) | (basin_code==8)] = 1.

    indo_pacific_mask = basin_code * 0.
    indo_pacific_mask[(basin_code==3) | (basin_code==5)] = 1.

    #-- Read model data
    f_in = nc.Dataset(args.infile)

    #-- Read in existing dimensions from history netcdf file
    xh  = f_in.variables['xh']
    yh  = f_in.variables['yh']
    yq  = f_in.variables['yq']
    z_l = f_in.variables['z_l']
    z_i = f_in.variables['z_i']
    tax = f_in.variables['time']

    #-- Note: based on conversations with @adcroft, the overturning should be reported on the interfaces, z_i.
    #   Also, the nominal latitude is insufficient for the basin-average fields.  Based on the methods in 
    #   meridional_overturning.py, the latitude dimension should be:
    #
    #   y = netCDF4.Dataset(cmdLineArgs.gridspec+'/ocean_hgrid.nc').variables['y'][::2,::2]
    #   yy = y[1:,:].max(axis=-1)+0*z
    #
    #   The quanity 'yy' above is numerically-equivalent to 'yq'

    #-- msftyyz
    varname = 'vmo'
    msftyyz = np.ma.ones((len(tax),3,len(z_i),len(yq)))*0.
    msftyyz[:,0,:,:] = m6toolbox.moc_maskedarray(f_in.variables[varname][:],mask=atlantic_arctic_mask)
    msftyyz[:,1,:,:] = m6toolbox.moc_maskedarray(f_in.variables[varname][:],mask=indo_pacific_mask)
    msftyyz[:,2,:,:] = m6toolbox.moc_maskedarray(f_in.variables[varname][:])
    msftyyz[msftyyz.mask] = nc_misval
    msftyyz = np.ma.array(msftyyz,fill_value=nc_misval)
    msftyyz.long_name = 'Ocean Y Overturning Mass Streamfunction'
    msftyyz.units = 'kg s-1'
    msftyyz.cell_methods = 'z_i:sum yq:sum basin:mean time:mean'
    msftyyz.time_avg_info = 'average_T1,average_T2,average_DT'
    msftyyz.standard_name = 'ocean_y_overturning_mass_streamfunction'

    #-- msftyzmpa
    varname = 'vhGM'
    msftyzmpa = np.ma.ones((len(tax),3,len(z_i),len(yq)))*0.
    msftyzmpa[:,0,:,:] = m6toolbox.moc_maskedarray(f_in.variables[varname][:],mask=atlantic_arctic_mask)
    msftyzmpa[:,1,:,:] = m6toolbox.moc_maskedarray(f_in.variables[varname][:],mask=indo_pacific_mask)
    msftyzmpa[:,2,:,:] = m6toolbox.moc_maskedarray(f_in.variables[varname][:])
    msftyzmpa[msftyzmpa.mask] = nc_misval
    msftyzmpa = np.ma.array(msftyzmpa,fill_value=nc_misval)
    msftyzmpa.long_name = 'ocean Y overturning mass streamfunction due to parameterized mesoscale advection'
    msftyzmpa.units = 'kg s-1'
    msftyzmpa.cell_methods = 'z_i:sum yq:sum basin:mean time:mean'
    msftyzmpa.time_avg_info = 'average_T1,average_T2,average_DT'
    msftyzmpa.standard_name = 'ocean_y_overturning_mass_streamfunction_due_to_parameterized_'+\
                              'mesoscale_advection'

    #-- msftyzsmpa
    varname = 'vhml'
    msftyzsmpa = np.ma.ones((len(tax),3,len(z_i),len(yq)))*0.
    msftyzsmpa[:,0,:,:] = m6toolbox.moc_maskedarray(f_in.variables[varname][:],mask=atlantic_arctic_mask)
    msftyzsmpa[:,1,:,:] = m6toolbox.moc_maskedarray(f_in.variables[varname][:],mask=indo_pacific_mask)
    msftyzsmpa[:,2,:,:] = m6toolbox.moc_maskedarray(f_in.variables[varname][:])
    msftyzsmpa[msftyzsmpa.mask] = nc_misval
    msftyzsmpa = np.ma.array(msftyzsmpa,fill_value=nc_misval)
    msftyzsmpa.long_name = 'ocean Y overturning mass streamfunction due to parameterized submesoscale advection'
    msftyzsmpa.units = 'kg s-1'
    msftyzsmpa.cell_methods = 'z_i:sum yq:sum basin:mean time:mean'
    msftyzsmpa.time_avg_info = 'average_T1,average_T2,average_DT'
    msftyzsmpa.standard_name = 'ocean_meridional_overturning_mass_streamfunction_due_to_parameterized_'+\
                               'submesoscale_advection'

    #-- wmo
    varname = 'wmo'
    wmo = calc_w_from_convergence(f_in.variables['umo'], f_in.variables['vmo'])
    wmo[wmo.mask] = nc_misval
    wmo = np.ma.array(wmo,fill_value=nc_misval)
    wmo.long_name = 'Upward mass transport from resolved and parameterized advective transport'
    wmo.units = 'kg s-1'
    wmo.cell_methods = 'z_i:sum xh:sum yh:sum time:mean'
    wmo.time_avg_info = 'average_T1,average_T2,average_DT'
    wmo.standard_name = 'upward_ocean_mass_transport'

    #-- mfo
    _, mfo, straits = sum_transport_in_straits(args.straitdir, monthly_average = True)
    #mfo[mfo.mask] = nc_misval
    mfo = np.ma.array(mfo, fill_value=nc_misval)
    strait_names = np.array( [strait.cmor_name for strait in straits] )
    mfo.long_name = 'Sea Water Transport'
    mfo.units = 'kg s-1'
    mfo.cell_methods = 'time:mean'
    mfo.time_avg_info = 'average_T1,average_T2,average_DT'
    mfo.standard_name = 'sea_water_transport_across_line'

    #-- Read time bounds
    nv = f_in.variables['nv']
    average_T1 = f_in.variables['average_T1']
    average_T2 = f_in.variables['average_T2']
    average_DT = f_in.variables['average_DT']
    time_bnds  = f_in.variables['time_bnds']

    #-- Generate output filename
    if args.outfile is None:
      if hasattr(f_in,'filename'):
          args.outfile = f_in.filename
      else:
          args.outfile = os.path.basename(args.infile)
      args.outfile = args.outfile.split('.')
      args.outfile[-2] = args.outfile[-2]+'_refined'
      args.outfile = '.'.join(args.outfile)

    if args.refineDiagDir is not None:
      args.outfile = args.refineDiagDir + '/' + args.outfile

    #-- Write output file
    try:
        os.remove(args.outfile)
    except:
        pass

    if os.path.exists(args.outfile):
        raise IOError('Output netCDF file already exists.')
        exit(1)

    f_out     = nc.Dataset(args.outfile, 'w', format='NETCDF3_CLASSIC')
    f_out.setncatts(f_in.__dict__)
    f_out.filename = args.outfile

    time_dim = f_out.createDimension('time', size=None)
    basin_dim = f_out.createDimension('basin', size=3)
    strait_dim = f_out.createDimension('strait', size=len(straits))
    strlen1_dim = f_out.createDimension('strlen1', size=21)
    strlen2_dim = f_out.createDimension('strlen2', size=31)
    xh_dim  = f_out.createDimension('xh',  size=len(xh[:]))
    yh_dim  = f_out.createDimension('yh',  size=len(yh[:]))
    yq_dim  = f_out.createDimension('yq',  size=len(yq[:]))
    z_l_dim = f_out.createDimension('z_l', size=len(z_l[:]))
    z_i_dim = f_out.createDimension('z_i', size=len(z_i[:]))
    nv_dim  = f_out.createDimension('nv',  size=len(nv[:]))

    time_out = f_out.createVariable('time', np.float64, ('time'))
    xh_out   = f_out.createVariable('xh',   np.float64, ('xh'))
    yh_out   = f_out.createVariable('yh',   np.float64, ('yh'))
    yq_out   = f_out.createVariable('yq',   np.float64, ('yq'))
    region_out = f_out.createVariable('region', 'c', ('basin', 'strlen1'))
    strait_out = f_out.createVariable('strait', 'c', ('strait', 'strlen2'))
    z_l_out  = f_out.createVariable('z_l',  np.float64, ('z_l'))
    z_i_out  = f_out.createVariable('z_i',  np.float64, ('z_i'))
    nv_out  = f_out.createVariable('nv',  np.float64, ('nv'))

    msftyyz_out = f_out.createVariable('msftyyz', np.float32, ('time', 'basin', 'z_i', 'yq'), fill_value=nc_misval)
    msftyyz_out.missing_value = nc_misval

    msftyzsmpa_out = f_out.createVariable('msftyzsmpa', np.float32, ('time', 'basin', 'z_i', 'yq'), fill_value=nc_misval)
    msftyzsmpa_out.missing_value = nc_misval

    msftyzmpa_out = f_out.createVariable('msftyzmpa', np.float32, ('time', 'basin', 'z_i', 'yq'), fill_value=nc_misval)
    msftyzmpa_out.missing_value = nc_misval

    wmo_out = f_out.createVariable('wmo', np.float32, ('time', 'z_i', 'yh', 'xh'), fill_value=nc_misval)
    wmo_out.missing_value = nc_misval

    mfo_out = f_out.createVariable('mfo', np.float32, ('time', 'strait'), fill_value=nc_misval)
    mfo_out.missing_value = nc_misval

    average_T1_out = f_out.createVariable('average_T1', np.float64, ('time'))
    average_T2_out = f_out.createVariable('average_T2', np.float64, ('time'))
    average_DT_out = f_out.createVariable('average_DT', np.float64, ('time'))
    time_bnds_out  = f_out.createVariable('time_bnds',  np.float64, ('time', 'nv'))

    time_out.setncatts(tax.__dict__)
    xh_out.setncatts(xh.__dict__)
    yh_out.setncatts(yh.__dict__)
    yq_out.setncatts(yq.__dict__)
    z_l_out.setncatts(z_l.__dict__)
    z_i_out.setncatts(z_i.__dict__)
    nv_out.setncatts(nv.__dict__)

    for k in msftyyz.__dict__.keys():
      if k[0] != '_': msftyyz_out.setncattr(k,msftyyz.__dict__[k])

    for k in msftyzsmpa.__dict__.keys():
      if k[0] != '_': msftyzsmpa_out.setncattr(k,msftyzsmpa.__dict__[k])

    for k in msftyzmpa.__dict__.keys():
      if k[0] != '_': msftyzmpa_out.setncattr(k,msftyzmpa.__dict__[k])

    for k in mfo.__dict__.keys():
      if k[0] != '_': mfo_out.setncattr(k,mfo.__dict__[k])

    for k in wmo.__dict__.keys():
      if k[0] != '_': wmo_out.setncattr(k,wmo.__dict__[k])

    average_T1_out.setncatts(average_T1.__dict__)
    average_T2_out.setncatts(average_T2.__dict__)
    average_DT_out.setncatts(average_DT.__dict__)
    time_bnds_out.setncatts(time_bnds.__dict__)

    time_out[:] = np.array(tax[:])
    xh_out[:] = np.array(xh[:])
    yh_out[:] = np.array(yh[:])
    yq_out[:] = np.array(yq[:])
    z_l_out[:] = np.array(z_l[:])
    z_i_out[:] = np.array(z_i[:])
    nv_out[:] = np.array(nv[:])

    msftyyz_out[:] = np.ma.array(msftyyz[:])
    msftyzsmpa_out[:] = np.ma.array(msftyzsmpa[:])
    msftyzmpa_out[:] = np.ma.array(msftyzmpa[:])
    wmo_out[:] = np.ma.array(wmo[:])
    mfo_out[:] = np.array(mfo[:])

    average_T1_out[:] = average_T1[:]
    average_T2_out[:] = average_T2[:]
    average_DT_out[:] = average_DT[:]
    time_bnds_out[:]  = time_bnds[:]

    print(region.shape)
    print(strait_names.shape)
    region_out[:] = nc.stringtochar(region)
    strait_out[:] = nc.stringtochar(strait_names)
    f_out.close()

    exit(0)

if __name__ == '__main__':
  run()
