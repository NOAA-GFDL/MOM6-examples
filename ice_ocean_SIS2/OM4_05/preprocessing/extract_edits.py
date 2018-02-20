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
       '''Extracts the recorded edits in a topogaphy file, if any.
        ''',
       epilog='Written by A.Adcroft, 2015.')
  parser.add_argument('topography_file', type=str,
                      help='netcdf file to read.')
  parser.add_argument('-o','--output', type=str,
                      nargs='?', default=' ',
                      help='Write list of edits to output file. If no output file is specified, edits are reported to the screen.')

  optCmdLineArgs = parser.parse_args()

  createGUI(optCmdLineArgs.topography_file, optCmdLineArgs.output)


def createGUI(fileName, outFile):

  # Open netcdf file
  try: rg = Dataset(fileName, 'r')
  except: error('There was a problem opening "'+fileName+'".')

  if not ( 'iEdit' in rg.variables and 'jEdit' in rg.variables and 'zEdit' in rg.variables):
    print fileName,'does not have any recorded edits'
    return

  iEdit = rg.variables['iEdit'][:]
  jEdit = rg.variables['jEdit'][:]
  zEdit = rg.variables['zEdit'][:]
  zEdit_units = rg.variables['zEdit'].units
  depths = numpy.zeros( zEdit.shape[0] )
  (nj,ni) = rg.variables['depth'].shape
  for n,(i,j) in enumerate(zip(iEdit, jEdit)):
    depths[n] = rg.variables['depth'][j,i]

  if outFile == ' ':
    print 'Edits apply to a dataset of dimensions %i x %i'%(ni,nj)
    for n,(i,j,oz,nz) in enumerate(zip(iEdit, jEdit, zEdit, depths)):
      print '%5i: i=%4i, j=%4i, old depth=%8.2f, new depth=%8.2f'%(n,i,j,oz,nz)

    return

  rg.close()

  rg = Dataset(outFile, 'w', format='NETCDF3_CLASSIC')

  nc_nEdits = rg.createDimension('nEdits', None)
  nc_iEdit = rg.createVariable('iEdit', 'i', ('nEdits',))
  nc_jEdit = rg.createVariable('jEdit', 'i', ('nEdits',))
  nc_zEdit = rg.createVariable('zEdit', 'i', ('nEdits',))
  nc_ni = rg.createVariable('ni', 'i')
  nc_nj = rg.createVariable('nj', 'i')

  nc_iEdit.long_name = 'i-index of edited data'
  nc_jEdit.long_name = 'j-index of edited data'
  nc_zEdit.long_name = 'New value of data'
  nc_zEdit.units = zEdit_units
  nc_ni.long_name = 'The size of the i-dimension of the dataset these edits apply to'
  nc_nj.long_name = 'The size of the j-dimension of the dataset these edits apply to'

  nc_ni[:] = ni
  nc_nj[:] = nj
  for n,(i,j,z) in enumerate(zip(iEdit, jEdit, depths)):
    nc_iEdit[n] = i
    nc_jEdit[n] = j
    nc_zEdit[n] = z

  rg.close()

# Invoke main()
if __name__ == '__main__': main()

