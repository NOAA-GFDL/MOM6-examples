# Build configuration
BUILD ?= build
MOM_MEMORY ?=

# Dependencies
FMS_CODEBASE ?= ../src/FMS2
FMS_BUILD ?= ../shared/fms/build

# Autoconf configuration
CODEBASE ?= ../src/MOM6
MAKEFILE_IN ?= $(CODEBASE)/ac/Makefile.in
CONFIGURE_AC ?= $(CODEBASE)/ac/configure.ac
M4DIR ?= $(CODEBASE)/ac/m4
MAKEDEP ?= $(CODEBASE)/ac/makedep

# Run configuration
EXPT ?=
OUTPUT ?= ./$(EXPT)
LAUNCHER ?= mpirun
# The following are either too large or appear to be broken.
EXCLUDE ?= \
  tides_025 \
  ISOMIP/% \
  MESO_025_% \
  rotating_gravity_current/% \
  buoy_forced_basin


# Autoconf setup
CONFIG_FLAGS := --config-cache
CONFIG_FLAGS += --srcdir=$(abspath $(CODEBASE))/ac
ifdef MOM_MEMORY
  CONFIG_FLAGS += MOM_MEMORY=$(abspath $(MOM_MEMORY))
endif

# `export` disables autoconf defaults; this restores them
CFLAGS ?= -g -O2
FCFLAGS ?= -g -O2

FCFLAGS += -I$(abspath $(FMS_BUILD))
LDFLAGS += -L$(abspath $(FMS_BUILD))

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


# Makefile setup

# Verify that BUILD is not set to the current directory
# (which would clobber this Makefile)
MAKEPATH = $(realpath $(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
ifeq ($(MAKEPATH), $(realpath $(BUILD)))
  $(error BUILD cannot be set to the current directory)
endif

# Disable builtin rules and variables
MAKEFLAGS += -rR

#----

.PHONY: all
all: $(BUILD)/MOM6

# NOTE: If libFMS has changed, then we completely rebuild MOM6
$(BUILD)/MOM6: FORCE $(BUILD)/Makefile $(FMS_BUILD)/libFMS.a
	if test $(FMS_BUILD)/libFMS.a -nt $@ ; then \
	  $(MAKE) -C $(BUILD) clean ; \
	fi
	$(MAKE) -C $(BUILD) MOM6

$(BUILD)/Makefile: $(BUILD)/config.status $(BUILD)/Makefile.in
	cd $(BUILD) && ./config.status

$(BUILD)/config.status: $(BUILD)/configure $(FMS_BUILD)/libFMS.a
	cd $(BUILD) && \
	PATH="${PATH}:$(dir $(abspath $(MAKEDEP)))" \
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

$(FMS_BUILD)/libFMS.a: FORCE
	$(MAKE) -C ../shared/fms \
	  BUILD=$(abspath $(FMS_BUILD)) \
	  CODEBASE=$(abspath $(FMS_CODEBASE))

FORCE:

#----
# Experiments
#
# Experiment configuration
# (NOTE: This is probably going away)

# NOTE: Static output may be produced alongside the configurations, so we
#   assume the *.static format and exclude them from the manifests.
EXPT_MANIFEST := $(patsubst ./%/,%,\
  $(dir $(shell find . -name MOM_parameter_doc.all -not -path "*/*.static/*")))
STATIC_EXPTS := $(patsubst ./%/,%,\
  $(dir $(shell find . -name MOM_memory.h -not -path "*/*.static/*")))

# Filter out the undesired experiments
EXPTS := $(filter-out $(EXCLUDE),$(EXPT_MANIFEST))

GET_NPROCS := $(abspath ../shared/tools/get_nprocs.sh)

# List of potential input files
# TODO: Generate this from input.nml
INPUT_FILESET = \
  input.nml \
  MOM_input \
  MOM_override \
  diag_table \
  data_table \
  field_table \
  INPUT

MANIFEST=$(notdir $(wildcard $(foreach f,$(INPUT_FILESET),$(EXPT)/$f)))

.PHONY: run
run: $(OUTPUT)/ocean.stats

.PHONY: ./ocean.stats
./ocean.stats:
	@echo "Please specify the experiment to run.  For example:"
	@echo "  make run EXPT=double_gyre"
	@echo "  make run.double_gyre"

run.%:
	$(MAKE) EXPT=$* run

%/ocean.stats: $(BUILD)/MOM6 $(foreach f,$(MANIFEST),%/$f) | %
	mkdir -p $(@D)/RESTART
	cd $(@D) && $(LAUNCHER) -np $$($(GET_NPROCS) $(abspath $(@D))) $(abspath $(BUILD)/MOM6)

ifneq ($(realpath $(EXPT)), $(realpath $(OUTPUT)))
define copy
$(OUTPUT)/$(1): $(EXPT)/$(1) | $(OUTPUT)
	cp -p $$^ $$@
endef
$(foreach f,$(MANIFEST),$(eval $(call copy,$f)))
endif

# TODO: Symlink will cause issues with restart runs
$(OUTPUT)/INPUT: $(EXPT)/INPUT | $(OUTPUT)
	if [ -e $< ]; then ln -s $(abspath $^) $@ ; fi

$(OUTPUT):
	mkdir -p $@


#.PHONY: run.all
#run.all: $(foreach e,$(EXPTS),run.$(e))

## Support macros
#RUNDIR = $(if $(OUTPUT),$(OUTPUT),.)
#
## MOM6 output
#MOM_OUTPUT = \
#  available_diags.?????? \
#  CPU_stats \
#  Depth_list.nc \
#  exitcode \
#  Vertical_coordinate.nc \
#  logfile.??????.out \
#  ocean.stats \
#  ocean.stats.nc \
#  ocean_geometry.nc \
#  time_stamp.out
#
## TODO: generate the diagnostic output files.  For now we just guess.
#MOM_OUTPUT += \
#  ave_prog__*.nc \
#  cont__*.nc \
#  prog__*.nc

## $(1): Experiment directory / name
#define EXPT_RULE
#
#.PHONY: run.$(1)
#run.$(1): $(RUNDIR)/$(1)/ocean.stats | $(RUNDIR)/$(1)
#
#$(RUNDIR)/$(1)/ocean.stats: $(BUILD)/MOM6 $(RUNDIR)/$(1)/input.nml
#	mkdir -p $(RUNDIR)/$(1)/RESTART
#	cd $(RUNDIR)/$(1) && $(LAUNCHER) -n $(NPROCS) $(abspath $(BUILD)/MOM6)
#
#$(RUNDIR)/$(1)/input.nml: | $(RUNDIR)/$(1)
#	cp -r $(1)/* $(RUNDIR)/$(1)/
#
#$(RUNDIR)/$(1):
#	mkdir -p $(RUNDIR)/$(1)
#
#.PHONY: clean.$(1)
#clean.$(1):
#	if [ $(realpath $(RUNDIR)/$(1)) != $(realpath ./$(1)) ]; then \
#	  rm -rf $(RUNDIR)/$(1); \
#	else \
#	  rm -f $(addprefix $(1)/,${MOM_OUTPUT}); \
#	  rm -rf $(1)/RESTART; \
#	fi
#endef
#$(foreach e,$(EXPTS),$(eval $(call EXPT_RULE,$(e))))


#----
# Cleanup

.PHONY: clean
clean:
	rm -rf $(BUILD)
	$(MAKE) -C ../shared/fms clean

.PHONY: clean.runs
clean.runs: $(foreach e,$(EXPTS),clean.$(e))
