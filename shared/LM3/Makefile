# Configuration
BUILD ?= build
FMS_BUILD ?= ../fms/build

LM3_SRC ?= ../../src/LM3

TARGET = libLM3.a
CODEBASE = ../../src/LM3
CONFIGURE_AC = ../config/configure.LM3.ac
M4DIR = ../../src/MOM6/ac/deps/m4

FCFLAGS += -I$(abspath $(FMS_BUILD))
LDFLAGS += -L$(abspath $(FMS_BUILD))

include ../config/Libs.mk

#----
# External Codebase
# NOTE: These are only visible within the GFDL firewall

$(BUILD)/configure: | $(LM3_SRC)

$(LM3_SRC):
	mkdir -p $@
	git -C $@ clone http://gitlab.gfdl.noaa.gov/fms/land_param.git
	git -C $@/land_param checkout xanadu
	git -C $@ clone http://gitlab.gfdl.noaa.gov/fms/land_lad2.git
	git -C $@/land_lad2 checkout verona_201701
	find $@/land_lad2 -type f -name \*.F90 \
	  -exec cpp -Duse_libMPI -Duse_netCDF -DSPMD -Duse_LARGEFILE -C -nostdinc -v -I ../../src/FMS/include -o '{}'.cpp {} \;
	find $@/land_lad2 -type f -name \*.F90.cpp -exec rename .F90.cpp .f90 {} \;
	find $@/land_lad2 -type f -name \*.F90 -exec rename .F90 .F90_preCPP {} \;
