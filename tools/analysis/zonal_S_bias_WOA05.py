#!/usr/bin/env python

import netCDF4
import os
import m6toolbox
import numpy
import m6plot

try: import argparse
except: raise Exception('This version of python is not new enough. python 2.7 or newer is required.')

def run():
  parser = argparse.ArgumentParser(description='''Script for plotting annual-average zonal salinity bias.''')
  parser.add_argument('annual_file', type=str, help='''Annually-averaged file containing 3D 'salt' and 'e'.''')
  parser.add_argument('-l','--label', type=str, default='', help='''Label to add to the plot.''')
  parser.add_argument('-s','--suptitle', type=str, default='', help='''Super-title for experiment.  Default is to read from netCDF file.''')
  parser.add_argument('-o','--outdir', type=str, default='.', help='''Directory in which to place plots.''')
  parser.add_argument('-g','--gridspec', type=str, required=True,
    help='''Directory containing mosaic/grid-spec files (ocean_hgrid.nc and ocean_mask.nc).''')
  parser.add_argument('-w','--woa', type=str, required=True,
    help='''File containing WOA (or obs) data to compare against.''')
  cmdLineArgs = parser.parse_args()
  main(cmdLineArgs)

def main(cmdLineArgs,stream=None):
  if not os.path.exists(cmdLineArgs.gridspec): raise ValueError('Specified gridspec directory/tar file does not exist.')
  if os.path.isdir(cmdLineArgs.gridspec):
    xcenter = netCDF4.Dataset(cmdLineArgs.gridspec+'/ocean_hgrid.nc').variables['x'][1::2,1::2]
    y = netCDF4.Dataset(cmdLineArgs.gridspec+'/ocean_hgrid.nc').variables['y'][1::2,1::2].max(axis=-1)
    ycenter = netCDF4.Dataset(cmdLineArgs.gridspec+'/ocean_hgrid.nc').variables['y'][1::2,1::2]
    msk = netCDF4.Dataset(cmdLineArgs.gridspec+'/ocean_mask.nc').variables['mask'][:]
    area = msk*netCDF4.Dataset(cmdLineArgs.gridspec+'/ocean_hgrid.nc').variables['area'][:,:].reshape([msk.shape[0], 2, msk.shape[1], 2]).sum(axis=-3).sum(axis=-1)
    depth = netCDF4.Dataset(cmdLineArgs.gridspec+'/ocean_topog.nc').variables['depth'][:]
    try: basin = netCDF4.Dataset(cmdLineArgs.gridspec+'/basin_codes.nc').variables['basin'][:]
    except: basin = m6toolbox.genBasinMasks(xcenter, ycenter, depth)
  elif os.path.isfile(cmdLineArgs.gridspec):
    xcenter = m6toolbox.readNCFromTar(cmdLineArgs.gridspec,'ocean_hgrid.nc','x')[1::2,1::2]
    y = m6toolbox.readNCFromTar(cmdLineArgs.gridspec,'ocean_hgrid.nc','y')[1::2,1::2].max(axis=-1)
    ycenter = m6toolbox.readNCFromTar(cmdLineArgs.gridspec,'ocean_hgrid.nc','y')[1::2,1::2]
    msk = m6toolbox.readNCFromTar(cmdLineArgs.gridspec,'ocean_mask.nc','mask')[:]
    area = msk*m6toolbox.readNCFromTar(cmdLineArgs.gridspec,'ocean_hgrid.nc','area')[:,:].reshape([msk.shape[0], 2, msk.shape[1], 2]).sum(axis=-3).sum(axis=-1)
    depth = m6toolbox.readNCFromTar(cmdLineArgs.gridspec,'ocean_topog.nc','depth')[:]
    try: basin = m6toolbox.readNCFromTar(cmdLineArgs.gridspec,'basin_codes.nc','basin')[:]
    except: basin = m6toolbox.genBasinMasks(xcenter, ycenter, depth)
  else:
    raise ValueError('Unable to extract grid information from gridspec directory/tar file.') 

  if stream != None:
    if len(stream) != 4:
      raise ValueError('If specifying output streams, exactly four (4) streams are needed for this analysis')

  Sobs = netCDF4.Dataset( cmdLineArgs.woa ).variables['salt']
  if len(Sobs.shape)==3: Sobs = Sobs[:]
  else: Sobs = Sobs[:].mean(axis=0)
  Zobs = netCDF4.Dataset( cmdLineArgs.woa ).variables['eta'][:]

  rootGroup = netCDF4.MFDataset( cmdLineArgs.annual_file )
  if 'salt' in rootGroup.variables: varName = 'salt'
  elif 'so' in rootGroup.variables: varName = 'so'
  else:raise Exception('Could not find "salt" or "so" in file "%s"'%(cmdLineArgs.annual_file))
  if len(rootGroup.variables[varName].shape)==4: Smod = rootGroup.variables[varName][:].mean(axis=0)
  else: Smod = rootGroup.variables[varName][:]
  if 'e' in rootGroup.variables: Zmod = rootGroup.variables['e'][0]
  else: Zmod = Zobs # Using model z-output
  
  def zonalAverage(S, eta, area, mask=1.):
    vols = ( mask * area ) * ( eta[:-1] - eta[1:] ) # mask * area * level thicknesses
    return numpy.sum( vols * S, axis=-1 ) / numpy.sum( vols, axis=-1 ), (mask*eta).min(axis=-1)
  
  ci=m6plot.pmCI(0.125,2.25,.25)

  if cmdLineArgs.suptitle != '':  suptitle = cmdLineArgs.suptitle + ' ' + cmdLineArgs.label
  else: suptitle = rootGroup.title + ' ' + cmdLineArgs.label
  
  # Global
  sPlot, z = zonalAverage(Smod, Zmod, area)
  sObsPlot, _ = zonalAverage(Sobs, Zobs, area)
  if stream != None: objOut = stream[0]
  else: objOut = cmdLineArgs.outdir+'/S_global_xave_bias_WOA05.png'
  m6plot.yzplot( sPlot - sObsPlot , y, z, splitscale=[0., -1000., -6500.],
        suptitle=suptitle, title='''Global zonal-average salinity bias (w.r.t. WOA'05) [ppt]''',
        clim=ci, colormap='dunnePM', centerlabels=True, extend='both',
        save=objOut)
  
  if stream is None:
    m6plot.yzcompare( sPlot, sObsPlot , y, z, splitscale=[0., -1000., -6500.],
        suptitle=suptitle,
        title1='Global zonal-average salinity [ppt]',
        title2='''WOA'05 salinity [ppt]''',
        clim=m6plot.linCI(20,30,10, 31,39,.5), colormap='dunneRainbow', extend='both',
        dlim=ci, dcolormap='dunnePM', dextend='both', centerdlabels=True,
        save=cmdLineArgs.outdir+'/S_global_xave_bias_WOA05.3_panel.png')
  
  # Atlantic + Arctic
  newMask = 1.*msk; newMask[ (basin!=2) & (basin!=4) ] = 0.
  sPlot, z = zonalAverage(Smod, Zmod, area, mask=newMask)
  sObsPlot, _ = zonalAverage(Sobs, Zobs, area, mask=newMask)
  if stream != None: objOut = stream[1]
  else: objOut = cmdLineArgs.outdir+'/S_Atlantic_xave_bias_WOA05.png'
  m6plot.yzplot( sPlot - sObsPlot , y, z, splitscale=[0., -1000., -6500.],
        suptitle=suptitle, title='''Atlantic zonal-average salinity bias (w.r.t. WOA'05) [ppt]''',
        clim=ci, colormap='dunnePM', centerlabels=True, extend='both',
        save=objOut)
  
  if stream is None:
    m6plot.yzcompare( sPlot, sObsPlot , y, z, splitscale=[0., -1000., -6500.],
        suptitle=suptitle,
        title1='Atlantic zonal-average salinity [ppt]',
        title2='''WOA'05 salinity [ppt]''',
        clim=m6plot.linCI(20,30,10, 31,39,.5), colormap='dunneRainbow', extend='both',
        dlim=ci, dcolormap='dunnePM', dextend='both', centerdlabels=True,
        save=cmdLineArgs.outdir+'/S_Atlantic_xave_bias_WOA05.3_panel.png')
  
  # Pacific
  newMask = 1.*msk; newMask[ (basin!=3) ] = 0.
  sPlot, z = zonalAverage(Smod, Zmod, area, mask=newMask)
  sObsPlot, _ = zonalAverage(Sobs, Zobs, area, mask=newMask)
  if stream != None: objOut = stream[2]
  else: objOut = cmdLineArgs.outdir+'/S_Pacific_xave_bias_WOA05.png'
  m6plot.yzplot( sPlot - sObsPlot , y, z, splitscale=[0., -1000., -6500.],
        suptitle=suptitle, title='''Pacific zonal-average salinity bias (w.r.t. WOA'05) [ppt]''',
        clim=ci, colormap='dunnePM', centerlabels=True, extend='both',
        save=objOut)
  
  if stream is None:
    m6plot.yzcompare( sPlot, sObsPlot , y, z, splitscale=[0., -1000., -6500.],
        suptitle=suptitle,
        title1='Pacific zonal-average salinity [ppt]',
        title2='''WOA'05 salinity [ppt]''',
        clim=m6plot.linCI(20,30,10, 31,39,.5), colormap='dunneRainbow', extend='both',
        dlim=ci, dcolormap='dunnePM', dextend='both', centerdlabels=True,
        save=cmdLineArgs.outdir+'/S_Pacific_xave_bias_WOA05.3_panel.png')
  
  # Indian
  newMask = 1.*msk; newMask[ (basin!=5) ] = 0.
  sPlot, z = zonalAverage(Smod, Zmod, area, mask=newMask)
  sObsPlot, _ = zonalAverage(Sobs, Zobs, area, mask=newMask)
  if stream != None: objOut = stream[3]
  else: objOut = cmdLineArgs.outdir+'/S_Indian_xave_bias_WOA05.png'
  m6plot.yzplot( sPlot - sObsPlot , y, z, splitscale=[0., -1000., -6500.],
        suptitle=suptitle, title='''Indian zonal-average salinity bias (w.r.t. WOA'05) [ppt]''',
        clim=ci, colormap='dunnePM', centerlabels=True, extend='both',
        save=objOut)
  
  if stream is None:
    m6plot.yzcompare( sPlot, sObsPlot , y, z, splitscale=[0., -1000., -6500.],
        suptitle=suptitle,
        title1='Indian zonal-average salinity [ppt]',
        title2='''WOA'05 salinity [ppt]''',
        clim=m6plot.linCI(20,30,10, 31,39,.5), colormap='dunneRainbow', extend='both',
        dlim=ci, dcolormap='dunnePM', dextend='both', centerdlabels=True,
        save=cmdLineArgs.outdir+'/S_Indian_xave_bias_WOA05.3_panel.png')

if __name__ == '__main__':
  run()
