#!/bin/bash

# Usage: setup_restart_test.sh <path_to_expt>
cd $1

# Scan experiment
DT=`grep "^DT =" MOM_parameter_doc.all | sed 's/\!.*//;s/ //g;s/.*=//'`
DT_FORCING=`grep "^DT_FORCING =" MOM_parameter_doc.all | sed 's/\!.*//;s/ //g;s/.*=//'`
INPUT_DAYS=`grep -i days input.nml | sed 's/\!.*//;s/ //g;s/.*=//;s/,.*//'`
INPUT_HOURS=`grep -i hours input.nml | sed 's/\!.*//;s/ //g;s/.*=//;s/,.*//'`
TIMEUNIT=`grep "^TIMEUNIT =" MOM_parameter_doc.all | sed 's/\!.*//;s/ //g;s/.*=//'`
DAYMAX=`grep DAYMAX MOM_parameter_doc.all | sed 's/\!.*//;s/ //g;s/.*=//'`
SAVEDAYS=`grep ENERGYSAVEDAYS MOM_parameter_doc.all | sed 's/\!.*//;s/ //g;s/.*=//'`
if [[ "$DT_FORCING" == *"E"* ]]; then
 DT_FORCING=`echo ${DT_FORCING/E+/\*10^} | bc`
fi
if [ ! -z $INPUT_DAYS ]; then
  TIMEUNIT=86400.
# HALF_DAYMAX=1.
# DOUBLE_DAYMAX=2.
# SAVEDAYS=0.5
# HALF_DAYS=1
# DOUBLE_DAYS=2
  HALF_DAYMAX=1.
  DOUBLE_DAYMAX=2.
  SAVEDAYS=0.25
  HALF_DAYS=0
  DOUBLE_DAYS=0
  HALF_HOURS=6
  DOUBLE_HOURS=12
else
  TIMEUNIT=1.
  HALF_DAYMAX=`echo $DT_FORCING\*2 | bc`
  DOUBLE_DAYMAX=`echo $DT_FORCING\*4 | bc`
  SAVEDAYS=$DT
fi

shopt -s nullglob

# Create full length test
mkdir -p 02.ignore
cd 02.ignore
test -d ../INPUT && ln -sf ../INPUT .
cp -f ../MOM_* ../*table ../input.nml .
test -e ../isopyc_coords.nc && cp -f ../isopyc_coords.nc .
sed -i "/^DAYMAX/d" MOM_input; echo "DAYMAX=$DOUBLE_DAYMAX" >> MOM_input
sed -i "/^TIMEUNIT/d" MOM_input; echo TIMEUNIT=1. >> MOM_input
sed -i "/^ENERGYSAVEDAYS/d" MOM_input; echo "ENERGYSAVEDAYS=$DT" >> MOM_input
[[ ! -z $INPUT_DAYS ]] && sed -i "/days/c days=$DOUBLE_DAYS," input.nml
[[ ! -z $INPUT_HOURS ]] && sed -i "/hours/c hours=$DOUBLE_HOURS," input.nml
test -f ../SIS_input && cp ../SIS_* .
sed -i "s/'n'/'F'/g" input.nml

# Create first half test
mkdir -p ../01.ignore
cd ../01.ignore
test -d ../INPUT && ln -sf ../INPUT .
cp -f ../MOM_* ../*table ../input.nml .
test -e ../isopyc_coords.nc && cp -f ../isopyc_coords.nc .
sed -i "/^DAYMAX/d" MOM_input; echo "DAYMAX=$HALF_DAYMAX" >> MOM_input
sed -i "/^TIMEUNIT/d" MOM_input; echo TIMEUNIT=1. >> MOM_input
sed -i "/^ENERGYSAVEDAYS/d" MOM_input; echo "ENERGYSAVEDAYS=$DT" >> MOM_input
sed -i "/^RESTART_CONTROL/d" MOM_input; echo "RESTART_CONTROL=1" >> MOM_input
[[ ! -z $INPUT_DAYS ]] && sed -i "/days/c days=$HALF_DAYS," input.nml
[[ ! -z $INPUT_HOURS ]] && sed -i "/hours/c hours=$HALF_HOURS," input.nml
test -f ../SIS_input && cp ../SIS_* .
sed -i "s/'n'/'F'/g" input.nml

# Create second half test
mkdir -p ../12.ignore
cd ../12.ignore
test -d ../INPUT && mkdir -p INPUT && ( cd INPUT && ln -sf ../../INPUT/* . )
cp -f ../MOM_* ../*table ../input.nml .
test -e ../isopyc_coords.nc && cp -f ../isopyc_coords.nc .
sed -i "/^DAYMAX/d" MOM_input; echo "DAYMAX=$DOUBLE_DAYMAX" >> MOM_input
sed -i "/^TIMEUNIT/d" MOM_input; echo TIMEUNIT=1. >> MOM_input
sed -i "/^ENERGYSAVEDAYS/d" MOM_input; echo "ENERGYSAVEDAYS=$DT" >> MOM_input
[[ ! -z $INPUT_DAYS ]] && sed -i "/days/c days=$HALF_DAYS," input.nml
[[ ! -z $INPUT_HOURS ]] && sed -i "/hours/c hours=$HALF_HOURS," input.nml
test -f ../SIS_input && cp ../SIS_* .
sed -i "s/'n'/'F'/g" input.nml
sed -i "/restart_input_dir/c restart_input_dir='INPUT/', " input.nml

echo ${1}:: DAYMAX=$DAYMAX, days=$INPUT_DAYS, hours=$INPUT_HOURS, timeunit=$TIMEUNIT, dt=$DT, dt_forcing=$DT_FORCING, 01=$HALF_DAYMAX, 02=$DOUBLE_DAYMAX
