# Build configuration
BUILD ?= build
MOM_MEMORY ?=
SIS_MEMORY ?=

# Dependencies
FMS_BUILD ?= ../shared/fms/build
ICEBERGS_BUILD ?= ../shared/icebergs/build
ICE_PARAM_BUILD ?= ../shared/ice_param/build
ATMOS_BUILD ?= ../shared/atmos_null/build
LAND_BUILD ?= ../shared/land_null/build

# Autoconf configuration
MOM_CODEBASE ?= ../src/MOM6
MAKEFILE_IN ?= $(MOM_CODEBASE)/ac/Makefile.in
CONFIGURE_AC ?= ../ac/configure.ice_ocean.ac
M4DIR ?= $(MOM_CODEBASE)/ac/m4
MAKEDEP ?= $(MOM_CODEBASE)/ac/makedep

# Run configuration
EXPT ?=
OUTPUT ?= ./$(EXPT)
LAUNCHER ?= mpirun
# The following runs do not appear to work
EXCLUDE ?= \
  OM4_025.JRA \
  SIS2_icebergs \
  SIS2_bergs_cgrid

# Autoconf setup
EXTRA_SRC_DIRS := \
  $(abspath ../src/SIS2/src) \
  $(abspath ../src/SIS2/config_src/external) \
  $(abspath ../src/coupler)

CONFIG_FLAGS := --config-cache
CONFIG_FLAGS += --srcdir=$(abspath $(MOM_CODEBASE))
CONFIG_FLAGS += --with-driver=FMS_cap
ifdef MOM_MEMORY
  CONFIG_FLAGS += MOM_MEMORY=$(abspath $(MOM_MEMORY))
endif
ifdef SIS_MEMORY
  CONFIG_FLAGS += SIS_MEMORY=$(abspath $(SIS_MEMORY))
endif

# `export` disables autoconf defaults; this restores them
CFLAGS ?= -g -O2
FCFLAGS ?= -g -O2

MOM_FCFLAGS := $(FCFLAGS) \
  -I$(abspath $(FMS_BUILD)) \
  -I$(abspath $(ICEBERGS_BUILD)) \
  -I$(abspath $(ICE_PARAM_BUILD)) \
  -I$(abspath $(ATMOS_BUILD)) \
  -I$(abspath $(LAND_BUILD))

MOM_LDFLAGS := $(LDFLAGS) \
  -L$(abspath $(FMS_BUILD)) \
  -L$(abspath $(ICEBERGS_BUILD)) \
  -L$(abspath $(ICE_PARAM_BUILD)) \
  -L$(abspath $(ATMOS_BUILD)) \
  -L$(abspath $(LAND_BUILD))

# Pass autoconf environment variables to submakes
export CPPFLAGS
export CC
export MPICC
export CFLAGS
export FC
export MPIFC
export FCFLAGS
export LDFLAGS
export LIBS
export PYTHON
export EXTRA_SRC_DIRS


# Makefile configuration

