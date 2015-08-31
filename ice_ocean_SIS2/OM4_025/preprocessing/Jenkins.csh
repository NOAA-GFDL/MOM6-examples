#!/bin/csh -fx

echo -n Started $0 in ; pwd

# Modules
source $MODULESHOME/init/csh
module use -a /home/fms/local/modulefiles
module load python
module load netcdf/4.2 intel_compilers
module load nco/4.3.1
module load mpich2

# Installing this file avoids a slow and unreliable file server (that would otherwise be ftp'd from ftp.oce.orst.edu)
cp -n /archive/gold/datasets/obs/tpxo7_atlas_netcdf.tar.Z .

# Work around for environment problem inside MIDAS
setenv PYTHONPATH $cwd/local/lib

# Run through the work flow
make
