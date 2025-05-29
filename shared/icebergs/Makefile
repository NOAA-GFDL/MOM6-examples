# Configuration
BUILD ?= build
FMS_BUILD ?= ../fms/build

CODEBASE = ../../src/icebergs/src
TARGET = libicebergs.a
CONFIGURE_AC = ../config/configure.icebergs.ac

FCFLAGS += -I$(abspath $(FMS_BUILD))
LDFLAGS += -L$(abspath $(FMS_BUILD))

include ../config/Libs.mk

$(BUILD)/$(TARGET): $(BUILD)/Makefile $(call find_src_files,$(CODEBASE))
	$(MAKE) -C $(BUILD) $(TARGET)
