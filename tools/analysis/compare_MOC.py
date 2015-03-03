#!/usr/bin/env python

import netCDF4
import numpy
import m6plot
import matplotlib.pyplot as plt

try: import argparse
except: raise Exception('This version of python is not new enough. python 2.7 or newer is required.')

parser = argparse.ArgumentParser(description='''Script for plotting meridional overturning.''')
parser.add_argument('annual_file', type=str, help='''Annually-averaged file containing 3D 'temp' and 'e'.''')
parser.add_argument('-l','--label', type=str, default='', help='''Label to add to the plot.''')
parser.add_argument('-1','--label1', type=str, default='', help='''Lable to give experiment 1.''')
parser.add_argument('-2','--label2', type=str, default='', help='''Lable to give experiment 2.''')
parser.add_argument('-o','--outdir', type=str, default='.', help='''Directory in which to place plots.''')
parser.add_argument('-g','--gridspecdir', type=str, required=True,
  help='''Directory containing mosaic/grid-spec files (ocean_hgrid.nc and ocean_mask.nc).''')
parser.add_argument('-r','--ref', type=str, required=True,
  help='''File containing reference experiment to compare against.''')
cmdLineArgs = parser.parse_args()

#x = netCDF4.Dataset(cmdLineArgs.gridspecdir+'/ocean_hgrid.nc').variables['x'][::2,::2]
y = netCDF4.Dataset(cmdLineArgs.gridspecdir+'/ocean_hgrid.nc').variables['y'][::2,::2]
msk = netCDF4.Dataset(cmdLineArgs.gridspecdir+'/ocean_mask.nc').variables['mask'][:]
area = msk*netCDF4.Dataset(cmdLineArgs.gridspecdir+'/ocean_hgrid.nc').variables['area'][:,:].reshape([msk.shape[0], 2, msk.shape[1], 2]).sum(axis=-3).sum(axis=-1)
depth = netCDF4.Dataset(cmdLineArgs.gridspecdir+'/ocean_topog.nc').variables['depth'][:]
basin_code = netCDF4.Dataset(cmdLineArgs.gridspecdir+'/basin_codes.v20140629.nc').variables['basin'][:]

rootGroupRef = netCDF4.Dataset( cmdLineArgs.ref )
if 'vh' in rootGroupRef.variables: varName = 'vh'
else: raise Exception('Could not find "vh" in file "%s"'%(cmdLineArgs.ref))
if len(rootGroupRef.variables[varName].shape)==4: VHref = rootGroupRef.variables[varName][:].mean(axis=0).filled(0.)
else: VHref = rootGroupRef.variables[varName][:].filled(0.)

rootGroup = netCDF4.Dataset( cmdLineArgs.annual_file )
if 'vh' in rootGroup.variables: varName = 'vh'
else: raise Exception('Could not find "vh" in file "%s"'%(cmdLineArgs.annual_file))
if len(rootGroup.variables[varName].shape)==4: VHmod = rootGroup.variables[varName][:].mean(axis=0).filled(0.)
else: VHmod = rootGroup.variables[varName][:].filled(0.)
if 'e' in rootGroup.variables: Zmod = rootGroup.variables['e'][0]
else: Zmod = rootGroup.variables['e'][0] # Using model z-ou:put

def MOCpsi(vh, vmsk=None):
  """Sums 'vh' zonally and cumulatively in the vertical to yield an overturning stream function, psi(y,z)."""
  shape = list(vh.shape); shape[-3] += 1
  psi = numpy.zeros(shape[:-1])
  if len(shape)==3:
    for k in range(shape[-3]-1,0,-1):
      if vmsk==None: psi[k-1,:] = psi[k,:] - vh[k-1].sum(axis=-1)
      else: psi[k-1,:] = psi[k,:] - (vmsk*vh[k-1]).sum(axis=-1)
  else:
    for n in range(shape[0]):
      for k in range(shape[-3]-1,0,-1):
        if vmsk==None: psi[n,k-1,:] = psi[n,k,:] - vh[n,k-1].sum(axis=-1)
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
  #plt.xlabel(r'Latitude [$\degree$N]')

