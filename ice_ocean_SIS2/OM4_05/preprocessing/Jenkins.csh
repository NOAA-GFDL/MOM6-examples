#!/bin/csh -fx

echo -n Started $0 in ; pwd

# Modules
source $MODULESHOME/init/csh
module use -a /home/fms/local/modulefiles
module unload python nco netcdf
module load python/2.7.3_workstation
module load netcdf/4.2 intel_compilers
module load nco/4.3.1
module load mpich2

# Installing this file avoids a slow and unreliable file server (that would otherwise be ftp'd from ftp.oce.orst.edu)
cp -n /archive/gold/datasets/obs/tpxo7_atlas_netcdf.tar.Z .
cp -n /archive/gold/datasets/obs/WOA05_pottemp_salt.nc .
cp -n /archive/gold/datasets/topography/{bedmap2.nc,GEBCO_08_v1.nc,IBCAO_V3_500m_RR.grd} .
cp -n /archive/mjh/gold/datasets/JRA55-do-suppl/woa13v2/woa13_decav_s_0-10m.mon_01v2.nc .
make OM4_05_preprocessing_geothermal/Makefile
(cd OM4_05_preprocessing_geothermal/ ; make convert_Davies_2013)
cp -n /archive/gold/datasets/obs/convert_Davies_2013/ggge20271-sup-0003-Data_Table1_Eq_lon_lat_Global_HF.csv OM4_05_preprocessing_geothermal/convert_Davies_2013/

# Work around for environment problem inside MIDAS
setenv PYTHONPATH $cwd/local/lib

# Run through the work flow
make
