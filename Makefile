-include config.mk

# Configuration
BUILD ?=

# Variable `export` replaces the default autoconf values with empty strings.
# This restores the default values.
CFLAGS ?= -g -O2
FCFLAGS ?= -g -O2

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

export LAUNCHER
export LAUNCHER_NP_FLAG
export LAUNCHER_FLAGS

# Disable builtin rules and variables
MAKEFLAGS += -rR

#------
# make

# Public models
.PHONY: all
all: ocean_only ice_ocean_SIS2

# GFDL-specific coupled models (requires access to GFDL intranet)
.PHONY: gfdl
gfdl: ocean_only ice_ocean_SIS2 coupled_AM2_LM3_SIS2


# Dependencies
# Although dependencies are defined in submakes, we pre-build the ocean_only
# and ice_ocean_SIS2 ones in order to prevent parallel build conflicts.
ocean_only: fms2
ice_ocean_SIS2: fms2 atmos_null land_null icebergs ice_param
atmos_null land_null icebergs ice_param: fms2


# If BUILD is defined, override the default values and store as macros.
# These are passed to the submake build/run/test rules.
ifdef BUILD
FMS2_BUILD = $(abspath $(BUILD)/fms2)
FMS1_BUILD = $(abspath $(BUILD)/fms1)
ATMOS_NULL_BUILD = $(abspath $(BUILD)/atmos_null)
AM2_BUILD = $(abspath $(BUILD)/AM2)
LAND_NULL_BUILD = $(abspath $(BUILD)/land_null)
LM3_BUILD = $(abspath $(BUILD)/LM3)
ICEBERGS_BUILD = $(abspath $(BUILD)/icebergs)
ICEBERGS_FMS1_BUILD = $(abspath $(BUILD)/icebergs_fms1)
ICE_PARAM_BUILD = $(abspath $(BUILD)/ice_param)
ICE_PARAM_FMS1_BUILD = $(abspath $(BUILD)/ice_param_fms1)
OCEAN_ONLY_BUILD = $(abspath $(BUILD)/ocean_only)
ICE_OCEAN_BUILD = $(abspath $(BUILD)/ice_ocean_SIS2)
COUPLED_BUILD = $(abspath $(BUILD)/coupled_AM2_LM3_SIS2)

FMS2_BUILDFLAGS = BUILD=$(FMS2_BUILD)

FMS1_BUILDFLAGS = BUILD=$(FMS1_BUILD)

ATMOS_NULL_BUILDFLAGS = \
  BUILD=$(ATMOS_NULL_BUILD) \
  FMS_BUILD=$(FMS2_BUILD)

AM2_BUILDFLAGS = \
  BUILD=$(AM2_BUILD) \
  FMS_BUILD=$(FMS1_BUILD)

LAND_NULL_BUILDFLAGS = \
  BUILD=$(LAND_NULL_BUILD) \
  FMS_BUILD=$(FMS2_BUILD)

LM3_BUILDFLAGS = \
  BUILD=$(LM3_BUILD) \
  FMS_BUILD=$(FMS1_BUILD)

ICEBERGS_BUILDFLAGS = \
  BUILD=$(ICEBERGS_BUILD) \
  FMS_BUILD=$(FMS2_BUILD)

ICEBERGS_FMS1_BUILDFLAGS = \
  BUILD=$(ICEBERGS_FMS1_BUILD) \
  FMS_BUILD=$(FMS1_BUILD)

ICE_PARAM_BUILDFLAGS = \
  BUILD=$(ICE_PARAM_BUILD) \
  FMS_BUILD=$(FMS2_BUILD)

ICE_PARAM_FMS1_BUILDFLAGS = \
  BUILD=$(ICE_PARAM_FMS1_BUILD) \
  FMS_BUILD=$(FMS1_BUILD)

OCEAN_ONLY_BUILDFLAGS = \
  BUILD=$(OCEAN_ONLY_BUILD) \
  FMS_BUILD=$(FMS2_BUILD)

ICE_OCEAN_BUILDFLAGS = \
  BUILD=$(ICE_OCEAN_BUILD) \
  FMS_BUILD=$(FMS2_BUILD) \
  ATMOS_BUILD=$(ATMOS_NULL_BUILD) \
  LAND_BUILD=$(LAND_NULL_BUILD) \
  ICEBERGS_BUILD=$(ICEBERGS_BUILD) \
  ICE_PARAM_BUILD=$(ICE_PARAM_BUILD)

COUPLED_BUILDFLAGS = \
  BUILD=$(COUPLED_BUILD) \
  FMS_BUILD=$(FMS1_BUILD) \
  AM2_BUILD=$(AM2_BUILD) \
  LM3_BUILD=$(LM3_BUILD) \
  ICEBERGS_BUILD=$(ICEBERGS_FMS1_BUILD) \
  ICE_PARAM_BUILD=$(ICE_PARAM_FMS1_BUILD)
