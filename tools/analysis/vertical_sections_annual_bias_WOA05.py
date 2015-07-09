#!/usr/bin/env python

import netCDF4
import numpy
import m6plot
import matplotlib.pyplot as plt

try: import argparse
except: raise Exception('This version of python is not new enough. python 2.7 or newer is required.')

parser = argparse.ArgumentParser(description='''Script for plotting annual-average zonal temperature bias.''')
parser.add_argument('annual_file', type=str, help='''Annually-averaged file containing 3D 'temp' and 'e'.''')
parser.add_argument('-l','--label', type=str, default='', help='''Label to add to the plot.''')
parser.add_argument('-o','--outdir', type=str, default='.', help='''Directory in which to place plots.''')
parser.add_argument('-g','--gridspecdir', type=str, required=True,
  help='''Directory containing mosaic/grid-spec files (ocean_hgrid.nc and ocean_mask.nc).''')
parser.add_argument('-w','--woa', type=str, required=True,
  help='''File containing WOA (or obs) data to compare against.''')
cmdLineArgs = parser.parse_args()

x = netCDF4.Dataset(cmdLineArgs.gridspecdir+'/ocean_hgrid.nc').variables['x'][1::2,1::2]
y = netCDF4.Dataset(cmdLineArgs.gridspecdir+'/ocean_hgrid.nc').variables['y'][1::2,1::2]
xg = netCDF4.Dataset(cmdLineArgs.gridspecdir+'/ocean_hgrid.nc').variables['x'][0::2,0::2]
yg = netCDF4.Dataset(cmdLineArgs.gridspecdir+'/ocean_hgrid.nc').variables['y'][0::2,0::2]
msk = netCDF4.Dataset(cmdLineArgs.gridspecdir+'/ocean_mask.nc').variables['mask'][:]
area = msk*netCDF4.Dataset(cmdLineArgs.gridspecdir+'/ocean_hgrid.nc').variables['area'][:,:].reshape([msk.shape[0], 2, msk.shape[1], 2]).sum(axis=-3).sum(axis=-1)
basin = netCDF4.Dataset(cmdLineArgs.gridspecdir+'/basin_codes.nc').variables['basin'][:]

obsRootGroup = netCDF4.Dataset( cmdLineArgs.woa )
if 'temp' in obsRootGroup.variables: OTvar = 'temp'
else: OTvar = 'ptemp'
Zobs = netCDF4.Dataset( cmdLineArgs.woa ).variables['eta']

rootGroup = netCDF4.Dataset( cmdLineArgs.annual_file )
if 'temp' in rootGroup.variables: varName = 'temp'
elif 'ptemp' in rootGroup.variables: varName = 'ptemp'
elif 'thetao' in rootGroup.variables: varName = 'thetao'
else: raise Exception('Could not find "temp", "ptemp" or "thetao" in file "%s"'%(cmdLineArgs.annual_file))
if len(rootGroup.variables[varName].shape)==4: need_time_average = True
else: need_time_average = False
if 'e' in rootGroup.variables: Zmod = rootGroup.variables['e']
else: Zmod = Zobs # Using model z-output

ci=m6plot.pmCI(0.1,0.5,.2, 1.0,4.5,1.)

# Pacific equator
j = numpy.abs( y[:,0] - 0. ).argmin()
i0 = numpy.abs( numpy.mod( x[j,:] - 117. + 360., 360. ) ).argmin()
i1 = numpy.abs( numpy.mod( x[j,:] + 78. + 360., 360. ) ).argmin()
tPlot = rootGroup.variables[varName][0,:,j,i0:i1]
tObsPlot = obsRootGroup.variables[OTvar][0,:,j,i0:i1]
zi = Zobs[:,j,i0:i1]; z = 0.5 * ( zi[:-1] + zi[1:] )
m6plot.yzplot( tPlot - tObsPlot , x[j,i0:i1][:], zi,
      ylabel='Longitude',
      suptitle=rootGroup.title+' '+cmdLineArgs.label, title=r'''Pacific equator $\theta$ bias (w.r.t. WOA'05) [$\degree$C]''',
      clim=ci, colormap='dunnePM', centerlabels=True, extend='both')
