# MOM6 experiment Makefile
#
# make
#   Build MOM6 and dependencies.  Target is in build/ directory.
#
# make BUILD=target
#   Build MOM6 in the target/ directory.
#
# make run EXPT=path/to/expt
#   Run EXPT in the EXPT directory.
#   If RUNDIR is unset, then the experiment is run in-place within EXPT.
#   Example:
#   	make run EXPT=single_column/EPBL
#
# make run EXPT=path/to/expt RUNDIR=output_dir
#	Run EXPT in the RUNDIR directory.
#   Example:
#   	make run EXPT=single_column/EPBL RUNDIR=target_dir
#
# make run.expt_name
#   If EXPT is a single word then the shortened form can be used.
#   Example:
#   	make run.double_gyre
#
# make test EXPT=expt_name
# make test.expt_name
#	Run tests associated with EXPT.
#   Currently only checks MOM_parameter_doc.* and available_diags* files.
#
# make clean
# make clean BUILD=build_dir
#   Clean up and delete the BUILD directory.


# User-defined configuration
-include config.mk

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
RUNDIR ?= ./$(EXPT)
LAUNCHER ?= mpirun
LAUNCHER_NP_FLAG ?= -np
LAUNCHER_FLAGS ?=
PYTHON ?= python

# Test suite
TESTDIR ?= scratch
INCLUDE ?=
EXCLUDE ?= \
  tides_025 \
  ISOMIP/% \
  MESO_025_% \
  rotating_gravity_current/% \
  buoy_forced_basin \
  idealized_hurricane \
  global


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


#--------------
# `make build`

.PHONY: all
all: $(BUILD)/MOM6

# NOTE: If libFMS has changed, then we completely rebuild MOM6
$(BUILD)/MOM6: $(call rwildcard,$(CODEBASE)/src $(CODEBASE)/config_src/drivers/solo_driver $(CODEBASE)/config_src/infra/ $(CODEBASE)/config_src/external,*.h *.c *.inc *.F90)
$(BUILD)/MOM6: $(FMS_BUILD)/libFMS.a
$(BUILD)/MOM6: $(BUILD)/Makefile
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


# Dependencies

$(FMS_BUILD)/libFMS.a: $(call rwildcard,$(FMS_CODEBASE)/,*.c *.h *.inc *.F90)
	$(MAKE) -C ../shared/fms \
	  BUILD=$(abspath $(FMS_BUILD)) \
	  CODEBASE=$(abspath $(FMS_CODEBASE))

FORCE:

# Recursive wildcard (finds all files in $1 with suffixes in $2)
rwildcard=$(foreach d,$(wildcard $(1:=/*)),$(call rwildcard,$d,$2) $(filter $(subst *,%,$2),$d))


#-----------
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

$(RUNDIR)/ocean.stats: NPROCS=$(shell $(PYTHON) $(GET_NPROCS) $(abspath $(EXPT)))
$(RUNDIR)/ocean.stats: $(BUILD)/MOM6 $(foreach f,$(INPUT_MANIFEST),$(RUNDIR)/$f) | $(RUNDIR)
	cd $(@D) \
	&& $(LAUNCHER) $(LAUNCHER_NP_FLAG) $(NPROCS) $(LAUNCHER_FLAGS) $(abspath $(BUILD)/MOM6)
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

ifdef INCLUDE
EXPT_MANIFEST := $(INCLUDE)
else
ALL_EXPTS := $(patsubst ./%/,%,\
  $(dir $(shell find . -name MOM_parameter_doc.all)))

EXPT_MANIFEST := $(filter-out $(EXCLUDE) $(TESTDIR)/%,$(ALL_EXPTS))
endif

.PHONY: run.all
run.all: $(foreach e,$(EXPT_MANIFEST),$(TESTDIR)/$(e)/run)

# This is a dummy rule used to avoid recursive ocean.stats rules.
.PHONY: $(TESTDIR)/%/run
$(TESTDIR)/%/run: $(BUILD)/MOM6
	$(MAKE) run EXPT=$* RUNDIR=$(TESTDIR)/$* TESTDIR=$(TESTDIR)

.PHONY: test.all
test.all: $(foreach e,$(EXPT_MANIFEST),$(TESTDIR)/$(e)/test)

# Another dummy rule
.PHONY: $(TESTDIR)/%/test
$(TESTDIR)/%/test: $(BUILD)/MOM6
	$(MAKE) test EXPT=$* RUNDIR=$(TESTDIR)/$* TESTDIR=$(TESTDIR)


#---------
# Cleanup

# I probably need a rule in Makefile.in for all the autoconf stuff.
.PHONY: clean
clean:
	cd $(BUILD) && make distclean
	rm -f $(BUILD)/aclocal.m4
	rm -rf $(BUILD)/autom4te.cache
	rm -rf $(BUILD)/config.cache
	rm -f $(BUILD)/configure
	rm -f $(BUILD)/configure.ac
	rm -rf $(BUILD)/m4
	rm -f $(BUILD)/Makefile.in
	rmdir $(BUILD)
	$(MAKE) -C ../shared/fms clean

#.PHONY: clean.run
#ifneq ($(realpath $(EXPT)), $(realpath $(RUNDIR)))
#clean.run:
#	if [ ! -d "$(EXPT)" ]; then exit 1; fi
#	echo rm -rf $(RUNDIR)
#else
## TODO: We need a better OUTPUT_MANIFEST
#clean.run:
#	if [ ! -d "$(EXPT)" ]; then exit 1; fi
#	for f in $(INPUT_MANIFEST) MOM_parameter_doc.{all,short,layout,debugging}; do \
#	  git checkout $(EXPT)/$$f; \
#	done
#	echo rm -f $(EXPT)/ocean.stats
#	echo rm -f $(EXPT)/available_diags*
#endif
