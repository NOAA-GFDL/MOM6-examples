#!/usr/bin/env python

import netCDF4
import numpy
import m6plot
import m6toolbox
import matplotlib.pyplot as plt
import os
import sys

def run():
  try: import argparse
  except: raise Exception('This version of python is not new enough. python 2.7 or newer is required.')
  parser = argparse.ArgumentParser(description='''Script for plotting meridional overturning.''')
  parser.add_argument('annual_file', type=str, help='''Annually-averaged file containing 3D 'vh' and 'e'.''')
  parser.add_argument('-l','--label', type=str, default='', help='''Label to add to the plot.''')
  parser.add_argument('-s','--suptitle', type=str, default='', help='''Super-title for experiment.  Default is to read from netCDF file.''')
  parser.add_argument('-o','--outdir', type=str, default='.', help='''Directory in which to place plots.''')
  parser.add_argument('-g','--gridspec', type=str, required=True,
    help='''Directory containing mosaic/grid-spec files (ocean_hgrid.nc and ocean_mask.nc).''')
  cmdLineArgs = parser.parse_args()
  main(cmdLineArgs)

def main(cmdLineArgs,stream=None):
  if not os.path.exists(cmdLineArgs.gridspec): raise ValueError('Specified gridspec directory/tar file does not exist.')
  if os.path.isdir(cmdLineArgs.gridspec):
    x = netCDF4.Dataset(cmdLineArgs.gridspec+'/ocean_hgrid.nc').variables['x'][::2,::2]
    xcenter = netCDF4.Dataset(cmdLineArgs.gridspec+'/ocean_hgrid.nc').variables['x'][1::2,1::2]
    y = netCDF4.Dataset(cmdLineArgs.gridspec+'/ocean_hgrid.nc').variables['y'][::2,::2]
    ycenter = netCDF4.Dataset(cmdLineArgs.gridspec+'/ocean_hgrid.nc').variables['y'][1::2,1::2]
    msk = netCDF4.Dataset(cmdLineArgs.gridspec+'/ocean_mask.nc').variables['mask'][:]
    area = msk*netCDF4.Dataset(cmdLineArgs.gridspec+'/ocean_hgrid.nc').variables['area'][:,:].reshape([msk.shape[0], 2, msk.shape[1], 2]).sum(axis=-3).sum(axis=-1)
    depth = netCDF4.Dataset(cmdLineArgs.gridspec+'/ocean_topog.nc').variables['depth'][:]
    try: basin_code = netCDF4.Dataset(cmdLineArgs.gridspec+'/basin_codes.nc').variables['basin'][:]
    except: basin_code = m6toolbox.genBasinMasks(xcenter, ycenter, depth)
  elif os.path.isfile(cmdLineArgs.gridspec):
    x = m6toolbox.readNCFromTar(cmdLineArgs.gridspec,'ocean_hgrid.nc','x')[::2,::2]
    xcenter = m6toolbox.readNCFromTar(cmdLineArgs.gridspec,'ocean_hgrid.nc','x')[1::2,1::2]
    y = m6toolbox.readNCFromTar(cmdLineArgs.gridspec,'ocean_hgrid.nc','y')[::2,::2]
    ycenter = m6toolbox.readNCFromTar(cmdLineArgs.gridspec,'ocean_hgrid.nc','y')[1::2,1::2]
    msk = m6toolbox.readNCFromTar(cmdLineArgs.gridspec,'ocean_mask.nc','mask')[:]
    area = msk*m6toolbox.readNCFromTar(cmdLineArgs.gridspec,'ocean_hgrid.nc','area')[:,:].reshape([msk.shape[0], 2, msk.shape[1], 2]).sum(axis=-3).sum(axis=-1)
    depth = m6toolbox.readNCFromTar(cmdLineArgs.gridspec,'ocean_topog.nc','depth')[:]
    try: basin_code = m6toolbox.readNCFromTar(cmdLineArgs.gridspec,'basin_codes.nc','basin')[:]
    except: basin_code = m6toolbox.genBasinMasks(xcenter, ycenter, depth)
  else:
    raise ValueError('Unable to extract grid information from gridspec directory/tar file.') 

  if stream != None:
    if len(stream) != 2:
      raise ValueError('If specifying output streams, exactly two streams are needed for this analysis')
  
  rootGroup = netCDF4.MFDataset( cmdLineArgs.annual_file )
  if 'vh' in rootGroup.variables:
    varName = 'vh'; conversion_factor = 1.e-9
  elif 'vmo' in rootGroup.variables:
    varName = 'vmo'; conversion_factor = 1.e-9
  else: raise Exception('Could not find "vh" or "vmo" in file "%s"'%(cmdLineArgs.annual_file))
  if 'zw' not in rootGroup.variables: conversion_factor = 1.e-6
  if len(rootGroup.variables[varName].shape)==4: VHmod = rootGroup.variables[varName][:].mean(axis=0)
  else: VHmod = rootGroup.variables[varName][:]
  try: VHmod = VHmod.filled(0.)
  except: pass
  Zmod = m6toolbox.get_z(rootGroup, depth, varName)
  
  def MOCpsi(vh, vmsk=None):
    """Sums 'vh' zonally and cumulatively in the vertical to yield an overturning stream function, psi(y,z)."""
    shape = list(vh.shape); shape[-3] += 1
    psi = numpy.zeros(shape[:-1])
    if len(shape)==3:
      for k in range(shape[-3]-1,0,-1):
        if vmsk is None: psi[k-1,:] = psi[k,:] - vh[k-1].sum(axis=-1)
        else: psi[k-1,:] = psi[k,:] - (vmsk*vh[k-1]).sum(axis=-1)
    else:
      for n in range(shape[0]):
        for k in range(shape[-3]-1,0,-1):
          if vmsk is None: psi[n,k-1,:] = psi[n,k,:] - vh[n,k-1].sum(axis=-1)
          else: psi[n,k-1,:] = psi[n,k,:] - (vmsk*vh[n,k-1]).sum(axis=-1)
    return psi
  
  def plotPsi(y, z, psi, ci, title):
    cmap = plt.get_cmap('dunnePM')
    plt.contourf(y, z, psi, levels=ci, cmap=cmap, extend='both')
    cbar = plt.colorbar()
    plt.contour(y, z, psi, levels=ci, colors='k', hold='on')
    plt.gca().set_yscale('splitscale',zval=[0,-2000,-6500])
    plt.title(title)
    cbar.set_label('[Sv]'); plt.ylabel('Elevation [m]')

  def findExtrema(y, z, psi, min_lat=-90., max_lat=90., min_depth=0., mult=1.):
    psiMax = mult*numpy.amax( mult * numpy.ma.array(psi)[(y>=min_lat) & (y<=max_lat) & (z<-min_depth)] )
    idx = numpy.argmin(numpy.abs(psi-psiMax))
    (j,i) = numpy.unravel_index(idx, psi.shape)
    plt.plot(y[j,i],z[j,i],'kx',hold=True)
    plt.text(y[j,i],z[j,i],'%.1f'%(psi[j,i]))
  
  m6plot.setFigureSize(npanels=1)
  cmap = plt.get_cmap('dunnePM')

  if cmdLineArgs.suptitle != '':  suptitle = cmdLineArgs.suptitle + ' ' + cmdLineArgs.label
  else: suptitle = rootGroup.title + ' ' + cmdLineArgs.label

  # Global MOC
  z = Zmod.min(axis=-1); psiPlot = MOCpsi(VHmod)*conversion_factor
  yy = y[1:,:].max(axis=-1)+0*z
  ci=m6plot.pmCI(0.,40.,5.)
  plotPsi(yy, z, psiPlot, ci, 'Global MOC [Sv]')
  plt.xlabel(r'Latitude [$\degree$N]')
  plt.suptitle(suptitle)
  findExtrema(yy, z, psiPlot, max_lat=-30.)
  findExtrema(yy, z, psiPlot, min_lat=25.)
  findExtrema(yy, z, psiPlot, min_depth=2000., mult=-1.)
  if stream != None:
    plt.savefig(stream[0])
  else:
    plt.savefig(cmdLineArgs.outdir+'/MOC_global.png')
  
  # Atlantic MOC
  plt.clf()
  m = 0*basin_code; m[(basin_code==2) | (basin_code==4) | (basin_code==6) | (basin_code==7) | (basin_code==8)]=1
  ci=m6plot.pmCI(0.,22.,2.)
  z = (m*Zmod).min(axis=-1); psiPlot = MOCpsi(VHmod, vmsk=m*numpy.roll(m,-1,axis=-2))*conversion_factor
  yy = y[1:,:].max(axis=-1)+0*z
  plotPsi(yy, z, psiPlot, ci, 'Atlantic MOC [Sv]')
  plt.xlabel(r'Latitude [$\degree$N]')
  plt.suptitle(suptitle)
  findExtrema(yy, z, psiPlot, min_lat=26.5, max_lat=27.) # RAPID
  findExtrema(yy, z, psiPlot, max_lat=-33.)
  findExtrema(yy, z, psiPlot)
  findExtrema(yy, z, psiPlot, min_lat=5.)
  if stream != None:
    plt.savefig(stream[1])
  else:
    plt.savefig(cmdLineArgs.outdir+'/MOC_Atlantic.png')

if __name__ == '__main__':
  run()