def findExtrema(y, z, psi, min_lat=-90., max_lat=90., min_depth=0., mult=1.):
  psiMax = mult*numpy.amax( mult * numpy.ma.array(psi)[(y>=min_lat) & (y<=max_lat) & (z<-min_depth)] )
  idx = numpy.argmin(numpy.abs(psi-psiMax))
  (j,i) = numpy.unravel_index(idx, psi.shape)
  plt.plot(y[j,i],z[j,i],'kx',hold=True)
  plt.text(y[j,i],z[j,i],'%.1f'%(psi[j,i]))

m6plot.setFigureSize(npanels=3)
if len(cmdLineArgs.label1): title1 = cmdLineArgs.label1
else: title1 = rootGroup.title
if len(cmdLineArgs.label2): title2 = cmdLineArgs.label2
else: title2 = rootGroupRef.title

# Global MOC
z = Zmod.min(axis=-1)
yy = y[1:,:].max(axis=-1)+0*z
psiPlotM = MOCpsi(VHmod)/1e6
psiPlotR = MOCpsi(VHref)/1e6
ci=m6plot.pmCI(0.,40.,5.)
di=m6plot.pmCI(0.,5.,0.5)
plt.subplot(311)
plotPsi(yy, z, psiPlotM, ci, title1)
findExtrema(yy, z, psiPlotM, max_lat=-30.)
findExtrema(yy, z, psiPlotM, min_lat=25.)
findExtrema(yy, z, psiPlotM, min_depth=2000., mult=-1.)
plt.subplot(312)
plotPsi(yy, z, psiPlotR, ci, title2)
findExtrema(yy, z, psiPlotR, max_lat=-30.)
findExtrema(yy, z, psiPlotR, min_lat=25.)
findExtrema(yy, z, psiPlotR, min_depth=2000., mult=-1.)
plt.subplot(313)
plotPsi(yy, z, psiPlotM-psiPlotR, di, title1 + ' - ' + title2)
plt.xlabel(r'Latitude [$\degree$N]')
plt.suptitle('Global MOC')
plt.savefig(cmdLineArgs.outdir+'/MOC_global_difference.3_panel.png')

m6plot.setFigureSize(npanels=1)
plt.clf()
plotPsi(yy, z, psiPlotM-psiPlotR, di, title1 + ' - ' + title2)
plt.xlabel(r'Latitude [$\degree$N]')
plt.suptitle('Global MOC')
plt.savefig(cmdLineArgs.outdir+'/MOC_global_difference.png')

# Atlantic MOC
m6plot.setFigureSize(npanels=3)
plt.clf()
m = 0*basin_code; m[(basin_code==2) | (basin_code==4) | (basin_code==6) | (basin_code==7) | (basin_code==8)]=1
z = (m*Zmod).min(axis=-1)
y = y[1:,:].max(axis=-1)+0*z
psiPlotM = MOCpsi(VHmod, vmsk=m*numpy.roll(m,1,axis=1))/1e6
psiPlotR = MOCpsi(VHref, vmsk=m*numpy.roll(m,1,axis=1))/1e6
ci=m6plot.pmCI(0.,22.,2.)
di=m6plot.pmCI(0.,5.,0.5)
plt.subplot(311)
plotPsi(yy, z, psiPlotM, ci, title1)
findExtrema(yy, z, psiPlotM, min_lat=26.5, max_lat=27.)
findExtrema(yy, z, psiPlotM, max_lat=-33.)
findExtrema(yy, z, psiPlotM)
plt.subplot(312)
plotPsi(yy, z, psiPlotR, ci, title2)
findExtrema(yy, z, psiPlotR, min_lat=26.5, max_lat=27.)
findExtrema(yy, z, psiPlotR, max_lat=-33.)
findExtrema(yy, z, psiPlotR)
plt.subplot(313)
plotPsi(yy, z, psiPlotM-psiPlotR, di, title1 + ' - ' + title2)
plt.xlabel(r'Latitude [$\degree$N]')
plt.suptitle('Atlantic MOC')
plt.savefig(cmdLineArgs.outdir+'/MOC_Atlantic_difference.3_panel.png')

m6plot.setFigureSize(npanels=1)
plt.clf()
plotPsi(yy, z, psiPlotM-psiPlotR, di, title1 + ' - ' + title2)
plt.xlabel(r'Latitude [$\degree$N]')
plt.suptitle('Atlantic MOC')
plt.savefig(cmdLineArgs.outdir+'/MOC_Atlantic_difference.png')
