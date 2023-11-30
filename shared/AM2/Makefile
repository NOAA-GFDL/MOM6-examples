# Configuration
BUILD ?= build
FMS_BUILD ?= ../fms/build

TARGET = libAM2.a
CODEBASE = ../../src/AM2
CONFIGURE_AC = ../config/configure.AM2.ac
M4DIR = ../../src/MOM6/ac/deps/m4
SRCDIRS = $(addprefix $(abspath $(CODEBASE))/, \
  $(addprefix atmos_fv_dynamics/,driver/coupled model tools) \
  atmos_drivers/coupled \
  atmos_shared_am3 \
  atmos_param_am3)

CPPFLAGS += -Duse_AM3_physics -DSPMD

FCFLAGS += -I$(abspath $(FMS_BUILD))
FCFLAGS += -I$(abspath ../../src/FMS/include)

LDFLAGS += -L$(abspath $(FMS_BUILD))

include ../config/Libs.mk

#----
# External Codebase
# NOTE: These are only visible within the GFDL firewall

$(BUILD)/configure: | $(CODEBASE)

$(CODEBASE):
	mkdir -p $@
	git -C $@ clone http://gitlab.gfdl.noaa.gov/fms/atmos_shared_am3.git
	git -C $@/atmos_shared_am3 checkout warsaw_201803
	git -C $@ clone http://gitlab.gfdl.noaa.gov/fms/atmos_drivers.git
	git -C $@/atmos_drivers checkout warsaw_201803
	git -C $@ clone http://gitlab.gfdl.noaa.gov/fms/atmos_fv_dynamics.git
	git -C $@/atmos_fv_dynamics checkout warsaw_201803
	git -C $@ clone http://gitlab.gfdl.noaa.gov/fms/atmos_param_am3.git
	git -C $@/atmos_param_am3 checkout warsaw_201803