endif

.PHONY: ocean_only
ocean_only:
	$(MAKE) -C ocean_only $(OCEAN_ONLY_BUILDFLAGS)

.PHONY: ice_ocean_SIS2
ice_ocean_SIS2:
	$(MAKE) -C ice_ocean_SIS2 $(ICE_OCEAN_BUILDFLAGS)

.PHONY: coupled_AM2_LM3_SIS2
coupled_AM2_LM3_SIS2:
	$(MAKE) -C coupled_AM2_LM3_SIS2 $(COUPLED_BUILDFLAGS)

.PHONY: land_null
land_null:
	$(MAKE) -C shared/land_null $(LAND_NULL_BUILDFLAGS)

.PHONY: LM3
LM3:
	$(MAKE) -C shared/LM3 $(LM3_BUILDFLAGS)

.PHONY: atmos_null
atmos_null: fms2
	$(MAKE) -C shared/atmos_null $(ATMOS_NULL_BUILDFLAGS)

.PHONY: AM2
AM2: fms1
	$(MAKE) -C shared/AM2 $(AM2_BUILDFLAGS)

.PHONY: icebergs
icebergs: fms2
	$(MAKE) -C shared/icebergs $(ICEBERGS_BUILDFLAGS)

.PHONY: icebergs_fms1
icebergs_fms1: fms1
	$(MAKE) -C shared/icebergs $(ICEBERGS_BUILDFLAGS)

.PHONY: ice_param
ice_param: fms2
	$(MAKE) -C shared/ice_param $(ICE_PARAM_BUILDFLAGS)

.PHONY: ice_param_fms1
ice_param_fms1: fms1
	$(MAKE) -C shared/ice_param $(ICE_PARAM_FMS1_BUILDFLAGS)

.PHONY: fms2
fms2:
	$(MAKE) -C shared/fms $(FMS2_BUILDFLAGS)

.PHONY: fms1
fms1:
	$(MAKE) -C shared/fms $(FMS1_BUILDFLAGS) CODEBASE=$(abspath src/FMS1)


#----------
# make run

.PHONY: run.all
run.all: run.ocean_only run.ice_ocean_SIS2 run.coupled_AM2_LM3_SIS2

.PHONY: run.ocean_only
run.ocean_only: ocean_only
	$(MAKE) -C ocean_only/ run.all $(OCEAN_ONLY_BUILDFLAGS)

.PHONY: run.ice_ocean_SIS2
run.ice_ocean_SIS2: ice_ocean_SIS2
	$(MAKE) -C ice_ocean_SIS2/ run.all $(ICE_OCEAN_BUILDFLAGS)

.PHONY: run.coupled_AM2_LM3_SIS2
run.coupled_AM2_LM3_SIS2: coupled_AM2_LM3_SIS2
	$(MAKE) -C coupled_AM2_LM3_SIS2/ run.all $(COUPLED_BUILDFLAGS)


#-----------
# make test

.PHONY: test.all
test.all: test.ocean_only test.ice_ocean_SIS2 test.coupled_AM2_LM3_SIS2

.PHONY: test.ocean_only
test.ocean_only: ocean_only
	$(MAKE) -C ocean_only/ test.all $(OCEAN_ONLY_BUILDFLAGS)

.PHONY: test.ice_ocean_SIS2
test.ice_ocean_SIS2: ice_ocean_SIS2
	$(MAKE) -C ice_ocean_SIS2/ test.all $(ICE_OCEAN_BUILDFLAGS)

.PHONY: test.coupled_AM2_LM3_SIS2
test.coupled_AM2_LM3_SIS2: coupled_AM2_LM3_SIS2
	$(MAKE) -C coupled_AM2_LM3_SIS2/ test.all $(COUPLED_BUILDFLAGS)


# -----------
# make clean
# (TODO: not yet working)

MODELS = ocean_only ice_ocean_SIS2 coupled_AM2_LM3_SIS2

DEPS = \
  atmos_null land_null icebergs ice_param \
  AM2 LM3 icebergs_fms1 ice_param_fms1

.PHONY: clean
clean: $(foreach m,$(MODELS),$(m).clean) $(foreach d,$(DEPS),$(d).clean) fms.clean

.PHONY: $(foreach m,$(MODELS) $(DEPS) fms,$(m).clean)

$(foreach model,$(MODELS),$(model).clean):
	$(MAKE) -C $(subst .clean,,$@) clean

$(foreach dep,$(DEPS) fms,$(dep).clean):
	$(MAKE) -C shared/$(subst .clean,,$@) clean
