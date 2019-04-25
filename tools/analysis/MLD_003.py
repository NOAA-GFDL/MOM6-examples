#!/usr/bin/env python

import io
import netCDF4
import numpy
import m6plot
import m6toolbox
import matplotlib.pyplot as plt
import os

def run():
  try: import argparse
  except: raise Exception('This version of python is not new enough. python 2.7 or newer is required.')
  parser = argparse.ArgumentParser(description='''Script for plotting annual-min/max mixed layer depth.''')
  parser.add_argument('infile', type=str, help='''Monthly-averaged file containing at least 12 months of MLD_003.''')
  parser.add_argument('-l','--label', type=str, default='', help='''Label to add to the plot.''')
  parser.add_argument('-o','--outdir', type=str, default='.', help='''Directory in which to place plots.''')
  parser.add_argument('-od','--obsdata', type=str, default='',help='''File containing the observational MLD data (Hosoda et al., 2010).''')
  parser.add_argument('-g','--gridspec', type=str, required=True,
    help='''Directory containing mosaic/grid-spec files (ocean_hgrid.nc and ocean_mask.nc).''')
  cmdLineArgs = parser.parse_args()
  main(cmdLineArgs)

def main(cmdLineArgs,stream=False):
  rootGroup = netCDF4.MFDataset( cmdLineArgs.infile )
  if 'MLD_003' not in rootGroup.variables: raise Exception('Could not find "MLD_003" in file "%s"'%(cmdLineArgs.infile))
  
  if not os.path.exists(cmdLineArgs.gridspec): raise ValueError('Specified gridspec directory/tar file does not exist.')
  if os.path.isdir(cmdLineArgs.gridspec):
    x = netCDF4.Dataset(cmdLineArgs.gridspec+'/ocean_hgrid.nc').variables['x'][::2,::2]
    y = netCDF4.Dataset(cmdLineArgs.gridspec+'/ocean_hgrid.nc').variables['y'][::2,::2]
    msk = netCDF4.Dataset(cmdLineArgs.gridspec+'/ocean_mask.nc').variables['mask'][:]
    area = msk*netCDF4.Dataset(cmdLineArgs.gridspec+'/ocean_hgrid.nc').variables['area'][:,:].reshape([msk.shape[0], 2, msk.shape[1], 2]).sum(axis=-3).sum(axis=-1)
  elif os.path.isfile(cmdLineArgs.gridspec):
    x = m6toolbox.readNCFromTar(cmdLineArgs.gridspec,'ocean_hgrid.nc','x')[::2,::2]
    y = m6toolbox.readNCFromTar(cmdLineArgs.gridspec,'ocean_hgrid.nc','y')[::2,::2]
    msk = m6toolbox.readNCFromTar(cmdLineArgs.gridspec,'ocean_mask.nc','mask')[:]
    area = msk*m6toolbox.readNCFromTar(cmdLineArgs.gridspec,'ocean_hgrid.nc','area')[:,:].reshape([msk.shape[0], 2, msk.shape[1], 2]).sum(axis=-3).sum(axis=-1)
  else:
    raise ValueError('Unable to extract grid information from gridspec directory/tar file.') 
  
  variable = rootGroup.variables['MLD_003']
  shape = variable.shape
  MLD = variable[:].reshape(int(shape[0]/12),12,shape[1],shape[2]).mean(axis=0)
  
  if not hasattr(cmdLineArgs,'obsdata') or cmdLineArgs.obsdata == '':
    cmdLineArgs.obsdata = '/archive/gold/datasets/obs/Hosada2010_MLD_climatology.v20140515.nc'

  MLD_obs = netCDF4.Dataset(cmdLineArgs.obsdata).variables['MLD'][:]
  x_obs = netCDF4.Dataset(cmdLineArgs.obsdata).variables['LONGITUDE'][:]
  y_obs = netCDF4.Dataset(cmdLineArgs.obsdata).variables['LATITUDE'][:]
  
  ciMin = m6plot.linCI(0,95,5)
  ciMax = m6plot.linCI(0,680,20)
  
  imgbufs = []
  
  # Plot of shallowest model MLD (summer)
  m6plot.xyplot( MLD.min(axis=0), x, y, area=area,
        suptitle=rootGroup.title+' '+cmdLineArgs.label, title='Annual-minimum MLD$_{0.03}$ [m]',
        clim=ciMin, extend='max', colormap='dunneRainbow',
        save=cmdLineArgs.outdir+'/MLD_003_minimum.png')
  
  # 2-panel plot of shallowest model MLD + obs (summer)
  if stream is True: img = io.BytesIO()
  else: img = cmdLineArgs.outdir+'/MLD_003_minimum.2_panel.png'
  m6plot.setFigureSize(aspect=[3,3], verticalresolution=976, npanels=0)
  ax1 = plt.subplot(2,1,1)
  m6plot.xyplot( numpy.roll(MLD_obs.min(axis=0),300,axis=-1), x_obs-300, y_obs,
        suptitle=rootGroup.title+' '+cmdLineArgs.label, title='Hosoda et al., 2010, annual-minimum MLD$_{0.03}$ [m]',
        clim=ciMin, extend='max', colormap='dunneRainbow',
        axis=ax1)
  ax2 = plt.subplot(2,1,2)
  m6plot.xyplot( MLD.min(axis=0), x, y, area=area,
        suptitle=rootGroup.title+' '+cmdLineArgs.label, title='Annual-minimum MLD$_{0.03}$ [m]',
        clim=ciMin, extend='max', colormap='dunneRainbow',
        axis=ax2,
        save=img)
  if stream is True: imgbufs.append(img)
  
  # Plot of deepest model MLD (winter)
  m6plot.xyplot( MLD.max(axis=0), x, y, area=area,
        suptitle=rootGroup.title+' '+cmdLineArgs.label, title='Annual-maximum MLD$_{0.03}$ [m]',
        clim=ciMax, extend='max', colormap='dunneRainbow',
        save=cmdLineArgs.outdir+'/MLD_003_maximum.png')
  
  # 2-panel plot of deepest model MLD + obs (winter)
  if stream is True: img = io.BytesIO()
  else: img = cmdLineArgs.outdir+'/MLD_003_maximum.2_panel.png'
  m6plot.setFigureSize(aspect=[3,3], verticalresolution=976, npanels=0)
  ax1 = plt.subplot(2,1,1)
  m6plot.xyplot( numpy.roll(MLD_obs.max(axis=0),300,axis=-1), x_obs-300, y_obs,
        suptitle=rootGroup.title+' '+cmdLineArgs.label, title='Hosoda et al., 2010, annual-maximum MLD$_{0.03}$ [m]',
        clim=ciMax, extend='max', colormap='dunneRainbow',
        axis=ax1)
  ax2 = plt.subplot(2,1,2)
  m6plot.xyplot( MLD.max(axis=0), x, y, area=area,
        suptitle=rootGroup.title+' '+cmdLineArgs.label, title='Annual-maximum MLD$_{0.03}$ [m]',
        clim=ciMax, extend='max', colormap='dunneRainbow',
        axis=ax2,
        save=img)
  if stream is True: imgbufs.append(img)

  if stream is True:
    return imgbufs

if __name__ == '__main__':
  run()
