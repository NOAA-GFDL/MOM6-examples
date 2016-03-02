#!/bin/csh

# -------------------------------------------------
#    Simple csh snippet to repair frepp analysis
#
#
#  Instructions:
#    1. Fill in ppDir, years, and chunk
#    2. Select either the 0.25 or 0.5 degree 
#       GRIDSPEC and WOA paths
#
# -------------------------------------------------

source $MODULESHOME/init/csh
module load python

set ppDir = ""  # e.g. include everything up to but not including the '/pp'
set yr1   = ""  # make sure it has 4 digits
set yr2   = ""  # make sure it has 4 digits
set chunk = ""  # e.g. '${chunk}' or '20yr'

# Settings for the 0.5 degree configuration
set GRIDSPEC = "/archive/gold/datasets/OM4_05/mosaic.v20151203.unpacked"
set WOA = "/archive/gold/datasets/OM4_05/obs/WOA05_ptemp_salt_annual.v2015.12.03.nc"

# Settings for the 0.25 degree configuration
# set GRIDSPEC = "/archive/gold/datasets/OM4_025/mosaic.v20140610.tar"
# set WOA = "/archive/gold/datasets/OM4_025/obs/WOA05_ptemp_salt_annual.v20150310.nc"


# No need to edit below this line
# -----------------------------------------------------------------------------

mkdir -p ../../../ocean_${yr1}-${yr2}/ptemp
./SST_bias_WOA05.py -w ${WOA} -g ${GRIDSPEC} -o ../../../ocean_${yr1}-${yr2}/ptemp -l ${yr1}-${yr2} ${ppDir}/pp/ocean_annual_z/av/annual_${chunk}/ocean_annual_z.${yr1}-${yr2}.ann.nc
./zonal_T_bias_WOA05.py -w ${WOA} -g ${GRIDSPEC} -o ../../../ocean_${yr1}-${yr2}/ptemp -l ${yr1}-${yr2} ${ppDir}/pp/ocean_annual_z/av/annual_${chunk}/ocean_annual_z.${yr1}-${yr2}.ann.nc
./depth_average_T_bias.py -zb 100 -w ${WOA} -g ${GRIDSPEC} -o ../../../ocean_${yr1}-${yr2}/ptemp -l ${yr1}-${yr2} ${ppDir}/pp/ocean_annual_z/av/annual_${chunk}/ocean_annual_z.${yr1}-${yr2}.ann.nc
./depth_average_T_bias.py -zb 300 -w ${WOA} -g ${GRIDSPEC} -o ../../../ocean_${yr1}-${yr2}/ptemp -l ${yr1}-${yr2} ${ppDir}/pp/ocean_annual_z/av/annual_${chunk}/ocean_annual_z.${yr1}-${yr2}.ann.nc
./depth_average_T_bias.py -zb 700 -w ${WOA} -g ${GRIDSPEC} -o ../../../ocean_${yr1}-${yr2}/ptemp -l ${yr1}-${yr2} ${ppDir}/pp/ocean_annual_z/av/annual_${chunk}/ocean_annual_z.${yr1}-${yr2}.ann.nc
./depth_average_T_bias.py -zb 2000 -w ${WOA} -g ${GRIDSPEC} -o ../../../ocean_${yr1}-${yr2}/ptemp -l ${yr1}-${yr2} ${ppDir}/pp/ocean_annual_z/av/annual_${chunk}/ocean_annual_z.${yr1}-${yr2}.ann.nc
./depth_average_T_bias.py -zt 2000 -zb 4000 -w ${WOA} -g ${GRIDSPEC} -o ../../../ocean_${yr1}-${yr2}/ptemp -l ${yr1}-${yr2} ${ppDir}/pp/ocean_annual_z/av/annual_${chunk}/ocean_annual_z.${yr1}-${yr2}.ann.nc
./depth_average_T_bias.py -zb 6500 -w ${WOA} -g ${GRIDSPEC} -o ../../../ocean_${yr1}-${yr2}/ptemp -l ${yr1}-${yr2} ${ppDir}/pp/ocean_annual_z/av/annual_${chunk}/ocean_annual_z.${yr1}-${yr2}.ann.nc


mkdir -p ../../../ocean_${yr1}-${yr2}/salinity
./SSS_bias_WOA05.py -w ${WOA} -g ${GRIDSPEC} -o ../../../ocean_${yr1}-${yr2}/salinity -l ${yr1}-${yr2} ${ppDir}/pp/ocean_annual_z/av/annual_${chunk}/ocean_annual_z.${yr1}-${yr2}.ann.nc
./zonal_S_bias_WOA05.py -w ${WOA} -g ${GRIDSPEC} -o ../../../ocean_${yr1}-${yr2}/salinity -l ${yr1}-${yr2} ${ppDir}/pp/ocean_annual_z/av/annual_${chunk}/ocean_annual_z.${yr1}-${yr2}.ann.nc


# -- This script may not work; different behavior on workstation vs. PAN
mkdir -p ../../../ocean_${yr1}-${yr2}/sections
./vertical_sections_annual_bias_WOA05.py -w ${WOA} -g ${GRIDSPEC} -o ../../../ocean_${yr1}-${yr2}/sections -l ${yr1}-${yr2} ${ppDir}/pp/ocean_annual_z/av/annual_${chunk}/ocean_annual_z.${yr1}-${yr2}.ann.nc


mkdir -p ../../../ocean_${yr1}-${yr2}/MOC
./meridional_overturning.py -g ${GRIDSPEC} -o ../../../ocean_${yr1}-${yr2}/MOC -l ${yr1}-${yr2} ${ppDir}/pp/ocean_annual_z/av/annual_${chunk}/ocean_annual_z.${yr1}-${yr2}.ann.nc


mkdir -p ../../../ocean_${yr1}-${yr2}/Hosoda_MLD
./MLD_003.py -g ${GRIDSPEC} -o ../../../ocean_${yr1}-${yr2}/Hosoda_MLD -l ${yr1}-${yr2} ${ppDir}/pp/ocean_monthly/ts/monthly/${chunk}/ocean_monthly.${yr1}01-${yr2}12.MLD_003.nc
if ($status != 0) echo '   --> Mixed Layer Depth analysis may only be available on 5-year chunks.'


mkdir -p ../../../ocean_${yr1}-${yr2}/heat_transport
./poleward_heat_transport.py -l ${yr1}-${yr2} -g ${GRIDSPEC} -o ../../../ocean_${yr1}-${yr2}/heat_transport -l ${yr1}-${yr2} ${ppDir}/pp/ocean_annual/av/annual_${chunk}/ocean_annual.${yr1}-${yr2}.ann.nc

# -- This script may not work; requires MIDAS build
mkdir -p ../../../ocean_${yr1}-${yr2}/heat_salt_0_300m
./TS_depth_integrals.py -r ${WOA} -s 0 -e 300 -g ${GRIDSPEC} -o ../../../ocean_${yr1}-${yr2}/heat_salt_0_300m -l ${yr1}-${yr2} ${ppDir}/ocean_annual.$yr1-$yr2.ann.nc
if ($status != 0) echo '   --> Script may have failed on the MIDAS dependency.'

#//
