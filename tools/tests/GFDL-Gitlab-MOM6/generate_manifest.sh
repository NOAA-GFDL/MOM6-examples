#!/bin/bash

expts=$(find MOM6-examples -name ocean.stats.gnu -printf "%h\n")

for e in $expts
do
  layout_file=$e/MOM_parameter_doc.layout
  test -f $layout_file && \
    npi=$(egrep "^NIPROC = " $layout_file | awk '{print $3}') &&
    npj=$(egrep "^NJPROC = " $layout_file | awk '{print $3}') &&
    masktable=($(grep MASKTABLE $layout_file | grep -v 'MASKTABLE = "MOM_mask_table"' | sed 's/MASKTABLE = "[a-zA-Z_]*\.//;s/".*//;s/[\.x]/ /g'))
    if [[ "${#masktable}" -gt "0" ]]; then
      npes=$((${masktable[1]}*${masktable[2]}-${masktable[0]}))
    else
      npes=$(($npi*$npj))
    fi
    atmos_npes=$(grep atmos_npes $e/input.nml | sed 's/[a-zA-Z _=,]*//g')
    if [[ "${#atmos_npes}" -gt 0 ]]; then
      npes=$(($npes+$atmos_npes))
    fi
    echo $e/ocean.stats.%: NPES=$npes
    if [[ "$npes" -gt "1" && "${#masktable}" -eq "0" && "${#atmos_npes}" -eq 0 ]]; then
      alt_npes=$(($npes-1))
      echo $e/ocean.stats.%: ALT_NPES=$alt_npes
    fi
  mom_memory_file=$e/MOM_memory.h
  test -f $mom_memory_file && \
    npi=$(egrep "define NIPROC_ " $mom_memory_file | sed 's:.*_ ::' | awk '{print $1}') &&
    npj=$(egrep "define NJPROC_ " $mom_memory_file | sed 's:.*_ ::' | awk '{print $1}') &&
    npes=$(($npi*$npj)) &&
    echo $e/ocean.stats.%: STATIC_NPES=$npes
done

echo "STATIC_OCEAN_ONLY =" `find MOM6-examples/ocean_only -type d -exec bash -c '[ -f "$0"/MOM_memory.h ] && [ -f "$0"/ocean.stats.gnu ]' '{}' \; -print`
