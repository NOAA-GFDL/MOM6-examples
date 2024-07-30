MODELS = ocean_only ice_ocean_SIS2 coupled_AM2_LM3_SIS2
DEPS = AM2 atmos_null LM3 land_null ice_param icebergs

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

# Disable builtin rules and variables
MAKEFLAGS += -rR

#---

# Public models
.PHONY: all
all: ocean_only ice_ocean_SIS2

# GFDL-specific coupled models (requires access to GFDL intranet)
.PHONY: gfdl
gfdl: ocean_only ice_ocean_SIS2 coupled_AM2_LM3_SIS2

# Dependencies
$(MODELS): fms
ice_ocean_SIS2 coupled_AM2_LM3_SIS2: ice_param icebergs
ice_ocean_SIS2: atmos_null land_null
coupled_AM2_LM3_SIS2: AM2 LM3
$(DEPS): fms

.PHONY: $(MODELS)
$(MODELS):
	$(MAKE) -C $@


.PHONY: $(DEPS) fms
$(DEPS) fms:
	$(MAKE) -C shared/$@


# Cleanup
.PHONY: clean
clean: $(foreach m,$(MODELS),$(m).clean) $(foreach d,$(DEPS),$(d).clean) fms.clean

.PHONY: $(foreach m,$(MODELS) $(DEPS) fms,$(m).clean)

$(foreach model,$(MODELS),$(model).clean):
	$(MAKE) -C $(subst .clean,,$@) clean

$(foreach dep,$(DEPS) fms,$(dep).clean):
	$(MAKE) -C shared/$(subst .clean,,$@) clean


# Runs
# NOTE: This is not yet implemented, and is only an example of how this could
# look in a future version.

RUNDIR ?= runs

# unused
rwildcard=$(foreach d,$(wildcard $(1:=/*)),\
  $(call rwildcard,$d,$2) $(filter $(subst *,%,$2),$d))

# Build manifest
# TODO: recursive wildcard
PARAM_LIST=$(shell find $1 -name MOM_parameter_doc.all)
EXPT_DIRS=$(patsubst $1/%/MOM_parameter_doc.all,%,$(call PARAM_LIST,$1))

# 1: rundir
# 2: build dir
# 3: expt dir
define EXPT_RULE
$(1)/ocean.stats: ocean_only ;
	$(MAKE) -C ocean_only ../$(1)/ocean.stats \
	  BUILD=../$(2) \
	  OUTPUT=../$(1) \
	  EXPT=$(3)
endef
$(foreach e,$(call EXPT_DIRS,ocean_only),\
  $(eval $(call EXPT_RULE,$(RUNDIR)/ocean_only/symmetric/$e,$(BUILD)/ocean_only/symmetric,$e)))


run.ocean_only: $(foreach e,$(call EXPT_DIRS,ocean_only),\
  $(RUNDIR)/ocean_only/symmetric/$(e)/ocean.stats)
