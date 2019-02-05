#!/bin/bash
echo "Building FMS library"
mkdir -p build/FMS && \
cd build/FMS && \
rm -f path_names && \
../../MOM6-examples/src/mkmf/bin/list_paths -l ../../MOM6-examples/src/FMS/{platform,include,memutils,constants,mpp,fms,time_manager,diag_manager,data_override,coupler/ensemble_manager.F90,axis_utils,horiz_interp,time_interp,astronomy,mosaic,random_numbers}  && \
../../MOM6-examples/src/mkmf/bin/mkmf -t ../../MOM6-examples/src/mkmf/templates/linux-ubuntu-trusty-gnu.mk -p libfms.a -c '-Duse_libMPI -Duse_netCDF -DSPMD -DUSE_LOG_DIAG_FIELD_INFO -DMAXFIELDMETHODS_=500 -Duse_AM3_physics' path_names && \
make -s NETCDF=3 REPRO=1 libfms.a
