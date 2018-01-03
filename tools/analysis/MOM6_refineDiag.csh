#!/bin/csh
#------------------------------------------------------------------------------
#  MOM6_refineDiag.csh
#
#  DESCRIPTION: This is a script that is inteded to drive all the
#               pre-postprocessing stages of data manipulations on analysis nodes.
#               It is intended to be called by FRE at the "refineDiag" stage
#               which happens just before the components are post processed by frepp.
#               To make this happen a path to the (would be) script should appear
#               in the <refineDiag> tag of the xmls, e.g.,
#      <refineDiag script="$(NB_ROOT)/mom6/tools/analysis/MOM6_refineDiag.csh"/>
#               Note that the above script should exist when frepp is called.
#               This could be achieved by cloning the mom6 git repo in the <csh> section of the setup block
#               in the corresponding the gfdl platfrom. E.g.,
#        <csh><![CDATA[
#           source $MODULESHOME/init/csh
#           module use -a /home/John.Krasting/local/modulefiles
#           module purge
#           module load jpk-analysis/0.0.4
#           module load $(FRE_VERSION)
###         The following clones the mom6 git repo which should contain all the pp scripts
#           setenv NBROOT /nbhome/$USER/$(FRE_STEM)$(DEBUGLEVEL)
#           mkdir -p $NBROOT
#           cd $NBROOT
#           #bronx-8
#           #git clone "http://gitlab.gfdl.noaa.gov/github_mirror/noaa-gfdl-mom6.git" mom6
#           #bronx-7 (due to a bug in interpreting : in the above command)
#           /home/Niki.Zadeh/bin/git_clone_mom6_fix.csh
#         ]]></csh>
#
#------------------------------------------------------------------------------
echo ""
echo "  -- begin MOM6_refineDiag.csh --  "
echo ""
#The mere existance of a refineDiag section in the xml pointing to any non-empty refineDiag
#script (as simple as doing a "echo" above)
#causes the history files to be unpacked by frepp in /ptmp/$USER/$ARCHIVE/$year.nc
#when the current year data lands on gfdl archive.
#
echo "  ---------- begin yearly analysis ----------  "
echo ""
#
#Generate this year's analysis figures based on the unpacked history files
#
#Niki: Note that here we do not have any FRE environment to /nbhome
#      NBROOT should be set as an environ vatiable at the setup in the xml
#      setenv NBROOT /nbhome/$USER/$(FRE_STEM)$(DEBUGLEVEL)
set src_dir=$NBROOT/mom6/tools/analysis
# The following variables are set by frepp, but frepp is not called yet at refineDiag stage of FRE workflow,
#  so we need to explicitly set them here
set descriptor = $name
set out_dir = $NBROOT                  #Niki: How can we set this to frepp analysisdir /nbhome
set yr1 = $oname
set yr2 = $oname
set databegyr = $oname
set dataendyr = $oname
set datachunk = 1
#Try setting fre version to the caller version
if ( ! $?FREVERSION ) set FREVERSION = fre
set fremodule = $FREVERSION
set freanalysismodule = fre-analysis/test

# make sure valid platform and required modules are loaded
if (`gfdl_platform` == "hpcs-csc") then
   source $MODULESHOME/init/csh
   module use -a /home/fms/local/modulefiles /usr/local/paida/Modules
   module purge
   module load $fremodule
   module load $freanalysismodule
   module load gcc
   module load netcdf/4.2
   module load python/2.7.3
else
   echo "ERROR: invalid platform"
   exit 1
endif

# check again?
if (! $?FRE_ANALYSIS_HOME) then
   echo "ERROR: environment variable FRE_ANALYSIS_HOME not set."
   exit 1
endif

#
#At this point of the FRE workflow we are in a /vftmp directory on an analysis node
#with all the history files for the current finished year ${yr1} unpacked and present
#
echo "We are inside the refineDiag script"
pwd
ls -l

set script_dir=${out_dir}/mom6/tools/analysis
#gcp does not preserve executable bit, re-set it in order to work after transfer
chmod +x $script_dir/*.py

set ocean_static_file = $yr1.ocean_static.nc
if ( -e $yr1.ocean_static_no_mask_table.nc ) set ocean_static_file = $yr1.ocean_static_no_mask_table.nc
set ocean_basin_file = $yr1.basin_codes.nc

#echo '====annual mean Eddy Kinetic Energy======'
#mkdir -p $out_dir/refineDiag_ocean_annual/EddyKineticEnergy
#$script_dir/EddyKineticEnergy.py  -g $ocean_static_file -o $out_dir/refineDiag_ocean_annual/EddyKineticEnergy/EKE_mean_${yr1}.png -l ${yr1} $yr1.ocean_daily.nc

echo '==== Offline Diagnostics ===='
$script_dir/refineDiag_ocean_month.py -b $ocean_basin_file -r $refineDiagDir $yr1.ocean_month.nc
$script_dir/refineDiag_ocean_month_z.py -b $ocean_basin_file -r $refineDiagDir -s ./ $yr1.ocean_month_z.nc
$script_dir/refineDiag_ocean_month_rho2.py -b $ocean_basin_file -r $refineDiagDir $yr1.ocean_month_rho2.nc
#$script_dir/calc_variance.py zos $yr1.ocean_daily.nc $refineDiagDir/$yr1.ocean_month_refined.nc

#-- Note: The calc_variance script pre-dated refineDiag efforts just prior to the start of the GFDL-CM4 DECK runs.
#         Based on the diag_table, it looks like the calc_variance script is no longer needed and is now commented out.
#         If it is reactivated, it should be called LAST, since it appends to the ocean_month_refined.nc file that is 
#         created first by the other scripts.

echo "  ---------- end yearly analysis ----------  "

echo "  -- end   MOM6_refineDiag.csh --  "

exit 0
