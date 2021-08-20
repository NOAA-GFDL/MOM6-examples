#!/bin/csh -fx

echo -n Started $0 in ; pwd

# Modules
source $MODULESHOME/init/csh
module use -a /home/fms/local/modulefiles
module unload python nco netcdf
module load python/2.7.12
module load netcdf/4.2 intel_compilers
module load nco/4.3.1
module load mpich2

# Installing this file avoids a slow and unreliable file server (that would otherwise be ftp'd from ftp.oce.orst.edu)
cp -n /archive/gold/datasets/obs/tpxo7_atlas_netcdf.tar.Z .
cp -n /archive/gold/datasets/CORE/PHC2_salx/PHC2_salx.2004_08_03.nc .
make OM4_025_preprocessing_geothermal/Makefile
(cd OM4_025_preprocessing_geothermal/ ; make convert_Davies_2013)
cp -n /archive/gold/datasets/obs/convert_Davies_2013/ggge20271-sup-0003-Data_Table1_Eq_lon_lat_Global_HF.csv OM4_025_preprocessing_geothermal/convert_Davies_2013/

# Work around for environment problem inside MIDAS
setenv PYTHONPATH $cwd/local/lib

# Run through the work flow
make
