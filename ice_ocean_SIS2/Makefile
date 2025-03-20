# User-defined configuration
-include config.mk

# Build configuration
BUILD ?= build
MOM_MEMORY ?=
SIS_MEMORY ?=

# Dependencies
FMS_CODEBASE ?= ../src/FMS2
FMS_BUILD ?= ../shared/fms/build
ICEBERGS_BUILD ?= ../shared/icebergs/build
ICE_PARAM_BUILD ?= ../shared/ice_param/build
ATMOS_BUILD ?= ../shared/atmos_null/build
LAND_BUILD ?= ../shared/land_null/build

# Autoconf configuration
MOM_CODEBASE ?= ../src/MOM6
MAKEFILE_IN ?= $(MOM_CODEBASE)/ac/Makefile.in
CONFIGURE_AC ?= configure.ice_ocean.ac
M4DIR ?= $(MOM_CODEBASE)/ac/m4
MAKEDEP ?= $(MOM_CODEBASE)/ac/makedep

# Run configuration
EXPT ?=
RUNDIR ?= ./$(EXPT)
LAUNCHER ?= mpirun
LAUNCHER_NP_FLAG ?= -np
LAUNCHER_FLAGS ?=
PYTHON ?= python

# Test suite
TESTDIR ?= scratch
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


#--------
# `make`

$(BUILD)/coupler_main: $(call rwildcard,$(CODEBASE)/src $(CODEBASE)/config_src/drivers/FMS_cap $(CODEBASE)/config_src/infra/ $(CODEBASE)/config_src/external,*.h *.c *.inc *.F90)
$(BUILD)/coupler_main: $(FMS_BUILD)/libFMS.a
$(BUILD)/coupler_main: $(ATMOS_BUILD)/libatmos_null.a
$(BUILD)/coupler_main: $(LAND_BUILD)/libland_null.a
$(BUILD)/coupler_main: $(ICE_PARAM_BUILD)/libice_param.a
$(BUILD)/coupler_main: $(ICEBERGS_BUILD)/libicebergs.a
$(BUILD)/coupler_main: $(BUILD)/Makefile
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

$(ATMOS_BUILD)/libatmos_null.a: $(call rwildcard,../src/atmos_null/,*.c *.h *.inc *.F90)
$(ATMOS_BUILD)/libatmos_null.a: $(FMS_BUILD)/libFMS.a
	$(MAKE) -C ../shared/atmos_null \
	  BUILD=$(abspath $(ATMOS_BUILD)) \
	  FMS_BUILD=$(abspath $(FMS_BUILD))

$(LAND_BUILD)/libland_null.a: $(call rwildcard,../src/land_null/,*.c *.h *.inc *.F90)
$(LAND_BUILD)/libland_null.a: $(FMS_BUILD)/libFMS.a
	$(MAKE) -C ../shared/land_null \
	  BUILD=$(abspath $(LAND_BUILD)) \
	  FMS_BUILD=$(abspath $(FMS_BUILD))

$(ICE_PARAM_BUILD)/libice_param.a: $(call rwildcard,../src/ice_param/,*.c *.h *.inc *.F90)
$(ICE_PARAM_BUILD)/libice_param.a: $(FMS_BUILD)/libFMS.a
	$(MAKE) -C ../shared/ice_param \
	  BUILD=$(abspath $(ICE_PARAM_BUILD)) \
	  FMS_BUILD=$(abspath $(FMS_BUILD))

$(ICEBERGS_BUILD)/libicebergs.a: $(call rwildcard,../src/icebergs/src/,*.c *.h *.inc *.F90)
$(ICEBERGS_BUILD)/libicebergs.a: $(FMS_BUILD)/libFMS.a
	$(MAKE) -C ../shared/icebergs \
	  BUILD=$(abspath $(ICEBERGS_BUILD)) \
	  FMS_BUILD=$(abspath $(FMS_BUILD))

$(FMS_BUILD)/libFMS.a: $(call rwildcard,$(FMS_CODEBASE)/,*.c *.h *.inc *.F90)
	$(MAKE) -C ../shared/fms \
	  BUILD=$(abspath $(FMS_BUILD)) \
	  CODEBASE=$(abspath $(FMS_CODEBASE))

