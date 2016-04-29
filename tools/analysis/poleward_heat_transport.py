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
  parser.add_argument('-s','--suptitle', type=str, default='', help='''Super-title for experiment.  Default is to read from netCDF file.''')
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
    if len(rootGroup.variables[varName].shape)==3: advective = rootGroup.variables[varName][:].mean(axis=0).filled(0.)
    else: advective = rootGroup.variables[varName][:].filled(0.)
  else: raise Exception('Could not find "T_ady_2d" in file "%s"'%(cmdLineArgs.annual_file))
  if 'T_diffy_2d' in rootGroup.variables:
    varName = 'T_diffy_2d'
    if len(rootGroup.variables[varName].shape)==3: diffusive = rootGroup.variables[varName][:].mean(axis=0).filled(0.)
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

  def plotHeatTrans(y, HT, title, xlim=(-80,90)):
    plt.plot(y, y*0., 'k', linewidth=0.5)
    plt.plot(y, HT, 'r', linewidth=1.5,label='Model')
    plt.xlim(xlim); plt.ylim(-2.5,3.0)
    plt.title(title)
    plt.grid(True)

  def annotatePlot(label):
    fig = plt.gcf()
    #fig.text(0.1,0.85,label)
    fig.text(0.535,0.12,label)
 
  def annotateObs():
    fig = plt.gcf()
    fig.text(0.1,0.85,r"Trenberth, K. E. and J. M. Caron, 2001: Estimates of Meridional Atmosphere and Ocean Heat Transports. J.Climate, 14, 3433-3443.", fontsize=8)
    fig.text(0.1,0.825,r"Ganachaud, A. and C. Wunsch, 2000: Improved estimates of global ocean circulation, heat transport and mixing from hydrographic data.", fontsize=8)
    fig.text(0.13,0.8,r"Nature, 408, 453-457", fontsize=8)

  m6plot.setFigureSize(npanels=1)

  # Load Observations
  fObs = netCDF4.Dataset('/archive/John.Krasting/obs/TC2001/Trenberth_and_Caron_Heat_Transport.nc')  #Trenberth and Caron
  yobs = fObs.variables['ylat'][:]
  NCEP = {}; NCEP['Global'] = fObs.variables['OTn']
  NCEP['Atlantic'] = fObs.variables['ATLn'][:]; NCEP['IndoPac'] = fObs.variables['INDPACn'][:]
  ECMWF = {}; ECMWF['Global'] = fObs.variables['OTe'][:]
  ECMWF['Atlantic'] = fObs.variables['ATLe'][:]; ECMWF['IndoPac'] = fObs.variables['INDPACe'][:]

  #G and W 
  Global = {}
  Global['lat'] = numpy.array([-30., -19., 24., 47.])
  Global['trans'] = numpy.array([-0.6, -0.8, 1.8, 0.6])
  Global['err'] = numpy.array([0.3, 0.6, 0.3, 0.1])

  Atlantic = {}
  Atlantic['lat'] = numpy.array([-45., -30., -19., -11., -4.5, 7.5, 24., 47.])
  Atlantic['trans'] = numpy.array([0.66, 0.35, 0.77, 0.9, 1., 1.26, 1.27, 0.6])
  Atlantic['err'] = numpy.array([0.12, 0.15, 0.2, 0.4, 0.55, 0.31, 0.15, 0.09])

  IndoPac = {}
  IndoPac['lat'] = numpy.array([-30., -18., 24., 47.])
  IndoPac['trans'] = numpy.array([-0.9, -1.6, 0.52, 0.])
  IndoPac['err'] = numpy.array([0.3, 0.6, 0.2, 0.05,])

  GandW = {}
  GandW['Global'] = Global
  GandW['Atlantic'] = Atlantic
  GandW['IndoPac'] = IndoPac

  def plotGandW(lat,trans,err):
    low = trans - err
    high = trans + err
    for n in range(0,len(low)):
      if n == 0:
        plt.plot([lat[n],lat[n]], [low[n],high[n]], 'c', linewidth=2.0, label='G&W')
      else:
        plt.plot([lat[n],lat[n]], [low[n],high[n]], 'c', linewidth=2.0)
    plt.scatter(lat,trans,marker='s',facecolor='cyan')

  if cmdLineArgs.suptitle != '':  suptitle = cmdLineArgs.suptitle + ' ' + cmdLineArgs.label
  else: suptitle = rootGroup.title + ' ' + cmdLineArgs.label

  # Global Heat Transport
  HTplot = heatTrans(advective,diffusive)
  yy = y[1:,:].max(axis=-1)
  plotHeatTrans(yy,HTplot,title='Global Y-Direction Heat Transport [PW]')
  plt.plot(yobs,NCEP['Global'],'k--',linewidth=0.5,label='NCEP')
  plt.plot(yobs,ECMWF['Global'],'k.',linewidth=0.5,label='ECMWF')
  plotGandW(GandW['Global']['lat'],GandW['Global']['trans'],GandW['Global']['err'])
  plt.xlabel(r'Latitude [$\degree$N]')
  plt.suptitle(suptitle)
  plt.legend(loc=0,fontsize=10)
  annotateObs()
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
  plt.plot(yobs,NCEP['Atlantic'],'k--',linewidth=0.5,label='NCEP')
  plt.plot(yobs,ECMWF['Atlantic'],'k.',linewidth=0.5,label='ECMWF')
  plotGandW(GandW['Atlantic']['lat'],GandW['Atlantic']['trans'],GandW['Atlantic']['err'])
  plt.xlabel(r'Latitude [$\degree$N]')
  plt.suptitle(suptitle)
  plt.legend(loc=0,fontsize=10)
  annotateObs()
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
  HTplot[yy<-34] = numpy.nan
  plotHeatTrans(yy,HTplot,title='Indo-Pacific Y-Direction Heat Transport [PW]')
  plt.plot(yobs,NCEP['IndoPac'],'k--',linewidth=0.5,label='NCEP')
  plt.plot(yobs,ECMWF['IndoPac'],'k.',linewidth=0.5,label='ECMWF')
  plotGandW(GandW['IndoPac']['lat'],GandW['IndoPac']['trans'],GandW['IndoPac']['err'])
  plt.xlabel(r'Latitude [$\degree$N]')
  annotateObs()
  if diffusive == None: annotatePlot('Warning: Diffusive component of transport is missing.')
  plt.suptitle(suptitle)
  plt.legend(loc=0,fontsize=10)
  if stream != None:
    plt.savefig(stream[2])
  else:
    plt.savefig(cmdLineArgs.outdir+'/HeatTransport_IndoPac.png')
 
if __name__ == '__main__':
  run()
