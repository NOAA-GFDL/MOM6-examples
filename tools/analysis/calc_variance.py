#!/usr/bin/env python

import netCDF4
import numpy
import os

try: import argparse
except: raise Exception('This version of python is not new enough. python 2.7 or newer is required.')

parser = argparse.ArgumentParser(description='''Script for generating monthly-averages of square from a year-long file of daily data.''')
parser.add_argument('variable', type=str, help='''Variable to process.''')
parser.add_argument('daily_file', type=str, help='''Daily data file.''')
parser.add_argument('annual_file', type=str, help='''Annual file to create.''')
parser.add_argument('-v','--verbose', action='store_true', help='''Inidicate progress.''')
args = parser.parse_args()

if args.verbose: print 'Opening',args.daily_file
nc_in = netCDF4.Dataset( args.daily_file )
if args.variable not in nc_in.variables: raise Exception('Could not find %s in file "%s"'%(args.variable,args.daily_file))
variable = nc_in.variables[args.variable]
if len(variable.shape)<=2: raise Exception('Expecting a 2D+time or 3D+time array.')
shape = variable.shape
nt = shape[0];
nxy = shape[1:]

if args.verbose: print 'Creating',args.annual_file
if os.path.exists(args.annual_file):
    mode = 'r+'
    append = True
else:
    mode = 'w'
    append = False
nc_out = netCDF4.Dataset( args.annual_file, mode, format='NETCDF3_CLASSIC' )

if append is True:
  if 'time' in nc_out.variables.keys():
    time_var = 'time'
  elif 'Time' in nc_out.variables.keys():
    time_var = 'Time'
  else:
    nc_out.close()
    raise ValueError('Time dimension could not be found in existing file.')
  if len(nc_out.variables[time_var][:]) <= 1:
    nc_out.close()
    raise ValueError('Existing file has only one time value. Assuming this is annual output.  Aborting.')

if nt==365: days_in_month =   [31,28,31,30,31,30,31,31,30,31,30,31]
elif nt==366: days_in_month = [31,29,31,30,31,30,31,31,30,31,30,31]
elif nt==73 : days_in_month = [6,6,6,6,6,6,6,7,6,6,6,6] # for ocean_5daily.nc
else: raise Exception('First dimension appears to not match a days in a single year.')

# Create dimensions
for d in variable.dimensions:
  if d not in nc_out.dimensions:
    if nc_in.dimensions[d].isunlimited(): nc_out.createDimension(d, None)
    else: nc_out.createDimension(d, len(nc_in.dimensions[d]))

# Copy global attributes
if append is False:
  for a in nc_in.ncattrs():
    if a not in nc_out.dimensions:
      nc_out.__setattr__(a ,nc_in.__getattr__(a))

# Copy variables corresponding to dimensions used by variable
copy_vars = list(variable.dimensions)
if 'time_avg_info' in variable.ncattrs():
  time_bounds_vars = variable.__getattr__('time_avg_info').split(',')
else: time_bounds_vars = []
for v in copy_vars+time_bounds_vars:
  if v in nc_in.variables:
    if v not in nc_out.variables:
      hv = nc_out.createVariable(v, nc_in.variables[v].dtype, nc_in.variables[v].dimensions)
      for a in nc_in.variables[v].ncattrs():
        hv.setncattr(a, nc_in.variables[v].__getattr__(a))
      if v in variable.dimensions:
        if not nc_in.dimensions[v].isunlimited():
          hv[:] = nc_in.variables[v][:]
          print(str(v))
    if v in variable.dimensions:
      if nc_in.dimensions[v].isunlimited():
        intime = nc_in.variables[v]
        time = intime[:]  # Keep around for later

# Create new variables
if args.variable not in nc_out.variables:
  new_mean = nc_out.createVariable(args.variable, variable.dtype, variable.dimensions)
  do_mean = True
else:
  do_mean = False

if args.variable+'_squared' not in nc_out.variables:
  new_squared = nc_out.createVariable(args.variable+'_squared', variable.dtype, variable.dimensions)
  do_squared = True
else:
  do_squared = False

if args.variable+'_var' not in nc_out.variables:
  new_variance = nc_out.createVariable(args.variable+'_var', variable.dtype, variable.dimensions)
  do_variance = True
else:
  do_variance = False


for a in variable.ncattrs():
  if do_mean:  new_mean.setncattr(a, variable.__getattr__(a))
  if a == 'long_name':
    if do_squared:  new_squared.setncattr(a, 'Square of '+variable.__getattr__(a))
    if do_variance:  new_variance.setncattr(a, 'Variance of '+variable.__getattr__(a))
  elif a == 'units':
    if do_squared:  new_squared.setncattr(a, '('+variable.__getattr__(a)+')^2')
    if do_variance:  new_variance.setncattr(a, '('+variable.__getattr__(a)+')^2')
  else:
    if do_squared:  new_squared.setncattr(a, variable.__getattr__(a))
    if do_variance:  new_variance.setncattr(a, variable.__getattr__(a))

numpy.seterr(divide='ignore', invalid='ignore', over='ignore') # To avoid warnings
record = -1
if len(time_bounds_vars): b1 = nc_in.variables[time_bounds_vars[0]][0]
for month,days in enumerate(days_in_month):
  if args.verbose: print 'Reading daily data for month',month+1
  mean_val = numpy.ma.zeros(nxy)
  squared_val = numpy.ma.zeros(nxy)
  time_val = 0.
  count = 0.
  dt = 0.
  b0 = b1 # Assumes the time bounds are space-filling
  for day in range(days):
    record += 1
    daily_vals = variable[record,:]
    mean_val += daily_vals
    squared_val += daily_vals**2
    time_val += intime[record]
    if len(time_bounds_vars):
      b1 = nc_in.variables[time_bounds_vars[1]][record]
      dt = nc_in.variables[time_bounds_vars[2]][record]
      count += dt
    else:
      count += 1.
  mean_val = mean_val/count
  squared_val = squared_val/count
  if do_mean:  new_mean[month,:] = mean_val
  if do_squared:  new_squared[month,:] = squared_val
  if do_variance:  new_variance[month,:] = squared_val - mean_val**2
  if append is False:
    time[month] = time_val/count
    if len(time_bounds_vars):
      nc_out.variables[time_bounds_vars[0]][month] = b0
      nc_out.variables[time_bounds_vars[1]][month] = b1
      nc_out.variables[time_bounds_vars[2]][month] = count

nc_out.close()
nc_in.close()
if args.verbose: print args.annual_file,'written.'