cs1 = plt.contour( x[j,i0:i1][:] + 0*z, z, tObsPlot, levels=numpy.arange(0.,45,2.), colors='k' ); plt.clabel(cs1,fmt='%.0f')
cs2 = plt.contour( x[j,i0:i1][:] + 0*z, z, tPlot, levels=numpy.arange(0.,45,2.), colors='g' ); plt.clabel(cs2,fmt='%.0f')
plt.ylim(-1200,0)
plt.savefig(cmdLineArgs.outdir+'/T_Pacific_equator_bias_WOA05.png')

m6plot.yzcompare( tPlot, tObsPlot , x[j,i0:i1], zi, splitscale=[0., -1000., -6500.],
      suptitle=rootGroup.title+' '+cmdLineArgs.label,
      ylabel='Longitude',
      title1=r'Pacific equator $\theta$ [$\degree$C]',
      title2=r'''WOA'05 $\theta$ [$\degree$C]''',
      clim=m6plot.linCI(-2,29,.5), colormap='dunneRainbow', extend='max',
      dlim=ci, dcolormap='dunnePM', dextend='both', centerdlabels=True,
      save=cmdLineArgs.outdir+'/T_Pacific_equator_bias_WOA05.3_panel.png')

# Atlantic equator
j = numpy.abs( y[:,0] - 0. ).argmin()
i0 = numpy.abs( numpy.mod( x[j,:] + 52. + 360., 360. ) ).argmin()
i1 = numpy.abs( numpy.mod( x[j,:] - 10.5 + 360., 360. ) ).argmin()
tPlot = rootGroup.variables[varName][0,:,j,i0:i1]
tObsPlot = obsRootGroup.variables[OTvar][0,:,j,i0:i1]
zi = Zobs[:,j,i0:i1]; z = 0.5 * ( zi[:-1] + zi[1:] )
m6plot.yzplot( tPlot - tObsPlot , x[j,i0:i1][:], zi,
      ylabel='Longitude',
      suptitle=rootGroup.title+' '+cmdLineArgs.label, title=r'''Atlantic equator $\theta$ bias (w.r.t. WOA'05) [$\degree$C]''',
      clim=ci, colormap='dunnePM', centerlabels=True, extend='both')
cs1 = plt.contour( x[j,i0:i1][:] + 0*z, z, tObsPlot, levels=numpy.arange(0.,45,2.), colors='k' ); plt.clabel(cs1,fmt='%.0f')
cs2 = plt.contour( x[j,i0:i1][:] + 0*z, z, tPlot, levels=numpy.arange(0.,45,2.), colors='g' ); plt.clabel(cs2,fmt='%.0f')
plt.ylim(-1200,0)
plt.savefig(cmdLineArgs.outdir+'/T_Atlantic_equator_bias_WOA05.png')

m6plot.yzcompare( tPlot, tObsPlot , x[j,i0:i1], zi, splitscale=[0., -1000., -6500.],
      suptitle=rootGroup.title+' '+cmdLineArgs.label,
      ylabel='Longitude',
      title1=r'Atlantic equator $\theta$ [$\degree$C]',
      title2=r'''WOA'05 $\theta$ [$\degree$C]''',
      clim=m6plot.linCI(-2,29,.5), colormap='dunneRainbow', extend='max',
      dlim=ci, dcolormap='dunnePM', dextend='both', centerdlabels=True,
      save=cmdLineArgs.outdir+'/T_Atlantic_equator_bias_WOA05.3_panel.png')

# 170W, 20S-20N
j0 = numpy.abs( y[:,0] + 20. ).argmin()
j1 = numpy.abs( y[:,0] - 20. ).argmin()
i = numpy.abs( numpy.mod( x[j0,:] + 170. + 360., 360. ) ).argmin()
tPlot = rootGroup.variables[varName][0,:,j0:j1,i]
tObsPlot = obsRootGroup.variables[OTvar][0,:,j0:j1,i]
zi = Zobs[:,j0:j1,i]; z = 0.5 * ( zi[:-1] + zi[1:] )
m6plot.yzplot( tPlot - tObsPlot , y[j0:j1,i][:], zi,
      suptitle=rootGroup.title+' '+cmdLineArgs.label, title=r'''170$\degree$W $\theta$ bias (w.r.t. WOA'05) [$\degree$C]''',
      clim=ci, colormap='dunnePM', centerlabels=True, extend='both')
