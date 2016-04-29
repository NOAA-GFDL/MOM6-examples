#!/usr/bin/env python

import netCDF4
import numpy
import m6plot
import m6toolbox
import matplotlib.pyplot as plt
import os

try: import argparse
except: raise Exception('This version of python is not new enough. python 2.7 or newer is required.')

def run():
  parser = argparse.ArgumentParser(description='''Script for plotting depth vs. time plots of temperature and salinity drift''')
  parser.add_argument('annual_directory', type=str, help='''Directory containing annual time series thetao and so xyave files''')
  parser.add_argument('-l','--label', type=str, default='', help='''Label to add to the plot.''')
  parser.add_argument('-s','--suptitle', type=str, default='', help='''Super-title for experiment.  Default is to read from netCDF file.''')
  parser.add_argument('-o','--outdir', type=str, default='.', help='''Directory in which to place plots.''')
  parser.add_argument('-t','--trange', type=str, default=None, help='''Tuple containing start and end years to plot''')
  cmdLineArgs = parser.parse_args()
  main(cmdLineArgs)

def main(cmdLineArgs,stream=None):
  rootGroupT = netCDF4.MFDataset( cmdLineArgs.annual_directory + '/*.thetao_xyave.nc' )
  rootGroupS = netCDF4.MFDataset( cmdLineArgs.annual_directory + '/*.so_xyave.nc' )
  if 'thetao_xyave' not in rootGroupT.variables: raise Exception('Could not find "thetao_xyave" files "%s"'%(cmdLineArgs.annual_directory))
  if 'so_xyave' not in rootGroupS.variables: raise Exception('Could not find "so_xyave" files "%s"'%(cmdLineArgs.annual_directory))

  zt = rootGroupT.variables['zt'][::-1] * -1
  timeT = rootGroupT.variables['time']
  timeS = rootGroupS.variables['time']
  timeT = numpy.array([int(x.year) for x in netCDF4.num2date(timeT[:],timeT.units,calendar=timeT.calendar)])
  timeS = numpy.array([int(x.year) for x in netCDF4.num2date(timeS[:],timeS.units,calendar=timeS.calendar)])

  if cmdLineArgs.trange != None:
    start = list(timeT).index(cmdLineArgs.trange[0])
    end = list(timeT).index(cmdLineArgs.trange[1])
  else:
    start = 0
    end = -1

  variable = rootGroupT.variables['thetao_xyave']
  T = variable[start:end] - variable[start]
  T = T[:,::-1]
  timeT = timeT[start:end]

  variable = rootGroupS.variables['so_xyave']
  S = variable[start:end] - variable[start]
  S = S[:,::-1]
  timeS = timeS[start:end]

  if cmdLineArgs.suptitle != '':  suptitle = cmdLineArgs.suptitle + ' ' + cmdLineArgs.label
  else: suptitle = rootGroupT.title + ' ' + cmdLineArgs.label

  if stream != None: objOut = stream[0]
  else: objOut = cmdLineArgs.outdir+'/T_drift.png'
  m6plot.ztplot( T, timeT, zt, splitscale=[0., -1000., -6500.],
      suptitle=suptitle, title='Potential Temperature [C]',
      extend='both', colormap='dunnePM', autocenter=True,
      save=objOut)

  if stream != None: objOut = stream[1]
  else: objOut = cmdLineArgs.outdir+'/S_drift.png'
  m6plot.ztplot( S, timeS, zt, splitscale=[0., -1000., -6500.],
      suptitle=suptitle, title='Salinity [psu]',
      extend='both', colormap='dunnePM', autocenter=True,
      save=objOut)

if __name__ == '__main__':
  run()

