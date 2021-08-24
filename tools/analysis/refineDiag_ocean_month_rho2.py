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
##
##   Variables we intend to provide in rho-coordinates:
##   (potenital density referenced to 2000 m)
##
##     msftyrho    -> vmo
##     msftyrhompa -> vhGM           * applies only to 0.5 resolution
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

    _, nl = nc.stringtochar(region).shape

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
    rho2_l = f_in.variables['rho2_l']
    rho2_i = f_in.variables['rho2_i']
    tax = f_in.variables['time']

    if (len(yq) == 1+atlantic_arctic_mask.shape[0]): #symmetric case
       atlantic_arctic_mask=np.append(atlantic_arctic_mask,np.zeros((1,atlantic_arctic_mask.shape[1])),axis=0)
       indo_pacific_mask=np.append(indo_pacific_mask,np.zeros((1,indo_pacific_mask.shape[1])),axis=0)
    #-- msftyrho
    if 'vmo' in list(f_in.variables.keys()):
      varname = 'vmo'
      msftyrho = np.ma.ones((len(tax),3,len(rho2_i),len(yq)))*0.
      msftyrho[:,0,:,:] = m6toolbox.moc_maskedarray(f_in.variables[varname][:],mask=atlantic_arctic_mask)
      msftyrho[:,1,:,:] = m6toolbox.moc_maskedarray(f_in.variables[varname][:],mask=indo_pacific_mask)
      msftyrho[:,2,:,:] = m6toolbox.moc_maskedarray(f_in.variables[varname][:])
      msftyrho[msftyrho.mask] = 1.e20
      msftyrho = np.ma.array(msftyrho,fill_value=1.e20)
      msftyrho.long_name = 'Ocean Y Overturning Mass Streamfunction'
      msftyrho.units = 'kg s-1'
      msftyrho.coordinates = 'region'
      msftyrho.cell_methods = 'rho2_i:point yq:point time:mean'
      msftyrho.time_avg_info = 'average_T1,average_T2,average_DT'
      msftyrho.standard_name = 'ocean_y_overturning_mass_streamfunction'
      do_msftyrho = True
    else:
      do_msftyrho = False

    #-- msftyrhompa
    if 'vhGM' in list(f_in.variables.keys()):
      varname = 'vhGM'
      msftyrhompa = np.ma.ones((len(tax),3,len(rho2_i),len(yq)))*0.
      msftyrhompa[:,0,:,:] = m6toolbox.moc_maskedarray(f_in.variables[varname][:],mask=atlantic_arctic_mask)
      msftyrhompa[:,1,:,:] = m6toolbox.moc_maskedarray(f_in.variables[varname][:],mask=indo_pacific_mask)
      msftyrhompa[:,2,:,:] = m6toolbox.moc_maskedarray(f_in.variables[varname][:])
      msftyrhompa[msftyrhompa.mask] = 1.e20
      msftyrhompa = np.ma.array(msftyrhompa,fill_value=1.e20)
      msftyrhompa.long_name = 'ocean Y overturning mass streamfunction due to parameterized mesoscale advection'
      msftyrhompa.units = 'kg s-1'
      msftyrhompa.coordinates = 'region'
      msftyrhompa.cell_methods = 'rho2_i:point yq:point time:mean'
      msftyrhompa.time_avg_info = 'average_T1,average_T2,average_DT'
      msftyrhompa.standard_name = 'ocean_y_overturning_mass_streamfunction_due_to_parameterized_'+\
                                  'mesoscale_advection'
      do_msftyrhompa = True
    else:
      do_msftyrhompa = False

    #-- Read time bounds
    nv = f_in.variables['nv']
    average_T1 = f_in.variables['average_T1']
    average_T2 = f_in.variables['average_T2']
    average_DT = f_in.variables['average_DT']
    time_bnds  = f_in.variables['time_bnds']

    if any([do_msftyrho,do_msftyrhompa]):
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
      ncattrs = f_in.__dict__
      ncattrs.pop('associated_files', '')  # not needed for these fields
      f_out.setncatts(ncattrs)
      f_out.filename = os.path.basename(args.outfile)

      time_dim = f_out.createDimension('time', size=None)
      basin_dim = f_out.createDimension('basin', size=3)
      strlen_dim = f_out.createDimension('strlen', size=nl)
      yq_dim  = f_out.createDimension('yq',  size=len(yq[:]))
      rho2_l_dim = f_out.createDimension('rho2_l', size=len(rho2_l[:]))
      rho2_i_dim = f_out.createDimension('rho2_i', size=len(rho2_i[:]))
      nv_dim  = f_out.createDimension('nv',  size=len(nv[:]))

      time_out = f_out.createVariable('time', np.float64, ('time'))
      yq_out   = f_out.createVariable('yq',   np.float64, ('yq'))
      region_out = f_out.createVariable('region', 'c', ('basin', 'strlen'))
      rho2_l_out  = f_out.createVariable('rho2_l',  np.float64, ('rho2_l'))
      rho2_i_out  = f_out.createVariable('rho2_i',  np.float64, ('rho2_i'))
      nv_out  = f_out.createVariable('nv',  np.float64, ('nv'))

      if do_msftyrho:
        msftyrho_out = f_out.createVariable('msftyrho', np.float32, ('time', 'basin', 'rho2_i', 'yq'), fill_value=1.e20)
        msftyrho_out.missing_value = 1.e20
        for k in list(msftyrho.__dict__.keys()):
          if k[0] != '_': msftyrho_out.setncattr(k,msftyrho.__dict__[k])

      if do_msftyrhompa:
        msftyrhompa_out = f_out.createVariable('msftyrhompa', np.float32, ('time', 'basin', 'rho2_i', 'yq'), fill_value=1.e20)
        msftyrhompa_out.missing_value = 1.e20
        for k in list(msftyrhompa.__dict__.keys()):
          if k[0] != '_': msftyrhompa_out.setncattr(k,msftyrhompa.__dict__[k])

      region_out.setncattr('standard_name','region')

      average_T1_out = f_out.createVariable('average_T1', np.float64, ('time'))
      average_T2_out = f_out.createVariable('average_T2', np.float64, ('time'))
      average_DT_out = f_out.createVariable('average_DT', np.float64, ('time'))
      time_bnds_out  = f_out.createVariable('time_bnds',  np.float64, ('time', 'nv'))

      time_out.setncatts(tax.__dict__)
      yq_out.setncatts(yq.__dict__)
      rho2_l_out.setncatts(rho2_l.__dict__)
      rho2_i_out.setncatts(rho2_i.__dict__)
      nv_out.setncatts(nv.__dict__)

      average_T1_out.setncatts(average_T1.__dict__)
      average_T2_out.setncatts(average_T2.__dict__)
      average_DT_out.setncatts(average_DT.__dict__)
      time_bnds_out.setncatts(time_bnds.__dict__)

      time_out[:] = np.array(tax[:])
      yq_out[:] = np.array(yq[:])
      rho2_l_out[:] = np.array(rho2_l[:])
      rho2_i_out[:] = np.array(rho2_i[:])
      nv_out[:] = np.array(nv[:])

      if do_msftyrho:    msftyrho_out[:] = np.ma.array(msftyrho[:])
      if do_msftyrhompa: msftyrhompa_out[:] = np.ma.array(msftyrhompa[:])

      average_T1_out[:] = average_T1[:]
      average_T2_out[:] = average_T2[:]
      average_DT_out[:] = average_DT[:]
      time_bnds_out[:]  = time_bnds[:]

      region_out[:] = nc.stringtochar(region)

      f_out.close()
      exit(0)

    else:
      print('RefineDiag for ocean_month_rho2 yielded no output.')
      exit(1)

if __name__ == '__main__':
  run()
