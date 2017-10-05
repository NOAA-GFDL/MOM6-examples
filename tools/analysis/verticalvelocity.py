#!/usr/bin/env python
# Estimate vertical mass transport (wmo) by the divergence of the horizontal mass transports. The vertical mass transport across an
# interface is the cumulative integral starting from the bottom of a water column. The sign convention is w>0 is an upward transport,
# (i.e., towards the surface of the ocean). By this convention, then div(u,v)<0 implies a negative (downward) transport and vice versa.
# Written by Andrew Shao (andrew.shao@noaa.gov) 29 September 2017
import numpy as np

def calc_w_from_convergence(u_var, v_var, wrapx = True, wrapy = False):

  tmax = u_var.shape[0]

  ntime, nk, nlat, nlon = u_var.shape
  w = np.ma.zeros( (ntime, nk+1, nlat, nlon)  )
  # Work timelevel by timelevel
  for tidx in range(0,tmax):
    # Get and process the u component
    u_dat = u_var[tidx,:,:,:]
    h_mask = np.logical_or(np.ma.getmask(u_dat), np.ma.getmask(np.roll(u_dat,1,axis=-1)))
    u_dat = u_dat.filled(0.)

    # Get and process the v component
    v_dat = v_var[tidx,:,:,:]
    h_mask = np.logical_or(h_mask,np.ma.getmask(v_dat))
    h_mask = np.logical_or(h_mask,np.ma.getmask(np.roll(v_dat,1,axis=-2)))
    v_dat = v_dat.filled(0.)

    # Order of subtraction based on upwind sign convention and desire for w>0 to correspond with upwards velocity
    w[tidx,:-1,:,:] += np.roll(u_dat,1,axis=-1)-u_dat
    if not wrapx: # If not wrapping, then convergence on westernmost side is simply so subtract back the rolled value
      w[tidx,:-1,:,0] += -u_dat[:-1,:,-1]
    w[tidx,:-1,:,:] += np.roll(v_dat,1,axis=-2)-v_dat
    if not wrapy: # If not wrapping, convergence on westernmost side is v
      w[tidx,:-1,0,:] += -v_dat[:,-1,:]
    w[tidx,-1,:,:] = 0.
    # Do a double-flip so that we integrate from the bottom
    w[tidx,:-1,:,:] = w[tidx,-2::-1,:,:].cumsum(axis=0)[::-1,:,:]
    # Mask if any of u[i-1], u[i], v[j-1], v[j] are not masked
    w[tidx,:-1,:,:] = np.ma.masked_where(h_mask, w[tidx,:-1,:,:])
    # Bottom should always be zero, mask applied wherever the top interface is a valid value
    w[tidx,-1,:,:] = np.ma.masked_where(h_mask[-2,:,:], w[tidx,-1,:,:])

  return w

if __name__ == "__main__":
  try: import argparse
  except: raise Exception('This version of python is not new enough. python 2.7 or newer is required.')
  import netCDF4

  parser = argparse.ArgumentParser(description=
           '''Script for calculating vertical velocity from divergence of horizontal mass transports.''')
  parser.add_argument('infile', type=str, help='''Daily file containing ssu,ssv.''')
  parser.add_argument('--uname', type=str, default='umo', help='''Name of the u-component of mass transport''')
  parser.add_argument('--vname', type=str, default='vmo', help='''Name of the v-component of mass transport''')
  parser.add_argument('--wrapx', type=bool, default=True, help='''True if the x-component is reentrant''')
  parser.add_argument('--wrapy', type=bool, default=False, help='''True if the y-component is reentrant''')
  parser.add_argument('--gridspec', type=str, default ='',
    help='''File containing variables wet,areacello. Usually the ocean_static.nc from diag_table.''')
  parser.add_argument('--plot', type=bool, default=False, help='''Plot w at the 8th interface (kind of random)''')
  cmdLineArgs = parser.parse_args()

  # Check for presence of variables
  rootGroup = netCDF4.Dataset( cmdLineArgs.infile )
  if cmdLineArgs.uname not in rootGroup.variables:
    raise Exception('Could not find "%s" in file "%s"' % (cmdLineArgs.uname, cmdLineArgs.infile))
  if cmdLineArgs.vname not in rootGroup.variables:
    raise Exception('Could not find "%s" in file "%s"' % (cmdLineArgs.vname, cmdLineArgs.infile))

  u_var = netCDF4.Dataset(cmdLineArgs.infile).variables[cmdLineArgs.uname]
  v_var = netCDF4.Dataset(cmdLineArgs.infile).variables[cmdLineArgs.vname]

  w = calc_w_from_convergence( u_var, v_var,
                               cmdLineArgs.wrapx, cmdLineArgs.wrapy )
  if len(cmdLineArgs.gridspec) > 0:
    area = netCDF4.Dataset(cmdLineArgs.gridspec).variables['areacello'][:,:]
    w = w/(area*1035.0)
  # Plot if requested
  if cmdLineArgs.plot:
    import matplotlib.pyplot as plt
    plt.pcolormesh(w[0,7,:,:],vmin=-2e-5,vmax=2e-5,cmap=plt.cm.coolwarm)
    plt.colorbar()
    plt.show()

