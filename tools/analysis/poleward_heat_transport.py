#!/usr/bin/env python

import netCDF4
import numpy
import m6plot
import matplotlib.pyplot as plt
import sys
import warnings

def run():
  try: import argparse
  except: raise Exception('This version of python is not new enough. python 2.7 or newer is required.')
  parser = argparse.ArgumentParser(description='''Script for plotting plotting poleward heat transport.''')
  parser.add_argument('annual_file', type=str, help='''Annually-averaged file containing 3D 'T_ady_2d' and 'T_diffy_2d'.''')
  parser.add_argument('-l','--label', type=str, default='', help='''Label to add to the plot.''')
  parser.add_argument('-o','--outdir', type=str, default='.', help='''Directory in which to place plots.''')
  parser.add_argument('-g','--gridspecdir', type=str, required=True,
    help='''Directory containing mosaic/grid-spec files (ocean_hgrid.nc and ocean_mask.nc).''')
  cmdLineArgs = parser.parse_args()
  main(cmdLineArgs)

def main(cmdLineArgs,stream=None):
  #x = netCDF4.Dataset(cmdLineArgs.gridspecdir+'/ocean_hgrid.nc').variables['x'][::2,::2]
  y = netCDF4.Dataset(cmdLineArgs.gridspecdir+'/ocean_hgrid.nc').variables['y'][::2,::2]
  msk = netCDF4.Dataset(cmdLineArgs.gridspecdir+'/ocean_mask.nc').variables['mask'][:]
  area = msk*netCDF4.Dataset(cmdLineArgs.gridspecdir+'/ocean_hgrid.nc').variables['area'][:,:].reshape([msk.shape[0], 2, msk.shape[1], 2]).sum(axis=-3).sum(axis=-1)
  depth = netCDF4.Dataset(cmdLineArgs.gridspecdir+'/ocean_topog.nc').variables['depth'][:]
  basin_code = netCDF4.Dataset(cmdLineArgs.gridspecdir+'/basin_codes.v20140629.nc').variables['basin'][:]
  
  if stream != None:
    if len(stream) != 2:
      raise ValueError('If specifying output streams, exactly two streams are needed for this analysis')
  
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
  plt.show(block=False) 

  # Atlantic Heat Transport
  plt.clf()
  m = 0*basin_code; m[(basin_code==2) | (basin_code==4)] = 1
  HTplot = heatTrans(advective, diffusive, vmask=m*numpy.roll(m,1,axis=1))
  yy = y[1:,:].max(axis=-1)
  HTplot[yy<-34] = numpy.nan
  plotHeatTrans(yy,HTplot,title='Atlantic Y-Direction Heat Transport [PW]')
  plt.xlabel(r'Latitude [$\degree$N]')
  plt.suptitle(rootGroup.title+' '+cmdLineArgs.label)
  if diffusive == None: annotatePlot('Warning: Diffusive component of transport is missing.')
  if stream != None:
    plt.savefig(stream[0])
  else:
    plt.savefig(cmdLineArgs.outdir+'/HeatTransport_Atlantic.png')
  plt.show(block=False) 
   
  # Indo-Pacific Heat Transport
  plt.clf()
  m = 0*basin_code; m[(basin_code==3) | (basin_code==5)] = 1
  HTplot = heatTrans(advective, diffusive, vmask=m*numpy.roll(m,1,axis=1))
  yy = y[1:,:].max(axis=-1)
  HTplot[yy<-38] = numpy.nan
  plotHeatTrans(yy,HTplot,title='Indo-Pacific Y-Direction Heat Transport [PW]')
  plt.xlabel(r'Latitude [$\degree$N]')
  if diffusive == None: annotatePlot('Warning: Diffusive component of transport is missing.')
  plt.suptitle(rootGroup.title+' '+cmdLineArgs.label)
  if stream != None:
    plt.savefig(stream[0])
  else:
    plt.savefig(cmdLineArgs.outdir+'/HeatTransport_IndoPac.png')
  plt.show(block=False)
 
if __name__ == '__main__':
  run()
