#!/usr/bin/env python

# Imports
try: import argparse
except: error('This version of python is not new enough. python 2.7 or newer is required.')
try: from netCDF4 import Dataset
except: error('Unable to import netCDF4 module. Check your PYTHONPATH.\n'
          +'Perhaps try:\n   module load python_netcdf4')
try: import numpy
except: error('Unable to import numpy module. Check your PYTHONPATH.\n'
          +'Perhaps try:\n   module load python_numpy')

def main():

  # Command line arguments
  parser = argparse.ArgumentParser(description=
       '''Applies list of topography edits from one file to a topography file.
        ''',
       epilog='Written by A.Adcroft, 2015.')
  parser.add_argument('edits_file', type=str,
                      help='netcdf file with list of edits.')
  parser.add_argument('topography_file', type=str,
                      help='netcdf file of topography to update.')

  optCmdLineArgs = parser.parse_args()

  createGUI(optCmdLineArgs.edits_file, optCmdLineArgs.topography_file)

def createGUI(edits_file, topo_file, var='depth'):

  # Open netcdf file with list of edits
  try: rge = Dataset(edits_file, 'r')
  except: error('There was a problem opening "'+edits_file+'".')

  if not ( 'iEdit' in rge.variables and 'jEdit' in rge.variables and 'zEdit' in rge.variables):
    print edits_file,'does not have any recorded edits'
    return

  try:
    iEdit = rge.variables['iEdit'][:]
    jEdit = rge.variables['jEdit'][:]
    zEdit = rge.variables['zEdit'][:]
    zEdit_units = rge.variables['zEdit'].units
    eni = rge.variables['ni'][:]
    enj = rge.variables['nj'][:]
    rge.close()
  except: raise Exception('There was a problem reading '+edits_file)

  rg = Dataset(topo_file, 'r+')

  # Sanity check
  if rg.variables[var].units != zEdit_units: raise Exception('Units mismatch!')
  if rg.variables[var].shape[0] != enj: raise Exception('j-dimension mismatch!')
  if rg.variables[var].shape[1] != eni: raise Exception('i-dimension mismatch!')

  depth = -rg.variables[var][:,:]

  if ( 'iEdit' in rg.variables and 'jEdit' in rg.variables and 'zEdit' in rg.variables):
    # Undo existing edits
    for n,(i,j,z) in enumerate(zip(rg.variables['iEdit'][:], rg.variables['jEdit'][:], rg.variables['zEdit'][:])):
      depth[j,i] = z
  else:
    # Create new edit variables
    rg.createDimension('nEdits', None)
    nc_iEdit = rg.createVariable('iEdit', 'i', ('nEdits',))
    nc_jEdit = rg.createVariable('jEdit', 'i', ('nEdits',))
    nc_zEdit = rg.createVariable('zEdit', 'f', ('nEdits',))
    nc_iEdit.long_name = 'i-index of edited data'
    nc_jEdit.long_name = 'j-index of edited data'
    nc_zEdit.long_name = 'Original value of edited data'
    nc_zEdit.units = zEdit_units

  n = rg.variables['iEdit'].shape[0]
  if n > zEdit.shape[0]:
    raise Exception('List of existing edits are longer than list of new edits')

  # Apply edits
  old_depths = numpy.zeros( zEdit.shape[0] )
  for n,(i,j,z) in enumerate(zip(iEdit, jEdit, zEdit)):
    old_depths[n] = depth[j,i]
    depth[j,i] = z

  # zero out land points
  depth[depth<0.]=0.
  rg.variables[var][:] = depth
  rg.variables['iEdit'][:] = iEdit
  rg.variables['jEdit'][:] = jEdit
  rg.variables['zEdit'][:] = old_depths


  rg.close()

# Invoke main()
if __name__ == '__main__': main()

