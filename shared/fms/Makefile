# Configuration
BUILD ?= build

CODEBASE = ../../src/FMS
TARGET = libFMS.a
MAKEFILE_IN = ../../src/MOM6/ac/deps/Makefile.fms.in
CONFIGURE_AC = ../../src/MOM6/ac/deps/configure.fms.ac
M4DIR = ../../src/MOM6/ac/deps/m4

# These are required by the FMS2 test suite
CPPFLAGS += -DAU_TEST_KIND_=r8_kind
CPPFLAGS += -DTEST_SVP_KIND_=8

include ../config/Libs.mk