cs1 = plt.contour( y[j0:j1,i][:] + 0*z, z, tObsPlot, levels=numpy.arange(0.,45,2.), colors='k' ); plt.clabel(cs1,fmt='%.0f')
cs2 = plt.contour( y[j0:j1,i][:] + 0*z, z, tPlot, levels=numpy.arange(0.,45,2.), colors='g' ); plt.clabel(cs2,fmt='%.0f')
plt.ylim(-1200,0)
plt.savefig(cmdLineArgs.outdir+'/T_170W_bias_WOA05.png')

m6plot.yzcompare( tPlot, tObsPlot , y[j0:j1,i], zi, splitscale=[0., -1000., -6500.],
      suptitle=rootGroup.title+' '+cmdLineArgs.label,
      title1=r'170$\degree$W $\theta$ [$\degree$C]',
      title2=r'''WOA'05 $\theta$ [$\degree$C]''',
      clim=m6plot.linCI(-2,29,.5), colormap='dunneRainbow', extend='max',
      dlim=ci, dcolormap='dunnePM', dextend='both', centerdlabels=True,
      save=cmdLineArgs.outdir+'/T_170W_bias_WOA05.3_panel.png')

m6plot.setFigureSize(); axis=plt.gca()
uPlot = rootGroup.variables['uo'][0,:,j0:j1,i]
plt.contourf( y[j0:j1,i][:] + 0*z, z, uPlot, levels=m6plot.linCI(-0.5,1.3,0.1), cmap='spectral', extend='both')
plt.colorbar(extend='both')
cs1 = plt.contour( y[j0:j1,i][:] + 0*z, z, uPlot, levels=m6plot.linCI(-0.5,1.3,0.1), colors='k'); plt.clabel(cs1,cs1.levels[::2],fmt='%.1f',inline_spacing=1)
plt.ylim(-600,0); plt.suptitle(rootGroup.title+' '+cmdLineArgs.label);plt.title(r'170$\degree$W u [m/s]')
plt.xlabel(r'Latitude [$\degree$N]'); plt.ylabel('Elevation [m]')
plt.savefig(cmdLineArgs.outdir+'/U_170W_bias_WOA05.png')

# 140W, 20S-20N
j0 = numpy.abs( y[:,0] + 20. ).argmin()
j1 = numpy.abs( y[:,0] - 20. ).argmin()
i = numpy.abs( numpy.mod( x[j0,:] + 140. + 360., 360. ) ).argmin()
tPlot = rootGroup.variables[varName][0,:,j0:j1,i]
tObsPlot = obsRootGroup.variables[OTvar][0,:,j0:j1,i]
zi = Zobs[:,j0:j1,i]; z = 0.5 * ( zi[:-1] + zi[1:] )
m6plot.yzplot( tPlot - tObsPlot , y[j0:j1,i][:], zi,
      suptitle=rootGroup.title+' '+cmdLineArgs.label, title=r'''140$\degree$W $\theta$ bias (w.r.t. WOA'05) [$\degree$C]''',
      clim=ci, colormap='dunnePM', centerlabels=True, extend='both')
cs1 = plt.contour( y[j0:j1,i][:] + 0*z, z, tObsPlot, levels=numpy.arange(0.,45,2.), colors='k' ); plt.clabel(cs1,fmt='%.0f')
cs2 = plt.contour( y[j0:j1,i][:] + 0*z, z, tPlot, levels=numpy.arange(0.,45,2.), colors='g' ); plt.clabel(cs2,fmt='%.0f')
plt.ylim(-1200,0)
plt.savefig(cmdLineArgs.outdir+'/T_140W_bias_WOA05.png')

m6plot.yzcompare( tPlot, tObsPlot , y[j0:j1,i], zi, splitscale=[0., -1000., -6500.],
      suptitle=rootGroup.title+' '+cmdLineArgs.label,
      title1=r'140$\degree$W $\theta$ [$\degree$C]',
      title2=r'''WOA'05 $\theta$ [$\degree$C]''',
      clim=m6plot.linCI(-2,29,.5), colormap='dunneRainbow', extend='max',
      dlim=ci, dcolormap='dunnePM', dextend='both', centerdlabels=True,
      save=cmdLineArgs.outdir+'/T_140W_bias_WOA05.3_panel.png')

