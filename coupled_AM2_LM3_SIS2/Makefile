# Configuration
BUILD ?= build
MOM_MEMORY ?=
SIS_MEMORY ?=

# Dependencies
FMS_CODEBASE ?= ../src/FMS1
FMS_BUILD ?= ../shared/fms/build_fms1
AM2_BUILD ?= ../shared/AM2/build
ICEBERGS_BUILD ?= ../shared/icebergs/build_fms1
ICE_PARAM_BUILD ?= ../shared/ice_param/build_fms1
LM3_BUILD ?= ../shared/LM3/build

# Autoconf configuration
MOM_CODEBASE ?= ../src/MOM6
MAKEFILE_IN ?= $(MOM_CODEBASE)/ac/Makefile.in
CONFIGURE_AC ?= ../ac/configure.coupled.ac
M4DIR ?= $(MOM_CODEBASE)/ac/m4
MAKEDEP ?= $(MOM_CODEBASE)/ac/makedep

# Run configuration
EXPT ?=
OUTPUT ?= ./$(EXPT)
LAUNCHER ?= mpirun
EXCLUDE ?=

# Autoconf setup
EXTRA_SRC_DIRS = \
  $(abspath ../src/SIS2/src) \
  $(abspath ../src/SIS2/config_src/external) \
  $(abspath ../src/coupler)

CONFIG_FLAGS := --config-cache
CONFIG_FLAGS += --srcdir=$(abspath $(MOM_CODEBASE))
CONFIG_FLAGS += --with-driver=FMS_cap
CONFIG_FLAGS += --with-framework=fms1
ifdef MOM_MEMORY
  CONFIG_FLAGS += MOM_MEMORY=$(abspath $(MOM_MEMORY))
endif
ifdef SIS_MEMORY
  CONFIG_FLAGS += SIS_MEMORY=$(abspath $(SIS_MEMORY))
endif

# `export` disables autoconf defaults; this restores them
CFLAGS ?= -g -O2
FCFLAGS ?= -g -O2

# Path to fms_platform.h
# NOTE: Most libraries need an explicit path to this file.  Someday, this could
#   be handled by library-specific autoconf tests.
FCFLAGS += -I$(abspath $(FMS_CODEBASE)/include)

MOM_FCFLAGS = $(FCFLAGS) \
  -I$(abspath $(FMS_BUILD)) \
  -I$(abspath $(AM2_BUILD)) \
  -I$(abspath $(ICEBERGS_BUILD)) \
  -I$(abspath $(ICE_PARAM_BUILD)) \
  -I$(abspath $(LM3_BUILD))

MOM_LDFLAGS := $(LDFLAGS) \
  -L$(abspath $(FMS_BUILD)) \
  -L$(abspath $(AM2_BUILD)) \
  -L$(abspath $(ICEBERGS_BUILD)) \
  -L$(abspath $(ICE_PARAM_BUILD)) \
  -L$(abspath $(LM3_BUILD))

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

all: $(BUILD)/coupler_main

$(BUILD)/coupler_main: FORCE $(BUILD)/Makefile
	if test $(FMS_BUILD)/libFMS.a -nt $@ \
	    -o $(AM2_BUILD)/libAM2.a -nt $@ \
	    -o $(LM3_BUILD)/libLM3.a -nt $@ \
	    -o $(ICE_PARAM_BUILD)/libice_param.a -nt $@ \
	    -o $(ICEBERGS_BUILD)/libicebergs.a -nt $@ ; then \
	  $(MAKE) -C $(@D) clean ; \
	fi
	$(MAKE) -C $(BUILD) coupler_main

$(BUILD)/Makefile: $(BUILD)/config.status $(BUILD)/Makefile.in
	cd $(BUILD) && ./config.status

$(BUILD)/config.status: $(FMS_BUILD)/libFMS.a
$(BUILD)/config.status: $(AM2_BUILD)/libAM2.a
$(BUILD)/config.status: $(LM3_BUILD)/libLM3.a
$(BUILD)/config.status: $(ICE_PARAM_BUILD)/libice_param.a
$(BUILD)/config.status: $(ICEBERGS_BUILD)/libicebergs.a
$(BUILD)/config.status: $(BUILD)/configure
	cd $(BUILD) && \
	PATH=${PATH}:$(dir $(abspath $(MAKEDEP))) \
	FCFLAGS="${MOM_FCFLAGS}" \
	LDFLAGS="${MOM_LDFLAGS}" \
	./configure -n ${CONFIG_FLAGS}

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

$(AM2_BUILD)/libAM2.a: FORCE $(FMS_BUILD)/libFMS.a
	if test $(FMS_BUILD)/libFMS.a -nt $@ ; then \
	  $(MAKE) -C ../shared/AM2 clean ; \
	fi
	$(MAKE) -C ../shared/AM2 \
	  BUILD=$(abspath $(AM2_BUILD)) \
	  FMS_BUILD=$(abspath $(FMS_BUILD))

$(LM3_BUILD)/libLM3.a: FORCE $(FMS_BUILD)/libFMS.a
	if test $(FMS_BUILD)/libFMS.a -nt $@ ; then \
	  $(MAKE) -C ../shared/LM3 clean ; \
	fi
	$(MAKE) -C ../shared/LM3 \
	  BUILD=$(abspath $(LM3_BUILD)) \
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
	  BUILD=$(abspath $(FMS_BUILD)) \
	  CODEBASE=$(abspath $(FMS_CODEBASE))

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
	$(MAKE) -C ../shared/AM2 clean \
	  BUILD=$(abspath $(AM2_BUILD))
	$(MAKE) -C ../shared/LM3 clean
	  BUILD=$(abspath $(LM3_BUILD))
	$(MAKE) -C ../shared/ice_param clean \
	  BUILD=$(abspath $(ICE_PARAM_BUILD))
	$(MAKE) -C ../shared/icebergs clean \
	  BUILD=$(abspath $(ICEBERGS_BUILD))
	$(MAKE) -C ../shared/fms clean \
	  BUILD=$(abspath $(FMS_BUILD))

.PHONY: clean.runs
clean.runs: $(foreach e,$(EXPTS),clean.$(e))
