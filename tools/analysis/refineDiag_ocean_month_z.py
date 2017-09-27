#!/usr/bin/env python

import argparse
import m6toolbox
import netCDF4 as nc
import numpy as np
import os
import sys
import matplotlib.pyplot as plt

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
    parser.add_argument('-o','--outfile', type=str, default=None, help='''Output file name''')
    parser.add_argument('-r','--refineDiagDir', type=str, default=None, help='''Path to refineDiagDir defined by FRE workflow)''')
    args = parser.parse_args()
    main(args)

def main(args):
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
    yh  = f_in.variables['yh']
    z_l = f_in.variables['z_l']
    z_i = f_in.variables['z_i']
    tax = f_in.variables['time']
    
    #-- msftyyz
    varname = 'vmo'
    msftyyz = np.ma.ones((len(tax),3,len(z_i),len(yh)))*0.
    msftyyz[:,0,:,:] = m6toolbox.moc_maskedarray(f_in.variables[varname][:],mask=atlantic_arctic_mask)
    msftyyz[:,1,:,:] = m6toolbox.moc_maskedarray(f_in.variables[varname][:],mask=indo_pacific_mask)
    msftyyz[:,2,:,:] = m6toolbox.moc_maskedarray(f_in.variables[varname][:])
    msftyyz[msftyyz.mask] = 1.e20
    msftyyz = np.ma.array(msftyyz,fill_value=1.e20)
    msftyyz.long_name = 'Ocean Y Overturning Mass Streamfunction'
    msftyyz.units = 'kg s-1'
    msftyyz.cell_methods = 'z_i:sum yh:sum basin:mean time:mean'
    msftyyz.time_avg_info = 'average_T1,average_T2,average_DT'
    msftyyz.standard_name = 'ocean_y_overturning_mass_streamfunction'

    #-- msftyzmpa
    varname = 'vhGM'
    msftyzmpa = np.ma.ones((len(tax),3,len(z_i),len(yh)))*0.
    msftyzmpa[:,0,:,:] = m6toolbox.moc_maskedarray(f_in.variables[varname][:],mask=atlantic_arctic_mask)
    msftyzmpa[:,1,:,:] = m6toolbox.moc_maskedarray(f_in.variables[varname][:],mask=indo_pacific_mask)
    msftyzmpa[:,2,:,:] = m6toolbox.moc_maskedarray(f_in.variables[varname][:])
    msftyzmpa[msftyzmpa.mask] = 1.e20
    msftyzmpa = np.ma.array(msftyzmpa,fill_value=1.e20)
    msftyzmpa.long_name = 'ocean Y overturning mass streamfunction due to parameterized mesoscale advection'
    msftyzmpa.units = 'kg s-1'
    msftyzmpa.cell_methods = 'z_i:sum yh:sum basin:mean time:mean'
    msftyzmpa.time_avg_info = 'average_T1,average_T2,average_DT'
    msftyzmpa.standard_name = 'ocean_y_overturning_mass_streamfunction_due_to_parameterized_'+\
                              'mesoscale_advection'

    #-- msftyzsmpa
    varname = 'vhml'
    msftyzsmpa = np.ma.ones((len(tax),3,len(z_i),len(yh)))*0.
    msftyzsmpa[:,0,:,:] = m6toolbox.moc_maskedarray(f_in.variables[varname][:],mask=atlantic_arctic_mask)
    msftyzsmpa[:,1,:,:] = m6toolbox.moc_maskedarray(f_in.variables[varname][:],mask=indo_pacific_mask)
    msftyzsmpa[:,2,:,:] = m6toolbox.moc_maskedarray(f_in.variables[varname][:])
    msftyzsmpa[msftyzsmpa.mask] = 1.e20
    msftyzsmpa = np.ma.array(msftyzsmpa,fill_value=1.e20)
    msftyzsmpa.long_name = 'ocean Y overturning mass streamfunction due to parameterized submesoscale advection'
    msftyzsmpa.units = 'kg s-1'
    msftyzsmpa.cell_methods = 'z_i:sum yh:sum basin:mean time:mean'
    msftyzsmpa.time_avg_info = 'average_T1,average_T2,average_DT'
    msftyzsmpa.standard_name = 'ocean_meridional_overturning_mass_streamfunction_due_to_parameterized_'+\
                               'submesoscale_advection'

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
    strlen_dim = f_out.createDimension('strlen', size=21)
    yh_dim  = f_out.createDimension('yh',  size=len(yh[:]))
    z_l_dim = f_out.createDimension('z_l', size=len(z_l[:]))
    z_i_dim = f_out.createDimension('z_i', size=len(z_i[:]))
    nv_dim  = f_out.createDimension('nv',  size=len(nv[:]))
    
    time_out = f_out.createVariable('time', np.float64, ('time'))
    #basin_out = f_out.createVariable('basin', np.int32, ('basin'))
    yh_out   = f_out.createVariable('yh',   np.float64, ('yh'))
    region_out = f_out.createVariable('region', 'c', ('basin', 'strlen'))
    z_l_out  = f_out.createVariable('z_l',  np.float64, ('z_l'))
    z_i_out  = f_out.createVariable('z_i',  np.float64, ('z_i'))
    nv_out  = f_out.createVariable('nv',  np.float64, ('nv'))
   
    msftyyz_out = f_out.createVariable('msftyyz', np.float32, ('time', 'basin', 'z_i', 'yh'), fill_value=1.e20)
    msftyyz_out.missing_value = 1.e20
 
    msftyzsmpa_out = f_out.createVariable('msftyzsmpa', np.float32, ('time', 'basin', 'z_i', 'yh'), fill_value=1.e20)
    msftyzsmpa_out.missing_value = 1.e20
 
    msftyzmpa_out = f_out.createVariable('msftyzmpa', np.float32, ('time', 'basin', 'z_i', 'yh'), fill_value=1.e20)
    msftyzmpa_out.missing_value = 1.e20
 
    average_T1_out = f_out.createVariable('average_T1', np.float64, ('time'))
    average_T2_out = f_out.createVariable('average_T2', np.float64, ('time'))
    average_DT_out = f_out.createVariable('average_DT', np.float64, ('time'))
    time_bnds_out  = f_out.createVariable('time_bnds',  np.float64, ('time', 'nv'))
    
    time_out.setncatts(tax.__dict__)
    yh_out.setncatts(yh.__dict__)
    z_l_out.setncatts(z_l.__dict__)
    z_i_out.setncatts(z_i.__dict__)
    nv_out.setncatts(nv.__dict__)

    for k in msftyyz.__dict__.keys():
      if k[0] != '_': msftyyz_out.setncattr(k,msftyyz.__dict__[k])
    
    for k in msftyzsmpa.__dict__.keys():
      if k[0] != '_': msftyzsmpa_out.setncattr(k,msftyzsmpa.__dict__[k])
    
    for k in msftyzmpa.__dict__.keys():
      if k[0] != '_': msftyzmpa_out.setncattr(k,msftyzmpa.__dict__[k])
    
    average_T1_out.setncatts(average_T1.__dict__)
    average_T2_out.setncatts(average_T2.__dict__)
    average_DT_out.setncatts(average_DT.__dict__)
    time_bnds_out.setncatts(time_bnds.__dict__)
   
    time_out[:] = np.array(tax[:])
    yh_out[:] = np.array(yh[:])
    z_l_out[:] = np.array(z_l[:])
    z_i_out[:] = np.array(z_i[:])
    nv_out[:] = np.array(nv[:])
   
    msftyyz_out[:] = np.ma.array(msftyyz[:])
    msftyzsmpa_out[:] = np.ma.array(msftyzsmpa[:])
    msftyzmpa_out[:] = np.ma.array(msftyzmpa[:])
 
    average_T1_out[:] = average_T1[:]
    average_T2_out[:] = average_T2[:]
    average_DT_out[:] = average_DT[:]
    time_bnds_out[:]  = time_bnds[:]
    
    region_out[:] = nc.stringtochar(region)
    
    f_out.close()
    
    exit(0)

if __name__ == '__main__':
  run()
