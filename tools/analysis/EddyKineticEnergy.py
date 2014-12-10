#!/usr/bin/env python

import netCDF4
import numpy
import m6plot
import math

try: import argparse
except: raise Exception('This version of python is not new enough. python 2.7 or newer is required.')

parser = argparse.ArgumentParser(description='''Script for plotting annual-average eddy kinetic energy.''')
parser.add_argument('annual_file', type=str, help='''Daily file containing ssu,ssv.''')
parser.add_argument('-l','--label', type=str, default='', help='''Label to add to the plot.''')
parser.add_argument('-o','--outdir', type=str, default='.', help='''Directory in which to place plots.''')
parser.add_argument('-g','--gridspec', type=str,
  help='''File containing variables geolon,geolat,wet,area_t. Usually the ocean_static.nc from diag_table.''')
cmdLineArgs = parser.parse_args()

rootGroup = netCDF4.Dataset( cmdLineArgs.annual_file )
if 'ssu' not in rootGroup.variables: raise Exception('Could not find "ssu" in file "%s"'%(cmdLineArgs.annual_file))
if 'ssv' not in rootGroup.variables: raise Exception('Could not find "ssv" in file "%s"'%(cmdLineArgs.annual_file))

x = netCDF4.Dataset(cmdLineArgs.gridspec).variables['geolon'][:,:]
y = netCDF4.Dataset(cmdLineArgs.gridspec).variables['geolat'][:,:]
msk = netCDF4.Dataset(cmdLineArgs.gridspec).variables['wet'][:,:]
area = msk*netCDF4.Dataset(cmdLineArgs.gridspec).variables['area_t'][:,:]

#[t,z,y,x] corresponds to axis [0,1,2,3] which can be indexed by [-4,-3,-2,-1]

ssu = rootGroup.variables['ssu']

ssu_mean = ssu[:].mean(axis=0)
eke_u = (0.5*(ssu-ssu_mean)**2).mean(axis=0)
eke = (eke_u + numpy.roll(eke_u,1,axis=-1))/2 # U-point to T-point transform

ssv = rootGroup.variables['ssv']
ssv_mean = ssv[:].mean(axis=0)
eke_v = (0.5*(ssv-ssv_mean)**2).mean(axis=0)
eke = eke + (eke_v + numpy.roll(eke_v,1,axis=-2))/2 

#factor of 10000 to convert to (cm/s)^2
eke = 10000*eke

#clip the extreme small values that cause log to blow up
eke = eke.clip(min=1.0e-8)

#Plot with logscale=True
#ci=m6plot.pmCI(0.0,10.0,0.1)
#plot_title = 'Eddy Kinetic Energy annual mean [(cm/s)^2]'

#The logscale=True of matplotlib.pyplot does not work!
#So, pass the log to be plotted instead
eke = numpy.log(eke)
plot_title = 'Log of Eddy Kinetic Energy annual mean [(cm/s)^2]'

m6plot.xyplot( eke, x, y, area=area,
      suptitle=rootGroup.title+' '+cmdLineArgs.label, title=plot_title,
#      clim=ci, logscale=True,
      save=cmdLineArgs.outdir+'/EKE_mean.png')