m6plot.setFigureSize(); axis=plt.gca()
uPlot = rootGroup.variables['uo'][0,:,j0:j1,i]
plt.contourf( y[j0:j1,i][:] + 0*z, z, uPlot, levels=m6plot.linCI(-0.5,1.3,0.1), cmap='spectral', extend='both')
plt.colorbar(extend='both')
cs1 = plt.contour( y[j0:j1,i][:] + 0*z, z, uPlot, levels=m6plot.linCI(-0.5,1.3,0.1), colors='k'); plt.clabel(cs1,cs1.levels[::2],fmt='%.1f',inline_spacing=1)
plt.ylim(-600,0); plt.suptitle(rootGroup.title+' '+cmdLineArgs.label);plt.title(r'140$\degree$W u [m/s]')
plt.xlabel(r'Latitude [$\degree$N]'); plt.ylabel('Elevation [m]')
plt.savefig(cmdLineArgs.outdir+'/U_140W_bias_WOA05.png')

# 110W, 20S-20N
j0 = numpy.abs( y[:,0] + 20. ).argmin()
j1 = numpy.abs( y[:,0] - 20. ).argmin()
i = numpy.abs( numpy.mod( x[j0,:] + 110. + 360., 360. ) ).argmin()
tPlot = rootGroup.variables[varName][0,:,j0:j1,i]
tObsPlot = obsRootGroup.variables[OTvar][0,:,j0:j1,i]
zi = Zobs[:,j0:j1,i]; z = 0.5 * ( zi[:-1] + zi[1:] )
m6plot.yzplot( tPlot - tObsPlot , y[j0:j1,i][:], zi,
      suptitle=rootGroup.title+' '+cmdLineArgs.label, title=r'''110$\degree$W $\theta$ bias (w.r.t. WOA'05) [$\degree$C]''',
      clim=ci, colormap='dunnePM', centerlabels=True, extend='both')
cs1 = plt.contour( y[j0:j1,i][:] + 0*z, z, tObsPlot, levels=numpy.arange(0.,45,2.), colors='k' ); plt.clabel(cs1,fmt='%.0f')
cs2 = plt.contour( y[j0:j1,i][:] + 0*z, z, tPlot, levels=numpy.arange(0.,45,2.), colors='g' ); plt.clabel(cs2,fmt='%.0f')
plt.ylim(-1200,0)
plt.savefig(cmdLineArgs.outdir+'/T_110W_bias_WOA05.png')

m6plot.yzcompare( tPlot, tObsPlot , y[j0:j1,i], zi, splitscale=[0., -1000., -6500.],
      suptitle=rootGroup.title+' '+cmdLineArgs.label,
      title1=r'110$\degree$W $\theta$ [$\degree$C]',
      title2=r'''WOA'05 $\theta$ [$\degree$C]''',
      clim=m6plot.linCI(-2,29,.5), colormap='dunneRainbow', extend='max',
      dlim=ci, dcolormap='dunnePM', dextend='both', centerdlabels=True,
      save=cmdLineArgs.outdir+'/T_110W_bias_WOA05.3_panel.png')

m6plot.setFigureSize(); axis=plt.gca()
uPlot = rootGroup.variables['uo'][0,:,j0:j1,i]
plt.contourf( y[j0:j1,i][:] + 0*z, z, uPlot, levels=m6plot.linCI(-0.5,1.3,0.1), cmap='spectral', extend='both')
plt.colorbar(extend='both')
cs1 = plt.contour( y[j0:j1,i][:] + 0*z, z, uPlot, levels=m6plot.linCI(-0.5,1.3,0.1), colors='k'); plt.clabel(cs1,cs1.levels[::2],fmt='%.1f',inline_spacing=1)
plt.ylim(-600,0); plt.suptitle(rootGroup.title+' '+cmdLineArgs.label);plt.title(r'110$\degree$W u [m/s]')
plt.xlabel(r'Latitude [$\degree$N]'); plt.ylabel('Elevation [m]')
plt.savefig(cmdLineArgs.outdir+'/U_110W_bias_WOA05.png')

