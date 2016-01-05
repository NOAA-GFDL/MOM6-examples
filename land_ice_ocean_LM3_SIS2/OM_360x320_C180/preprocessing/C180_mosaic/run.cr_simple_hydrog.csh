#!/bin/csh -f
#----------------------------------
#PBS -N cr_simple_hydrog
#PBS -l size=1
#PBS -l walltime=02:00:00
#PBS -r y
#PBS -j oe
#PBS -o $HOME
#PBS -q batch
#----------------------------------

# =========================================================================
#   script creates a simple hydrography, with no manual intervention,
#     simplified lake fields, no elevation
#    -- run river_regrid tool
#    -- run post-processor on river_regrid output
#    -- remove parallel rivers
#    -- run post-processor again
#    -- add GLCC waterbod fractions
# =========================================================================

#set echo on
#wipeftmp

if (`gfdl_platform` == "hpcs-csc") then
    source $MODULESHOME/init/csh
    module purge
    module load gcp
    module load netcdf/4.2
    module load nco/4.3.1 
    module load ifort/11.1.073
    module load icc/11.1.073
    module load mpich2/1.2.1p1
    alias gmake gmake -j 8
else
   echo "ERROR: invalid platform"
   exit
endif

set outdir = ""
set argv = (`getopt  hc:o:f:t:m: $*`)

while ("$argv[1]" != "--")
    switch ($argv[1])
        case -h:
            set help; breaksw
        case -o:
            set outdir = $argv[2]; shift argv; breaksw
        case -c:
            set compile = $argv[2]; shift argv; breaksw
        case -f:
            set min_frac = $argv[2]; shift argv; breaksw
        case -t:
            set land_thresh = $argv[2]; shift argv; breaksw
        case -m:
            set mosaic_file = $argv[2]; shift argv; breaksw
    endsw
    shift argv
end
shift argv

# argument error checking

if (! $?min_frac) then
   echo "ERROR: no argument given for min_frac (river_regrid)."
   set help
endif

if (! $?land_thresh) then
   echo "ERROR: no argument given for land_thresh (river_regrid)."
   set help
endif

if (! $?mosaic_file) then
   echo "ERROR: no argument given for mosaic_file."
   set help
endif

if (! $?compile) then
   echo "NOTE: no argument given for compile: default is to use previously compiled executables "
   echo " "
   set compile = " "
endif


# usage message
if ($?help) then
   set cmdname = `basename $0`
   echo
   echo "USAGE:  $cmdname [-f min_frac] [-t land_thresh] [-m mosaic] [-c compile] [-o outdir]"
   echo
   echo "         -f min_frac:    required, river-regrid, min land fraction; set to 0 to retain small "
   echo "                         land fractions from gridspec"
   echo "         -t land_thresh: required, river-regrid, land fraction exceeding (1-land_thresh) is set to 1;"
   echo "                         recommend 1.e-5"
   echo "         -m mosaic:      required, mosaic file location"
   echo "         -c compile:     use '-c compile' to compile code (optional)"
   echo "         -o outdir:      output directory (optional)"
   echo
   exit 1
endif


set home_dir         = /home/kap/lmdt/tools/simple_hydrog/
set fms_code_dir     = /home/kap/lmdt/analysis/diag3_bronx3/shared/code_siena_201211

set riv_regrd        = /home/Zhi.Liang/bin/tools_20130912/river_regrid              # set path to Zhi's river_regrid tool
set postp_code_path  = $home_dir/code/cp_river_vars.f90
set rmvpr_code_path  = $home_dir/code/rmv_parallel_rivers.f90
set lakes_code_path  = $home_dir/code/path_names_lakes_siena201211

set compile_template = $home_dir/code/TEMPLATE_siena_201211_b3

# set path for the disaggregated, extended river network
set river_network_ext_file = /archive/kap/lmdt/river_network/netcdf/0.5deg/disagg/river_network_mrg_0.5deg_ad3nov_fill_coast_auto1_0.125.nc

# set path for GLCC data (waterbod)
set glcc_file = /archive/pcm/land_data/cover_lad/gigbp2_0ll.nc



if (! -d work) mkdir work
set WORKDIR = `pwd`/work
cd $WORKDIR

mkdir -p EXEC/{postp,rmvpr,lakes}
mkdir -p OUTPUT/{river_regrid,post_regrid,rmv_parallel_rivers,post_rmvp}
mkdir DATA

if ($compile == "compile") then
# ------------------------------------------------
#  COMPILE FORTRAN PROGRAMS
# ------------------------------------------------
    gcp -v $compile_template $WORKDIR/EXEC/
    gcp -v $postp_code_path $WORKDIR/EXEC/postp/
    cd EXEC/postp/
    /home/fms/bin/mkmf -p cp_rvar -t $WORKDIR/EXEC/$compile_template:t $postp_code_path:t
    gmake
    if ($status != 0) then
        echo compile of post-processor code failed, exiting...
        exit
    endif
    cd $WORKDIR

    gcp -v $rmvpr_code_path $WORKDIR/EXEC/rmvpr/
    cd EXEC/rmvpr/
    /home/fms/bin/mkmf -p rmvp -t $WORKDIR/EXEC/$compile_template:t $rmvpr_code_path:t
    gmake
    if ($status != 0) then
        echo compile of remove-parallel-rivers code failed, exiting...
        exit
    endif
    cd $WORKDIR

    gcp -v $lakes_code_path $WORKDIR/EXEC/lakes/
    cd EXEC/lakes/
    /home/fms/bin/mkmf -p cplf -t $WORKDIR/EXEC/$compile_template:t -c "-Duse_netCDF" \
          $lakes_code_path:t -c $fms_code_dir/shared/include /usr/local/include
    gmake
    if ($status != 0) then
        echo compile of lakes code failed, exiting...
        exit
    endif
    cd $WORKDIR
