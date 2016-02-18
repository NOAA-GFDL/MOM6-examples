#!/usr/bin/env python

import netCDF4
import numpy
import m6plot
import m6toolbox
import matplotlib.pyplot as plt
import os
import sys
import warnings

def run():
  try: import argparse
  except: raise Exception('This version of python is not new enough. python 2.7 or newer is required.')
  parser = argparse.ArgumentParser(description='''Script for plotting plotting poleward heat transport.''')
  parser.add_argument('annual_file', type=str, help='''Annually-averaged file containing 3D 'T_ady_2d' and 'T_diffy_2d'.''')
  parser.add_argument('-l','--label', type=str, default='', help='''Label to add to the plot.''')
  parser.add_argument('-o','--outdir', type=str, default='.', help='''Directory in which to place plots.''')
  parser.add_argument('-g','--gridspec', type=str, required=True,
    help='''Directory or tarfile containing mosaic/grid-spec files (ocean_hgrid.nc and ocean_mask.nc).''')
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
    if len(stream) != 3:
      raise ValueError('If specifying output streams, exactly three streams are needed for this analysis')
  
  rootGroup = netCDF4.MFDataset( cmdLineArgs.annual_file )
  if 'T_ady_2d' in rootGroup.variables:
    varName = 'T_ady_2d'
    if len(rootGroup.variables[varName].shape)==4: advective = rootGroup.variables[varName][:].mean(axis=0).filled(0.)
    else: advective = rootGroup.variables[varName][:].filled(0.)
  else: raise Exception('Could not find "T_ady_2d" in file "%s"'%(cmdLineArgs.annual_file))
  if 'T_diffy_2d' in rootGroup.variables:
    varName = 'T_diffy_2d'
    if len(rootGroup.variables[varName].shape)==4: diffusive = rootGroup.variables[varName][:].mean(axis=0).filled(0.)
    else: diffusive = rootGroup.variables[varName][:].filled(0.)
  else: 
    diffusive = None
    warnings.warn('Diffusive temperature term not found. This will result in an underestimation of the heat transport.')

  def heatTrans(advective, diffusive=None, vmask=None):
    """Converts vertically integrated temperature advection into heat transport"""
    rho0 = 1.035e3; Cp = 3989.
    if diffusive != None: HT = advective + diffusive
    else: HT = advective
    HT = HT * (rho0 * Cp); HT = HT * 1.e-15  # convert to PW
    if vmask != None: HT = HT*vmask
    HT = HT.sum(axis=-1); HT = HT.squeeze() # sum in x-direction
    return HT

  def plotHeatTrans(y, HT, title):
    plt.plot(y, y*0., 'k', linewidth=0.5)
    plt.plot(y, HT, 'k', linewidth=1.5)
    plt.xlim(-80,90); plt.ylim(-2.0,3.0)
    plt.title(title)
    plt.grid(True)

  def annotatePlot(label):
    fig = plt.gcf()
    fig.text(0.1,0.85,label)
 
  m6plot.setFigureSize(npanels=1)

  # Global Heat Transport
  HTplot = heatTrans(advective,diffusive)
  yy = y[1:,:].max(axis=-1)
  plotHeatTrans(yy,HTplot,title='Global Y-Direction Heat Transport [PW]')
  plt.xlabel(r'Latitude [$\degree$N]')
  plt.suptitle(rootGroup.title+' '+cmdLineArgs.label)
  if diffusive == None: annotatePlot('Warning: Diffusive component of transport is missing.')
  if stream != None:
    plt.savefig(stream[0])
  else:
    plt.savefig(cmdLineArgs.outdir+'/HeatTransport_global.png')

  # Atlantic Heat Transport
  plt.clf()
  m = 0*basin_code; m[(basin_code==2) | (basin_code==4) | (basin_code==6) | (basin_code==7) | (basin_code==8)] = 1
  HTplot = heatTrans(advective, diffusive, vmask=m*numpy.roll(m,-1,axis=-2))
  yy = y[1:,:].max(axis=-1)
  HTplot[yy<-34] = numpy.nan
  plotHeatTrans(yy,HTplot,title='Atlantic Y-Direction Heat Transport [PW]')
  plt.xlabel(r'Latitude [$\degree$N]')
  plt.suptitle(rootGroup.title+' '+cmdLineArgs.label)
  if diffusive == None: annotatePlot('Warning: Diffusive component of transport is missing.')
  if stream != None:
    plt.savefig(stream[1])
  else:
    plt.savefig(cmdLineArgs.outdir+'/HeatTransport_Atlantic.png')
   
  # Indo-Pacific Heat Transport
  plt.clf()
  m = 0*basin_code; m[(basin_code==3) | (basin_code==5)] = 1
  HTplot = heatTrans(advective, diffusive, vmask=m*numpy.roll(m,-1,axis=-2))
  yy = y[1:,:].max(axis=-1)
  HTplot[yy<-38] = numpy.nan
  plotHeatTrans(yy,HTplot,title='Indo-Pacific Y-Direction Heat Transport [PW]')
  plt.xlabel(r'Latitude [$\degree$N]')
  if diffusive == None: annotatePlot('Warning: Diffusive component of transport is missing.')
  plt.suptitle(rootGroup.title+' '+cmdLineArgs.label)
  if stream != None:
    plt.savefig(stream[2])
  else:
    plt.savefig(cmdLineArgs.outdir+'/HeatTransport_IndoPac.png')
 
if __name__ == '__main__':
  run()