FORCE:

# Recursive wildcard (finds all files in $1 with suffixes in $2)
rwildcard=$(foreach d,$(wildcard $(1:=/*)),$(call rwildcard,$d,$2) $(filter $(subst *,%,$2),$d))


#------------
# `make run`

GET_NPROCS = $(abspath ../shared/tools/get_nprocs.py)

.PHONY: run
run: $(RUNDIR)/ocean.stats

# `make run` directs user to select an experiment.
.PHONY: ./ocean.stats
./ocean.stats:
	@echo "Please specify the experiment to run.  For example:"
	@echo "  make run EXPT=double_gyre"
	@echo "  make run.double_gyre"
	@exit 1

# NOTE: This alias rule can only be used on single directories, not full paths.
.PHONY: run.%
run.%:
	$(MAKE) EXPT=$* run

ifdef EXPT
INPUT_MANIFEST = \
  $(shell $(PYTHON) ../shared/tools/gen_input_manifest.py $(EXPT))

$(RUNDIR)/ocean.stats: \
  $(BUILD)/coupler_main $(foreach f,$(INPUT_MANIFEST),$(RUNDIR)/$f) | $(RUNDIR)
	cd $(@D) \
	&& $(LAUNCHER) \
	  $(LAUNCHER_NP_FLAG) $$($(PYTHON) $(GET_NPROCS) $(abspath $(EXPT))) \
	  $(LAUNCHER_FLAGS) \
	  $(abspath $(BUILD)/coupler_main)
endif

# Define rules for moving data
ifneq ($(realpath $(EXPT)), $(realpath $(RUNDIR)))

define copy
$(RUNDIR)/$(1): $(EXPT)/$(1) | $(RUNDIR)
	cp -p $$^ $$@
endef
$(foreach f,$(filter-out INPUT,$(INPUT_MANIFEST)),$(eval $(call copy,$f)))

# TODO: Symlink will cause issues with restart runs
$(RUNDIR)/INPUT: $(EXPT)/INPUT | $(RUNDIR)
	if [ -e $< ]; then ln -s $(abspath $^) $@ ; fi

$(RUNDIR):
	mkdir -p $@

endif


#-------------
# `make test`

# This testing validates the parameter and diagnostic logs.

.PHONY: test.%
test.%:
	$(MAKE) EXPT=$* test

.PHONY: test
ifneq ($(realpath $(EXPT)), $(realpath $(RUNDIR)))
test: FORCE $(RUNDIR)/ocean.stats
	diff --color --to-file=$(RUNDIR) \
	  $(wildcard $(EXPT)/*_parameter_doc.* $(EXPT)/available_diags*)
else
test: FORCE $(RUNDIR)/ocean.stats
	git diff --exit-code $(EXPT)
endif


#------------
# Test suite

ALL_EXPTS := $(patsubst ./%/,%,\
  $(dir $(shell find . -name MOM_parameter_doc.all)))

EXPT_MANIFEST := $(filter-out $(EXCLUDE) $(TESTDIR)/%,$(ALL_EXPTS))

.PHONY: run.all
run.all: $(foreach e,$(EXPT_MANIFEST),$(TESTDIR)/$(e)/run)

# This is a dummy rule used to avoid recursive ocean.stats rules.
.PHONY: $(TESTDIR)/%/run
$(TESTDIR)/%/run: $(BUILD)/coupler_main
	$(MAKE) run EXPT=$* RUNDIR=$(TESTDIR)/$* TESTDIR=$(TESTDIR)

.PHONY: test.all
test.all: $(foreach e,$(EXPT_MANIFEST),$(TESTDIR)/$(e)/test)

# Another dummy rule
.PHONY: $(TESTDIR)/%/test
$(TESTDIR)/%/test: $(BUILD)/coupler_main
	$(MAKE) test EXPT=$* RUNDIR=$(TESTDIR)/$* TESTDIR=$(TESTDIR)


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