else
    gcp -v $home_dir/exec/postp/cp_rvar $WORKDIR/EXEC/postp/
    gcp -v $home_dir/exec/rmvpr/rmvp    $WORKDIR/EXEC/rmvpr/
    gcp -v $home_dir/exec/lakes/cplf    $WORKDIR/EXEC/lakes/
    chmod ugo+x $WORKDIR/EXEC/postp/cp_rvar $WORKDIR/EXEC/rmvpr/rmvp $WORKDIR/EXEC/lakes/cplf
endif

dmget $river_network_ext_file


# ------------------------------------------------
#  RUN RIVER_REGRID
# ------------------------------------------------
echo ""
echo RUN RIVER-REGRID
$riv_regrd --mosaic $mosaic_file --river_src $river_network_ext_file --min_frac $min_frac --land_thresh $land_thresh
mv river_output*nc OUTPUT/river_regrid/


# ------------------------------------------------
#  POST-PROCESS OUTPUT FROM RIVER_REGRID
# ------------------------------------------------
set river_input_files = OUTPUT/river_regrid/river_output*nc 
echo $#river_input_files > fort.5
foreach file ($river_input_files)
   echo OUTPUT/river_regrid/$file:t >> fort.5
end
echo ""
echo RUN POST-PROCESSOR
$WORKDIR/EXEC/postp/cp_rvar < fort.5
if ($status != 0) then
    echo ERROR in post-processing river-regrid output, exiting...
    exit
else
    mv river_network*nc OUTPUT/post_regrid/
    mv out.cp_river_vars OUTPUT/post_regrid/
endif


# ------------------------------------------------
#  REMOVE PARALLEL RIVERS
# ------------------------------------------------
set add_ocean_const = F

set river_input_files = OUTPUT/post_regrid/river_network*nc
echo $#river_input_files > fort.5
foreach file ($river_input_files)
   echo OUTPUT/post_regrid/$file:t >> fort.5
end
echo $add_ocean_const >> fort.5
echo ""
echo REMOVE PARALLEL RIVERS
$WORKDIR/EXEC/rmvpr/rmvp < fort.5
if ($status != 0) then
    echo ERROR in removal of parallel rivers, exiting...
    exit
else
    mv river_network*nc OUTPUT/rmv_parallel_rivers/
    mv out.rmv_parallel_rivers OUTPUT/rmv_parallel_rivers/
endif


# ------------------------------------------------
#  POST-PROCESS OUTPUT FROM REMOVE-PARALLEL-RIVERS
# ------------------------------------------------
set river_input_files = OUTPUT/rmv_parallel_rivers/river_network*nc
echo $#river_input_files > fort.5
foreach file ($river_input_files)
   echo OUTPUT/rmv_parallel_rivers/$file:t >> fort.5
end
echo ""
echo RUN POST-PROCESSOR
$WORKDIR/EXEC/postp/cp_rvar < fort.5
if ($status != 0) then
    echo ERROR in post-processing parallel-river output, exiting...
    exit
else
    mv river_network*nc OUTPUT/post_rmvp/
    mv out.cp_river_vars OUTPUT/post_rmvp/
endif


# --------------------------------------
#  ADD GLCC WATERBOD DATA
# --------------------------------------
set travel_thresh = 2.

dmget $glcc_file
gcp -v gfdl:$glcc_file   gfdl:$WORKDIR/DATA/
set river_input_files = OUTPUT/post_rmvp/river_network*nc
echo $#river_input_files > fort.5
foreach file ($river_input_files)
   echo OUTPUT/post_rmvp/$file:t >> fort.5
end
echo DATA/$glcc_file:t >> fort.5
echo $travel_thresh >> fort.5
touch input.nml
echo ""
echo ADD LAKES
$WORKDIR/EXEC/lakes/cplf < fort.5
if ($status != 0) then
    echo ERROR in addition of lake data, exiting...
    exit
endif

@ k = 0
while ($k < $#river_input_files)
  @ k = $k + 1
  gcp OUTPUT/post_rmvp/river_network.tile"$k".nc $WORKDIR/hydrography.tile"$k".nc
end
set hydro_files = hydrography*.nc
foreach file ($hydro_files)
   set tn = `echo "$file" | awk -Ftile '{print $2}'`
   ncks -A -a -v lake_frac,lake_depth_sill,lake_tau,WaterBod,PWetland,connected_to_next,whole_lake_area,max_slope_to_next \
     lake_frac.tile"$tn" "$file:t"
end

if ($outdir != "") then
    gcp -v hydrography.tile*nc $outdir/
endif


