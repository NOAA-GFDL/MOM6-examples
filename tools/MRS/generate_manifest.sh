#!/bin/bash

# Generates Makefile rules to set NPES macro for experiments
# Usage:
#   bash generate_manifest.sh PATH_TO_MOM6_EXAMPLES [PATH_TO_EXLUDE_LIST]

if [[ "$#" -gt 2 ]]; then
  echo $0: Too many arguments
  exit 911
fi
if [[ "$#" -lt 1 ]]; then
  echo $0: Must specify path to configuration repository
  exit 999
fi
# Always works from top of MOM6-examples (first argument)
cd $1

# Path to exclude file
if [[ "$#" -gt 1 ]]; then
  EXCLUDED=$2
else
  EXCLUDED=tools/MRS/excluded-expts.txt
fi

expts=$(git ls-files **MOM_parameter_doc.layout | sed 's:/MOM_parameter_doc.layout::' | cat - ${EXCLUDED} | sort | uniq -u)

for e in $expts
do
  layout_file=${e}/MOM_parameter_doc.layout
  test -f $layout_file && \
    npi=$(egrep "^NIPROC = " $layout_file | awk '{print $3}') &&
    npj=$(egrep "^NJPROC = " $layout_file | awk '{print $3}') &&
    masktable=($(grep MASKTABLE $layout_file | grep -v 'MASKTABLE = "MOM_mask_table"' | sed 's/MASKTABLE = "[a-zA-Z_]*\.//;s/".*//;s/[\.x]/ /g'))
    if [[ "${#masktable}" -gt "0" ]]; then
      npes=$((${masktable[1]}*${masktable[2]}-${masktable[0]}))
    else
      npes=$((npi*npj))
    fi
    atmos_npes=$(grep atmos_npes $e/input.nml | sed 's/[a-zA-Z _=,]*//g')
    if [[ "${#atmos_npes}" -gt 0 ]]; then
      npes=$(($npes+$atmos_npes))
    fi
    echo ${e}/ocean.stats.%: NPES=$npes
    echo ${e}/01.ignore/ocean.stats.%: NPES=$npes
    echo ${e}/12.ignore/ocean.stats.%: NPES=$npes
    echo ${e}/02.ignore/ocean.stats.%: NPES=$npes
    if [[ "$npes" -gt "1" && "${#masktable}" -eq "0" && "${#atmos_npes}" -eq 0 ]]; then
      if [[ "$npes" -gt "15" ]]; then
        alt_npes=$(($npes-4))
      elif [[ "$npes" -gt "5" ]]; then
        alt_npes=$(($npes-2))
      else
        alt_npes=$(($npes-1))
      fi
      echo ${e}/ocean.stats.%: ALT_NPES=$alt_npes
    fi
  mom_memory_file=$e/MOM_memory.h
  test -f $mom_memory_file && \
    npi=$(egrep "define NIPROC_ " $mom_memory_file | sed 's:.*_ ::' | awk '{print $1}') &&
    npj=$(egrep "define NJPROC_ " $mom_memory_file | sed 's:.*_ ::' | awk '{print $1}') &&
    npes=$(($npi*$npj)) &&
    echo ${e}/ocean.stats.%: STATIC_NPES=$npes
done

echo "STATIC_OCEAN_ONLY = DOME nonBous_global benchmark double_gyre"
echo "RESTART_SKIP ?= circle_obcs|tracer_mixing|unit_test|mixed_layer_restrat_2d"
