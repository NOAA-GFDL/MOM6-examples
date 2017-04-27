#!/bin/bash

function run_test {
 # $1=executable_style, $2=n_cores, $3=expt_name
 here=`pwd`
 echo ; echo Running $3 with $2 core using $1 ...
 cd MOM6-examples/ocean_only/$3
 mkdir -p RESTART
 mpirun -n $2 $here/build/$1/MOM6 1> log 2> errlog
 if [ $? == 0 ]; then \
  echo "    ..." $3 completed successfully.
 else
  cat errlog ; exit 911
 fi
 cd $here
}

# Single-core tests with non-symmetric executable
run_test ocn 1 unit_tests
run_test ocn 1 double_gyre
run_test ocn 1 flow_downslope/layer
run_test ocn 1 flow_downslope/rho
run_test ocn 1 flow_downslope/sigma
run_test ocn 1 flow_downslope/z
run_test ocn 1 benchmark
run_test symocn 1 circle_obcs

# Checksum output
md5sum MOM6-examples/ocean_only/{*,*/*}/ocean.stats > stats.md5
echo ; echo Checksums
cat stats.md5

# Multi-core tests with symmetric executable
run_test symocn 1 unit_tests
run_test symocn 4 double_gyre
run_test symocn 2 flow_downslope/layer
run_test symocn 2 flow_downslope/rho
run_test symocn 2 flow_downslope/sigma
run_test symocn 2 flow_downslope/z
run_test symocn 4 benchmark
run_test symocn 4 circle_obcs

# Check that checksums match
md5sum -c stats.md5
