#!/usr/bin/env python

import io
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
  parser.add_argument('infile', type=str, help='''Directory containing annual time series thetao and so xyave files''')
  parser.add_argument('-l','--label', type=str, default='', help='''Label to add to the plot.''')
  parser.add_argument('-s','--suptitle', type=str, default='', help='''Super-title for experiment.  Default is to read from netCDF file.''')
  parser.add_argument('-o','--outdir', type=str, default='.', help='''Directory in which to place plots.''')
  parser.add_argument('-t','--trange', type=str, default=None, help='''Tuple containing start and end years to plot''')
  cmdLineArgs = parser.parse_args()
  main(cmdLineArgs)

def main(cmdLineArgs,stream=False):
  if not isinstance(cmdLineArgs.infile,list):
    cmdLineArgs.infile = [cmdLineArgs.infile]
  rootGroupT = [x+'.thetao_xyave.nc' for x in cmdLineArgs.infile]  
  rootGroupS = [x+'.so_xyave.nc' for x in cmdLineArgs.infile]  
  rootGroupT = netCDF4.MFDataset( rootGroupT )
  rootGroupS = netCDF4.MFDataset( rootGroupS )
  if 'thetao_xyave' not in rootGroupT.variables: raise Exception('Could not find "thetao_xyave" files "%s"'%(cmdLineArgs.infile))
  if 'so_xyave' not in rootGroupS.variables: raise Exception('Could not find "so_xyave" files "%s"'%(cmdLineArgs.infile))

  if 'zt' in rootGroupT.variables.keys():
    zt = rootGroupT.variables['zt'][:] * -1
  elif 'z_l' in rootGroupT.variables.keys():
    zt = rootGroupT.variables['z_l'][:] * -1
  timeT = rootGroupT.variables['time']
  timeS = rootGroupS.variables['time']
  timeT = numpy.array([int(x.year) for x in netCDF4.num2date(timeT[:],timeT.units,calendar=timeT.calendar)])
  timeS = numpy.array([int(x.year) for x in netCDF4.num2date(timeS[:],timeS.units,calendar=timeS.calendar)])

  variable = rootGroupT.variables['thetao_xyave']
  T = variable[:]
  T = T-T[0]

  variable = rootGroupS.variables['so_xyave']
  S = variable[:]
  S = S-S[0]

  if cmdLineArgs.suptitle != '':  suptitle = cmdLineArgs.suptitle + ' ' + cmdLineArgs.label
  else: suptitle = rootGroupT.title + ' ' + cmdLineArgs.label

  imgbufs = []

  if stream is True: objOut = io.BytesIO()
  else: objOut = cmdLineArgs.outdir+'/T_drift.png'
  m6plot.ztplot( T, timeT, zt, splitscale=[0., -2000., -6500.],
      suptitle=suptitle, title='Potential Temperature [C]',
      extend='both', colormap='dunnePM', autocenter=True,
      save=objOut)
  if stream is True: imgbufs.append(objOut)

  if stream is True: objOut = io.BytesIO()
  else: objOut = cmdLineArgs.outdir+'/S_drift.png'
  m6plot.ztplot( S, timeS, zt, splitscale=[0., -2000., -6500.],
      suptitle=suptitle, title='Salinity [psu]',
      extend='both', colormap='dunnePM', autocenter=True,
      save=objOut)
  if stream is True: imgbufs.append(objOut)

  if stream is True:
    return imgbufs

if __name__ == '__main__':
  run()

