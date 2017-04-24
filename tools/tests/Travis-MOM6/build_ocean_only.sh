#!/bin/bash
echo "Compiling non-symmetric MOM6"
mkdir -p build/ocn \
  && (cd build/ocn \
  && ../../MOM6-examples/src/mkmf/bin/list_paths ../../{config_src/dynamic,config_src/solo_driver,src/{*,*/*}}/ \
  && ../../MOM6-examples/src/mkmf/bin/mkmf -t ../../MOM6-examples/src/mkmf/templates/linux-gnu.mk -o '-I../FMS' -p MOM6 -l '-L../FMS -lfms' -c '-Duse_libMPI -Duse_netCDF -DSPMD -DUSE_LOG_DIAG_FIELD_INFO -DMAXFIELDMETHODS_=500 -Duse_AM3_physics' path_names \
  && make FC=mpif90 CC=mpicc LD=mpif90 NETCDF=3 REPRO=1 MOM6)

