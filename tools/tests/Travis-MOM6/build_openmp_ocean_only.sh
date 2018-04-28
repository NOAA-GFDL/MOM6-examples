#!/bin/bash -f
echo "Compiling symmetric MOM6 with OpenMP"
mkdir -p build/ompocn && \
cd build/ompocn && \
../../MOM6-examples/src/mkmf/bin/list_paths -l ../../{config_src/dynamic_symmetric,config_src/solo_driver,src/{*,*/*}}/ && \
../../MOM6-examples/src/mkmf/bin/mkmf -t ../../MOM6-examples/src/mkmf/templates/linux-ubuntu-trusty-gnu.mk -o '-I../FMS' -p MOM6 -l '-L../FMS -lfms' -c '-Duse_libMPI -Duse_netCDF -DSPMD -DUSE_LOG_DIAG_FIELD_INFO -DMAXFIELDMETHODS_=500 -Duse_AM3_physics' path_names && \
make -s NETCDF=3 REPRO=1 OPENMP=1 MOM6
