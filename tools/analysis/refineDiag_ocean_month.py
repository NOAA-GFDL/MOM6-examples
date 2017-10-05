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
##   2-D variables we intend to provide:
##
##     hfy  ->  T_ady_2d + ndiff_tracer_trans_y_2d_T   * T_ady_2d needs to be converted to Watts (Cp = 3992.)
##                                                       ndiff_tracer_trans_y_2d_T already in Watts
##                                                       advective term in both 0.25 and 0.5 resolutions
##                                                       diffusive term only in 0.5 resolution
##
##     hfx  -> same recipie as above, expect for x-dimension
##     hfbasin -> summed line of hfy in each basin 
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

def heat_trans_by_basin(x,mask=None,lat=None,minlat=None):
    if mask is not None:
        varmask = np.sum(mask,axis=-1)
        varmask = np.expand_dims(varmask,0)
        varmask = np.where(np.equal(varmask,0.),True,False)
    else:
        mask = 1.
        varmask = False
    result = np.ma.sum((x*mask),axis=-1)
    result.mask = varmask
    if (minlat is not None) and (lat is not None):
        if len(lat.shape) == 1:
            lat = np.tile(lat,0)
            lat = np.tile(lat,(len(x),1))
        result = np.ma.masked_where(np.less(lat,minlat),result)
    return result

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
    yq  = f_in.variables['yq']
    xh = f_in.variables['xh']
    tax = f_in.variables['time']
    
    #-- hfy
    advective = f_in.variables['T_ady_2d'][:]
    if 'ndiff_tracer_trans_y_2d_T' in f_in.variables.keys():
      diffusive = f_in.variables['ndiff_tracer_trans_y_2d_T'][:]
    else:
      print("Warning: diffusive term 'ndiff_tracer_trans_y_2d_T' not found. Check if this experiment is running with neutral diffusion.")
      diffusive = advective * 0.
    hfy = advective + diffusive
    hfy.long_name = 'Ocean Heat Y Transport'
    hfy.units = 'W'
    hfy.cell_methods = 'yq:point xh:mean time:mean'
    hfy.time_avg_info = 'average_T1,average_T2,average_DT'
    hfy.standard_name = 'ocean_heat_y_transport'

    #-- hfx
    advective = f_in.variables['T_adx_2d'][:]
    if 'ndiff_tracer_trans_x_2d_T' in f_in.variables.keys():
      diffusive = f_in.variables['ndiff_tracer_trans_x_2d_T'][:]
    else:
      print("Warning: diffusive term 'ndiff_tracer_trans_x_2d_T' not found. Check if this experiment is running with neutral diffusion.")
      diffusive = advective * 0.
    hfx = advective + diffusive
    hfx.long_name = 'Ocean Heat X Transport'
    hfx.units = 'W'
    hfx.cell_methods = 'yh:mean xq:point time:mean'
    hfx.time_avg_info = 'average_T1,average_T2,average_DT'
    hfx.standard_name = 'ocean_heat_x_transport'

    #-- hfbasin 
    hfbasin = np.ma.ones((len(tax),3,len(yq)))*0.
    hfbasin[:,0,:] = heat_trans_by_basin(hfy,mask=atlantic_arctic_mask)
    hfbasin[:,1,:] = heat_trans_by_basin(hfy,mask=indo_pacific_mask,minlat=-34,lat=yq)
    hfbasin[:,2,:] = heat_trans_by_basin(hfy)
    hfbasin[hfbasin.mask] = nc_misval
    hfbasin = np.ma.array(hfbasin,fill_value=nc_misval)
    hfbasin.long_name = 'Northward Ocean Heat Transport'
    hfbasin.units = 'W'
    hfbasin.coordinates = 'region'
    hfbasin.cell_methods = 'yq:point time:mean'
    hfbasin.comment = 'Indo-Pacific heat transport begins at 34 S'
    hfbasin.time_avg_info = 'average_T1,average_T2,average_DT'
    hfbasin.standard_name = 'northward_ocean_heat_transport'

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
    f_out.filename = os.path.basename(args.outfile)
    f_out.delncattr('associated_files')  # not needed for these fields     

    time_dim = f_out.createDimension('time', size=None)
    basin_dim = f_out.createDimension('basin', size=3)
    strlen_dim = f_out.createDimension('strlen', size=21)
    yq_dim  = f_out.createDimension('yq',  size=len(yq[:]))
    xh_dim = f_out.createDimension('xh', size=len(xh[:]))
    nv_dim  = f_out.createDimension('nv',  size=len(nv[:]))
    
    time_out = f_out.createVariable('time', np.float64, ('time'))
    yq_out   = f_out.createVariable('yq',   np.float64, ('yq'))
    region_out = f_out.createVariable('region', 'c', ('basin', 'strlen'))
    xh_out  = f_out.createVariable('xh',  np.float64, ('xh'))
    nv_out  = f_out.createVariable('nv',  np.float64, ('nv'))
   
    hfy_out = f_out.createVariable('hfy', np.float32, ('time', 'yq', 'xh'), fill_value=1.e20)
    hfy_out.missing_value = 1.e20
 
    hfx_out = f_out.createVariable('hfx', np.float32, ('time', 'yq', 'xh'), fill_value=1.e20)
    hfx_out.missing_value = 1.e20
 
    hfbasin_out = f_out.createVariable('hfbasin', np.float32, ('time', 'basin', 'yq'), fill_value=1.e20)
    hfbasin_out.missing_value = 1.e20
 
    average_T1_out = f_out.createVariable('average_T1', np.float64, ('time'))
    average_T2_out = f_out.createVariable('average_T2', np.float64, ('time'))
    average_DT_out = f_out.createVariable('average_DT', np.float64, ('time'))
    time_bnds_out  = f_out.createVariable('time_bnds',  np.float64, ('time', 'nv'))
    
    time_out.setncatts(tax.__dict__)
    yq_out.setncatts(yq.__dict__)
    xh_out.setncatts(xh.__dict__)
    nv_out.setncatts(nv.__dict__)

    for k in hfy.__dict__.keys():
      if k[0] != '_': hfy_out.setncattr(k,hfy.__dict__[k])
    
    for k in hfx.__dict__.keys():
      if k[0] != '_': hfx_out.setncattr(k,hfx.__dict__[k])

    for k in hfbasin.__dict__.keys():
      if k[0] != '_': hfbasin_out.setncattr(k,hfbasin.__dict__[k])

    region_out.setncattr('standard_name','region')

    average_T1_out.setncatts(average_T1.__dict__)
    average_T2_out.setncatts(average_T2.__dict__)
    average_DT_out.setncatts(average_DT.__dict__)
    time_bnds_out.setncatts(time_bnds.__dict__)
   
    time_out[:] = np.array(tax[:])
    yq_out[:] = np.array(yq[:])
    xh_out[:] = np.array(xh[:])
    nv_out[:] = np.array(nv[:])
   
    hfy_out[:] = np.ma.array(hfy[:])
    hfx_out[:] = np.ma.array(hfx[:])
    hfbasin_out[:] = np.ma.array(hfbasin[:])
 
    average_T1_out[:] = average_T1[:]
    average_T2_out[:] = average_T2[:]
    average_DT_out[:] = average_DT[:]
    time_bnds_out[:]  = time_bnds[:]
    
    region_out[:] = nc.stringtochar(region)
    
    f_out.close()
    
    exit(0)

if __name__ == '__main__':
  run()
