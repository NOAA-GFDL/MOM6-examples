#!/usr/bin/env python

import argparse
import m6toolbox
import netCDF4 as nc
import numpy as np
import os
import shutil
import sys

'''
Script to add the CF varaible 'basin' to an existing ocean_static.nc file
'''

def run():
    parser = argparse.ArgumentParser(description='''Script to append basin mask to static file''')
    parser.add_argument('infile', type=str, help='''Input file''')
    parser.add_argument('-o','--outfile', type=str, default=None, help='''Output file name''')
    parser.add_argument('-v',dest='verbose', action='store_true', default=False, help='''Verbose output''')
    args = parser.parse_args()
    main(args)


def main(args):
    f = nc.Dataset(args.infile)
    
    if 'basin' in f.variables.keys():
      sys.stdout.write('The basin field already appears to be in the static file.  Exiting.')
      exit(1)

    if args.outfile is None:
        outfile = os.path.basename(args.infile)
        outfile = outfile.split('.')
        outfile.insert(-1,'basins')
        outfile = str('.').join(outfile)
    else:
        outfile = args.outfile

    if os.path.exists(outfile):
        sys.stdout.write('File already exists ... would you like to overwrite? (y/n): ')
        choice = raw_input().lower()
        if choice == 'y':
            if args.verbose:
                sys.stdout.write('Overwriting file: '+outfile+'\n')
        elif choice == 'n':
            exit(1)
        else:
            sys.stdout.write('Please respond with \'y\' or \'n\'')

    geolon = np.array(f.variables['geolon'][:])
    geolat = np.array(f.variables['geolat'][:])
    deptho = np.array(f.variables['deptho'][:].filled(0))
    basin_code = m6toolbox.genBasinMasks(geolon, geolat, deptho, args.verbose)

    shutil.copyfile(args.infile,outfile)

    nc_out = nc.Dataset(outfile,'r+',format='NETCDF3_CLASSIC')
    basin_out = nc_out.createVariable('basin', np.int32, ('yh', 'xh'))

    basin_out.setncattr('long_name','Region Selection Index')
    basin_out.setncattr('standard_name','region')
    basin_out.setncattr('units','1.0')
    basin_out.setncattr('interp_method','none')
    basin_out.setncattr('flag_values','0 1 2 3 4 5 6 7 8 9 10')
    basin_out.setncattr('flag_meanings','global_land southern_ocean atlantic_ocean pacific_ocean '+\
                        'arctic_ocean indian_ocean mediterranean_sea black_sea hudson_bay baltic_sea red_sea')
    
    basin_out[:] = basin_code[:]

    nc_out.close()

    exit(0)


if __name__ == '__main__':
  run()
