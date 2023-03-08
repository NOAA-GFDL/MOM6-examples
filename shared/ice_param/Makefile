# Configuration
BUILD ?= build
FMS_BUILD ?= ../fms/$(BUILD)

CODEBASE = ../../src/ice_param
TARGET = libice_param.a
CONFIGURE_AC = ../config/configure.ice_param.ac

FCFLAGS += -I$(abspath $(FMS_BUILD))
LDFLAGS += -L$(abspath $(FMS_BUILD))

include ../config/Libs.mk