# Verify that BUILD is not set to the current directory
# (which would clobber this Makefile)
MAKEPATH = $(realpath $(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
ifeq ($(MAKEPATH), $(realpath $(BUILD)))
  $(error BUILD cannot be set to the current directory)
endif

# Disable builtin rules and variables
MAKEFLAGS += -rR

#----

$(BUILD)/coupler_main: $(FMS_BUILD)/libFMS.a
$(BUILD)/coupler_main: $(ATMOS_BUILD)/libatmos_null.a
$(BUILD)/coupler_main: $(LAND_BUILD)/libland_null.a
$(BUILD)/coupler_main: $(ICE_PARAM_BUILD)/libice_param.a
$(BUILD)/coupler_main: $(ICEBERGS_BUILD)/libicebergs.a
$(BUILD)/coupler_main: FORCE $(BUILD)/Makefile
	if test $(FMS_BUILD)/libFMS.a -nt $@ \
	    -o $(ATMOS_BUILD)/libatmos_null.a -nt $@ \
	    -o $(LAND_BUILD)/libland_null.a -nt $@ \
	    -o $(ICE_PARAM_BUILD)/libice_param.a -nt $@ \
	    -o $(ICEBERGS_BUILD)/libicebergs.a -nt $@ ; then \
	  $(MAKE) -C $(@D) clean ; \
	fi
	$(MAKE) -C $(BUILD) coupler_main

$(BUILD)/Makefile: $(BUILD)/config.status $(BUILD)/Makefile.in
	cd $(BUILD) && ./config.status

$(BUILD)/config.status: $(FMS_BUILD)/libFMS.a
$(BUILD)/config.status: $(ATMOS_BUILD)/libatmos_null.a
$(BUILD)/config.status: $(LAND_BUILD)/libland_null.a
$(BUILD)/config.status: $(ICE_PARAM_BUILD)/libice_param.a
$(BUILD)/config.status: $(ICEBERGS_BUILD)/libicebergs.a
$(BUILD)/config.status: $(BUILD)/configure
	cd $(BUILD) && \
	PATH="${PATH}:$(dir $(abspath $(MAKEDEP)))" \
	FCFLAGS="${MOM_FCFLAGS}" \
	LDFLAGS="${MOM_LDFLAGS}" \
	./configure -n $(CONFIG_FLAGS)

$(BUILD)/Makefile.in: $(MAKEFILE_IN) | $(BUILD)
	cp $(MAKEFILE_IN) $(BUILD)/Makefile.in

$(BUILD)/configure: $(BUILD)/configure.ac $(BUILD)/m4
	autoreconf $(BUILD)

$(BUILD)/configure.ac: $(CONFIGURE_AC) | $(BUILD)
	cp $(CONFIGURE_AC) $(BUILD)/configure.ac

$(BUILD)/m4: $(M4DIR) | $(BUILD)
	cp -r $(M4DIR) $(BUILD)

$(BUILD):
	mkdir -p $@


#----
# Dependencies

$(ATMOS_BUILD)/libatmos_null.a: FORCE $(FMS_BUILD)/libFMS.a
	if test $(FMS_BUILD)/libFMS.a -nt $@ ; then \
	  $(MAKE) -C ../shared/atmos_null clean ; \
	fi
	$(MAKE) -C ../shared/atmos_null \
	  BUILD=$(abspath $(ATMOS_BUILD)) \
	  FMS_BUILD=$(abspath $(FMS_BUILD))

$(LAND_BUILD)/libland_null.a: FORCE $(FMS_BUILD)/libFMS.a
	if test $(FMS_BUILD)/libFMS.a -nt $@ ; then \
	  $(MAKE) -C ../shared/land_null clean ; \
	fi
	$(MAKE) -C ../shared/land_null \
	  BUILD=$(abspath $(LAND_BUILD)) \
	  FMS_BUILD=$(abspath $(FMS_BUILD))

$(ICE_PARAM_BUILD)/libice_param.a: FORCE $(FMS_BUILD)/libFMS.a
	if test $(FMS_BUILD)/libFMS.a -nt $@ ; then \
	  $(MAKE) -C ../shared/ice_param clean ; \
	fi
	$(MAKE) -C ../shared/ice_param \
	  BUILD=$(abspath $(ICE_PARAM_BUILD)) \
	  FMS_BUILD=$(abspath $(FMS_BUILD))

$(ICEBERGS_BUILD)/libicebergs.a: FORCE $(FMS_BUILD)/libFMS.a
	if test $(FMS_BUILD)/libFMS.a -nt $@ ; then \
	  $(MAKE) -C ../shared/icebergs clean ; \
	fi
	$(MAKE) -C ../shared/icebergs \
	  BUILD=$(abspath $(ICEBERGS_BUILD)) \
	  FMS_BUILD=$(abspath $(FMS_BUILD))

$(FMS_BUILD)/libFMS.a: FORCE
	$(MAKE) -C ../shared/fms \
	  BUILD=$(abspath $(FMS_BUILD))

FORCE:


#----
# Experiments

EXPTS = $(patsubst ./%/,%,$(dir $(shell find . -name MOM_parameter_doc.all)))
GET_NPROCS = $(abspath ../shared/tools/get_nprocs.sh)

REG_EXPTS = $(filter-out $(EXCLUDE),$(EXPTS))

RUNDIR = $(if $(OUTPUT),$(OUTPUT)/$(1),$(1))

.PHONY: run.all
run.all: $(foreach e,$(REG_EXPTS),run.$(e))

define EXPT_RULE
.PHONY: run.$(1)
run.$(1): $(RUNDIR)/ocean.stats | $(RUNDIR)

$(RUNDIR)/ocean.stats: $(BUILD)/coupler_main $(RUNDIR)/input.nml
	mkdir -p $(RUNDIR)/RESTART
	cd $(RUNDIR) && srun -mblock --exclusive -n $$$$($(GET_NPROCS) .) \
	  $(abspath $(BUILD)/coupler_main)

# TODO: Whitelist the files/dirs to copy?
# TODO: What about symbolic links?
$(RUNDIR)/input.nml: | $(RUNDIR)
	cp -r $(1)/* $(RUNDIR)/

$(RUNDIR):
	mkdir -p $(RUNDIR)

clean.$(1):
	rm -f $(RUNDIR)/CPU_stats
	rm -f $(RUNDIR)/Depth_list.nc
	rm -rf $(RUNDIR)/RESTART
	rm -f $(RUNDIR)/Vertical_coordinate.nc
	rm -f $(RUNDIR)/available_diags.??????
	rm -f $(RUNDIR)/ave_prog__*.nc
	rm -f $(RUNDIR)/cont__*.nc
	rm -f $(RUNDIR)/exitcode
	rm -f $(RUNDIR)/logfile.??????.out
	rm -f $(RUNDIR)/ocean.stats
	rm -f $(RUNDIR)/ocean.stats.nc
	rm -f $(RUNDIR)/ocean_geometry.nc
	rm -f $(RUNDIR)/prog__*.nc
	rm -f $(RUNDIR)/time_stamp.out
endef
$(foreach expt,$(EXPTS),$(eval $(call EXPT_RULE,$(expt))))

#----
# Cleanup

.PHONY: clean
clean:
	rm -rf $(BUILD)
	$(MAKE) -C ../shared/atmos_null clean
	$(MAKE) -C ../shared/land_null clean
	$(MAKE) -C ../shared/ice_param clean
	$(MAKE) -C ../shared/icebergs clean
	$(MAKE) -C ../shared/fms clean

.PHONY: clean.runs
clean.runs: $(foreach e,$(EXPTS),clean.$(e))
