# Convenience make file with targets for complex tasks
# - Some targets update the working directory so be careful
# - These targets contain the commands that were in the .gitlab-ci.yml for various repositories. Putting them here allows us to develop and debug them at the command line.

# To test the pipelines by hand, use this Makefile and set CACHE_DIR and CI_PIPELINE_ID to something useful. e.g.
#   export CACHE_DIR=/lustre/f2/scratch/$USER/tmp
#   export CI_PIPELINE_ID=0000
# then
#   make -f tools/MRS/Makefile ...

# Path to this and other make files
MPTH ?= $(dir $(firstword $(MAKEFILE_LIST)))
# Path to configuration working directory (MOM6-examples)
CONFIGS ?= .
MOM6_SRC ?= src/MOM6
SIS2_SRC ?= src/SIS2

all:

# MOM6-examples gitlab pipeline (to be run from top of MOM6-examples)
# - Assumes a recursive clone of MOM6-examples is complete
# - Steps implemented in target:
#   - clone source code components for coupled models
#   - build executables (only dynamic symmetric)
#   - create manifest
#   - run standard tests
#   - check status of doc files
m6e-pipeline:
	@echo -e "\e[0Ksection_start:`date +%s`:clone[collapsed=true]\r\e[0KCloning submodules"
	test -f src/MOM6/README.md || (git submodule sync --recursive && git submodule update --init --recursive)
	test -d src/LM3 || make -f tools/MRS/Makefile.clone clone_gfdl -s
	@echo -e "\e[0Ksection_end:`date +%s`:clone\r\e[0K"
	@echo -e "\e[0Ksection_start:`date +%s`:environ[collapsed=true]\r\e[0KFetching environ"
	echo "Temporarily cloning stats repo to obtain environ/ directory"
	git clone --depth 1 https://gitlab.gfdl.noaa.gov/ogrp/Gaea-stats-MOM6-examples.git stats-tmp && mv stats-tmp/environ environ && rm -rf stats-tmp
	@echo -e "\e[0Ksection_end:`date +%s`:environ\r\e[0K"
	@echo -e "\e[0Ksection_start:`date +%s`:build[collapsed=true]\r\e[0KCompiling executables"
	time make -f tools/MRS/Makefile.build repro_gnu ENVIRON=environ -s -j
	@echo -e "\e[0Ksection_end:`date +%s`:build\r\e[0K"
	@echo -e "\e[0Ksection_start:`date +%s`:run[collapsed=true]\r\e[0KSubmit batch job"
	bash tools/MRS/generate_manifest.sh . tools/MRS/excluded-expts.txt > manifest.mk
	(echo '#!/bin/tcsh';echo 'time make -f tools/MRS/Makefile.run gnu_all MEMORY=dynamic_symmetric -s -j') > job.sh
	sbatch --clusters=c4 --nodes=25 --time=0:08:00 --account=gfdl_o --qos=debug --job-name=mom6_examples_tests --output=log.$$CI_PIPELINE_ID --wait job.sh && ( echo -e "\e[0Ksection_end:`date +%s`:run\r\e[0K" ; echo -e "\e[0Ksection_start:`date +%s`:joblog[collapsed=true]\r\e[0KJob output" ; cat log.$$CI_PIPELINE_ID ; echo -e "\e[0Ksection_end:`date +%s`:joblog\r\e[0K" ) || ( echo -e "\e[0Ksection_end:`date +%s`:run\r\e[0K" ; echo -e "\e[0Ksection_start:`date +%s`:joblog[collapsed=true]\r\e[0KJob output" ; cat log.$$CI_PIPELINE_ID ; echo -e "\e[0Ksection_end:`date +%s`:joblog\r\e[0K" ; echo Job failed ; exit 911 )
	git status
	git diff --exit-code

# MOM6 gitlab pipelines (to be run from above MOM6-examples)
# Note: multiple targets for each job.
# These commands are run before each job stage
# - git clone https://gitlab.gfdl.noaa.gov/ogrp/Gaea-stats-MOM6-examples.git tests
# - cd tests && git submodule init && git submodule update
# - cd MOM6-examples
mom6-pipeline-run:
	@echo -e "\e[0Ksection_start:`date +%s`:uncache[collapsed=true]\r\e[0KUncaching executables"
	tar vzxf $(CACHE_DIR)/build-repro-gnu-$(CI_PIPELINE_ID).tgz
	tar vzxf $(CACHE_DIR)/build-static-gnu-$(CI_PIPELINE_ID).tgz
	tar vzxf $(CACHE_DIR)/build-repro-intel-$(CI_PIPELINE_ID).tgz
	tar vzxf $(CACHE_DIR)/build-repro-pgi-$(CI_PIPELINE_ID).tgz
	bash tools/MRS/generate_manifest.sh . tools/MRS/excluded-expts.txt > manifest.mk
	time make -f tools/MRS/Makefile.clone .datasets
	@echo -e "\e[0Ksection_end:`date +%s`:uncache\r\e[0K"
	(echo '#!/bin/tcsh';echo 'time make -f tools/MRS/Makefile mom6-pipeline-run-steps') > job.sh
	sbatch --clusters=c4 --nodes=30 --time=1:00:00 --account=gfdl_o --qos=debug --job-name=mom6_examples_tests --output=log.$$CI_PIPELINE_ID --wait job.sh && ( egrep -v '.*: *$$|pagefaults|HiWaterMark=' log.$$CI_PIPELINE_ID ; echo Job returned normally ) || ( cat log.$$CI_PIPELINE_ID ; echo Job failed ; exit 911 )
	test -f results.ignore/restart_stats_gnu.tar.gz || ( echo Batch job did not complete ; exit 911 )
	@echo -e "\e[0Ksection_start:`date +%s`:cache[collapsed=true]\r\e[0KCaching results"
	time tar zvcf $(CACHE_DIR)/results-$(CI_PIPELINE_ID).tgz results.*
	@echo -e "\e[0Ksection_end:`date +%s`:cache\r\e[0K"
#&& ( echo -e "\e[0Ksection_start:`date +%s`:joblog[collapsed=true]\r\e[0KJob output" ; cat log.$$CI_PIPELINE_ID ; echo -e "\e[0Ksection_end:`date +%s`:joblog\r\e[0K" )
#|| ( echo -e "\e[0Ksection_start:`date +%s`:joblog[collapsed=true]\r\e[0KJob output" ; cat log.$$CI_PIPELINE_ID ; echo -e "\e[0Ksection_end:`date +%s`:joblog\r\e[0K" ; echo Job failed ; exit 911 )
mom6-pipeline-run-steps:
	time make -f tools/MRS/Makefile.tests all

mom6-pipeline-test-gnu_non_symmetric:
	@echo -e "\e[0Ksection_start:`date +%s`:uncache[collapsed=true]\r\e[0KUncaching results"
	time tar vzxf $(CACHE_DIR)/results-$(CI_PIPELINE_ID).tgz
	@echo -e "\e[0Ksection_end:`date +%s`:uncache\r\e[0K"
	make -f tools/MRS/Makefile.tests gnu_non_symmetric
mom6-pipeline-test-gnu_symmetric:
	@echo -e "\e[0Ksection_start:`date +%s`:uncache[collapsed=true]\r\e[0KUncaching results"
	time tar vzxf $(CACHE_DIR)/results-$(CI_PIPELINE_ID).tgz
	@echo -e "\e[0Ksection_end:`date +%s`:uncache\r\e[0K"
	make -f tools/MRS/Makefile.tests gnu_symmetric
mom6-pipeline-test-gnu_memory:
	@echo -e "\e[0Ksection_start:`date +%s`:uncache[collapsed=true]\r\e[0KUncaching results"
	time tar vzxf $(CACHE_DIR)/results-$(CI_PIPELINE_ID).tgz
	@echo -e "\e[0Ksection_end:`date +%s`:uncache\r\e[0K"
	make -f tools/MRS/Makefile.tests gnu_memory
mom6-pipeline-test-gnu_static:
	@echo -e "\e[0Ksection_start:`date +%s`:uncache[collapsed=true]\r\e[0KUncaching results"
	time tar vzxf $(CACHE_DIR)/results-$(CI_PIPELINE_ID).tgz
	@echo -e "\e[0Ksection_end:`date +%s`:uncache\r\e[0K"
	make -f tools/MRS/Makefile.tests gnu_static
mom6-pipeline-test-gnu_restarts:
	@echo -e "\e[0Ksection_start:`date +%s`:uncache[collapsed=true]\r\e[0KUncaching results"
	time tar vzxf $(CACHE_DIR)/results-$(CI_PIPELINE_ID).tgz
	bash tools/MRS/generate_manifest.sh . tools/MRS/excluded-expts.txt > manifest.mk
	@echo -e "\e[0Ksection_end:`date +%s`:uncache\r\e[0K"
	make -f tools/MRS/Makefile.tests gnu_check_restarts
mom6-pipeline-test-params_gnu_symmetric:
	@echo -e "\e[0Ksection_start:`date +%s`:uncache[collapsed=true]\r\e[0KUncaching results"
	time tar vzxf $(CACHE_DIR)/results-$(CI_PIPELINE_ID).tgz
	@echo -e "\e[0Ksection_end:`date +%s`:uncache\r\e[0K"
	make -f tools/MRS/Makefile.tests params_gnu_symmetric
mom6-pipeline-test-intel_non_symmetric:
	@echo -e "\e[0Ksection_start:`date +%s`:uncache[collapsed=true]\r\e[0KUncaching results"
	time tar vzxf $(CACHE_DIR)/results-$(CI_PIPELINE_ID).tgz
	@echo -e "\e[0Ksection_end:`date +%s`:uncache\r\e[0K"
	make -f tools/MRS/Makefile.tests intel_non_symmetric
mom6-pipeline-test-intel_symmetric:
	@echo -e "\e[0Ksection_start:`date +%s`:uncache[collapsed=true]\r\e[0KUncaching results"
	time tar vzxf $(CACHE_DIR)/results-$(CI_PIPELINE_ID).tgz
	@echo -e "\e[0Ksection_end:`date +%s`:uncache\r\e[0K"
	make -f tools/MRS/Makefile.tests intel_symmetric
mom6-pipeline-test-intel_memory:
	@echo -e "\e[0Ksection_start:`date +%s`:uncache[collapsed=true]\r\e[0KUncaching results"
	time tar vzxf $(CACHE_DIR)/results-$(CI_PIPELINE_ID).tgz
	@echo -e "\e[0Ksection_end:`date +%s`:uncache\r\e[0K"
	make -f tools/MRS/Makefile.tests intel_memory
mom6-pipeline-test-pgi_non_symmetric:
	@echo -e "\e[0Ksection_start:`date +%s`:uncache[collapsed=true]\r\e[0KUncaching results"
	time tar vzxf $(CACHE_DIR)/results-$(CI_PIPELINE_ID).tgz
	@echo -e "\e[0Ksection_end:`date +%s`:uncache\r\e[0K"
	make -f tools/MRS/Makefile.tests pgi_non_symmetric
mom6-pipeline-test-pgi_symmetric:
	@echo -e "\e[0Ksection_start:`date +%s`:uncache[collapsed=true]\r\e[0KUncaching results"
	time tar vzxf $(CACHE_DIR)/results-$(CI_PIPELINE_ID).tgz
	@echo -e "\e[0Ksection_end:`date +%s`:uncache\r\e[0K"
	make -f tools/MRS/Makefile.tests pgi_symmetric
mom6-pipeline-test-pgi_memory:
	@echo -e "\e[0Ksection_start:`date +%s`:uncache[collapsed=true]\r\e[0KUncaching results"
	time tar vzxf $(CACHE_DIR)/results-$(CI_PIPELINE_ID).tgz
	@echo -e "\e[0Ksection_end:`date +%s`:uncache\r\e[0K"
	make -f tools/MRS/Makefile.tests pgi_memory

# SIS2 gitlab pipelines (to be run from above MOM6-examples)
# Note: multiple targets for each job.
# These commands are run before each job stage
# - git clone https://gitlab.gfdl.noaa.gov/ogrp/Gaea-stats-MOM6-examples.git tests
# - cd tests && git submodule init && git submodule update
# - cd MOM6-examples
sis2-pipeline-run:
	@echo -e "\e[0Ksection_start:`date +%s`:uncache[collapsed=true]\r\e[0KUncaching executables"
	tar vzxf $(CACHE_DIR)/build-repro-gnu-$(CI_PIPELINE_ID).tgz
	#tar vzxf $(CACHE_DIR)/build-static-gnu-$(CI_PIPELINE_ID).tgz
	tar vzxf $(CACHE_DIR)/build-repro-intel-$(CI_PIPELINE_ID).tgz
	tar vzxf $(CACHE_DIR)/build-repro-pgi-$(CI_PIPELINE_ID).tgz
	bash tools/MRS/generate_manifest.sh . tools/MRS/excluded-expts.txt > manifest.mk
	time make -f tools/MRS/Makefile.clone .datasets
	@echo -e "\e[0Ksection_end:`date +%s`:uncache\r\e[0K"
	(echo '#!/bin/tcsh';echo 'time make -f tools/MRS/Makefile sis2-pipeline-run-steps') > job.sh
	sbatch --clusters=c4 --nodes=30 --time=1:00:00 --account=gfdl_o --qos=debug --job-name=mom6_examples_tests --output=log.$$CI_PIPELINE_ID --wait job.sh && ( egrep -v '.*: *$$|pagefaults|HiWaterMark=' log.$$CI_PIPELINE_ID ; echo Job returned normally ) || ( cat log.$$CI_PIPELINE_ID ; echo Job failed ; exit 911 )
	test -f results.ignore/restart_stats_gnu.tar.gz || ( echo Batch job did not complete ; exit 911 )
	@echo -e "\e[0Ksection_start:`date +%s`:cache[collapsed=true]\r\e[0KCaching results"
	time tar zvcf $(CACHE_DIR)/results-$(CI_PIPELINE_ID).tgz results.*
	@echo -e "\e[0Ksection_end:`date +%s`:cache\r\e[0K"
#&& ( echo -e "\e[0Ksection_start:`date +%s`:joblog[collapsed=true]\r\e[0KJob output" ; cat log.$$CI_PIPELINE_ID ; echo -e "\e[0Ksection_end:`date +%s`:joblog\r\e[0K" )
#|| ( echo -e "\e[0Ksection_start:`date +%s`:joblog[collapsed=true]\r\e[0KJob output" ; cat log.$$CI_PIPELINE_ID ; echo -e "\e[0Ksection_end:`date +%s`:joblog\r\e[0K" ; echo Job failed ; exit 911 )
sis2-pipeline-run-steps:
	time make -f tools/MRS/Makefile.sis2_tests all

sis2-pipeline-test-gnu_non_symmetric:
	@echo -e "\e[0Ksection_start:`date +%s`:uncache[collapsed=true]\r\e[0KUncaching results"
	time tar vzxf $(CACHE_DIR)/results-$(CI_PIPELINE_ID).tgz
	@echo -e "\e[0Ksection_end:`date +%s`:uncache\r\e[0K"
	make -f tools/MRS/Makefile.sis2_tests gnu_non_symmetric
sis2-pipeline-test-gnu_symmetric:
	@echo -e "\e[0Ksection_start:`date +%s`:uncache[collapsed=true]\r\e[0KUncaching results"
	time tar vzxf $(CACHE_DIR)/results-$(CI_PIPELINE_ID).tgz
	@echo -e "\e[0Ksection_end:`date +%s`:uncache\r\e[0K"
	make -f tools/MRS/Makefile.sis2_tests gnu_symmetric
sis2-pipeline-test-gnu_memory:
	@echo -e "\e[0Ksection_start:`date +%s`:uncache[collapsed=true]\r\e[0KUncaching results"
	time tar vzxf $(CACHE_DIR)/results-$(CI_PIPELINE_ID).tgz
	@echo -e "\e[0Ksection_end:`date +%s`:uncache\r\e[0K"
	make -f tools/MRS/Makefile.sis2_tests gnu_memory
#sis2-pipeline-test-gnu_static:
#	@echo -e "\e[0Ksection_start:`date +%s`:uncache[collapsed=true]\r\e[0KUncaching results"
#	time tar vzxf $(CACHE_DIR)/results-$(CI_PIPELINE_ID).tgz
#	@echo -e "\e[0Ksection_end:`date +%s`:uncache\r\e[0K"
#	make -f tools/MRS/Makefile.sis2_tests gnu_static
sis2-pipeline-test-gnu_restarts:
	@echo -e "\e[0Ksection_start:`date +%s`:uncache[collapsed=true]\r\e[0KUncaching results"
	time tar vzxf $(CACHE_DIR)/results-$(CI_PIPELINE_ID).tgz
	bash tools/MRS/generate_manifest.sh . tools/MRS/excluded-expts.txt > manifest.mk
	@echo -e "\e[0Ksection_end:`date +%s`:uncache\r\e[0K"
	make -f tools/MRS/Makefile.sis2_tests gnu_check_restarts
sis2-pipeline-test-params_gnu_symmetric:
	@echo -e "\e[0Ksection_start:`date +%s`:uncache[collapsed=true]\r\e[0KUncaching results"
	time tar vzxf $(CACHE_DIR)/results-$(CI_PIPELINE_ID).tgz
	@echo -e "\e[0Ksection_end:`date +%s`:uncache\r\e[0K"
	make -f tools/MRS/Makefile.sis2_tests params_gnu_symmetric
sis2-pipeline-test-intel_non_symmetric:
	@echo -e "\e[0Ksection_start:`date +%s`:uncache[collapsed=true]\r\e[0KUncaching results"
	time tar vzxf $(CACHE_DIR)/results-$(CI_PIPELINE_ID).tgz
	@echo -e "\e[0Ksection_end:`date +%s`:uncache\r\e[0K"
	make -f tools/MRS/Makefile.sis2_tests intel_non_symmetric
sis2-pipeline-test-intel_symmetric:
	@echo -e "\e[0Ksection_start:`date +%s`:uncache[collapsed=true]\r\e[0KUncaching results"
	time tar vzxf $(CACHE_DIR)/results-$(CI_PIPELINE_ID).tgz
	@echo -e "\e[0Ksection_end:`date +%s`:uncache\r\e[0K"
	make -f tools/MRS/Makefile.sis2_tests intel_symmetric
sis2-pipeline-test-intel_memory:
	@echo -e "\e[0Ksection_start:`date +%s`:uncache[collapsed=true]\r\e[0KUncaching results"
	time tar vzxf $(CACHE_DIR)/results-$(CI_PIPELINE_ID).tgz
	@echo -e "\e[0Ksection_end:`date +%s`:uncache\r\e[0K"
	make -f tools/MRS/Makefile.sis2_tests intel_memory
sis2-pipeline-test-pgi_non_symmetric:
	@echo -e "\e[0Ksection_start:`date +%s`:uncache[collapsed=true]\r\e[0KUncaching results"
	time tar vzxf $(CACHE_DIR)/results-$(CI_PIPELINE_ID).tgz
	@echo -e "\e[0Ksection_end:`date +%s`:uncache\r\e[0K"
	make -f tools/MRS/Makefile.sis2_tests pgi_non_symmetric
sis2-pipeline-test-pgi_symmetric:
	@echo -e "\e[0Ksection_start:`date +%s`:uncache[collapsed=true]\r\e[0KUncaching results"
	time tar vzxf $(CACHE_DIR)/results-$(CI_PIPELINE_ID).tgz
	@echo -e "\e[0Ksection_end:`date +%s`:uncache\r\e[0K"
	make -f tools/MRS/Makefile.sis2_tests pgi_symmetric
sis2-pipeline-test-pgi_memory:
	@echo -e "\e[0Ksection_start:`date +%s`:uncache[collapsed=true]\r\e[0KUncaching results"
	time tar vzxf $(CACHE_DIR)/results-$(CI_PIPELINE_ID).tgz
	@echo -e "\e[0Ksection_end:`date +%s`:uncache\r\e[0K"
	make -f tools/MRS/Makefile.sis2_tests pgi_memory

# Build for all pipelines
# - always invoked from MOM6-examples
pipeline-build-repro-gnu: $(CACHE_DIR)/build-repro-gnu-$(CI_PIPELINE_ID).tgz
pipeline-build-static-gnu: $(CACHE_DIR)/build-static-gnu-$(CI_PIPELINE_ID).tgz
pipeline-build-debug-gnu: $(CACHE_DIR)/build-debug-gnu-$(CI_PIPELINE_ID).tgz
pipeline-build-repro-intel: $(CACHE_DIR)/build-repro-intel-$(CI_PIPELINE_ID).tgz
pipeline-build-repro-pgi: $(CACHE_DIR)/build-repro-pgi-$(CI_PIPELINE_ID).tgz
$(CACHE_DIR)/build-%-$(CI_PIPELINE_ID).tgz:
	@echo -e "\e[0Ksection_start:`date +%s`:clone-$*[collapsed=true]\r\e[0KCloning submodules"
	test -d src/FMS1/fms && echo Skipping submodule update || ( git submodule init && git submodule update )
	test -f $(MOM6_SRC)/pkg/CVMix-src/README.md || (cd $(MOM6_SRC) && git submodule init && git submodule update)
	make -f tools/MRS/Makefile.clone clone_gfdl -s
	@echo -e "\e[0Ksection_end:`date +%s`:clone-$*\r\e[0K"
	@echo -e "\e[0Ksection_start:`date +%s`:build-$*[collapsed=true]\r\e[0KCompiling executables for $*"
	time make -f tools/MRS/Makefile.build $(subst -,_,$*) -s -j
	@echo -e "\e[0Ksection_end:`date +%s`:build-$*\r\e[0K"
	(test -w $(@D)/ && time tar zvcf $@ `find build/$(lastword $(subst -, ,$*)) -name MOM6`) || echo Not tarring
pipeline-build-gnu-oceanonly-nolibs:
	@echo -e "\e[0Ksection_start:`date +%s`:clone-$*[collapsed=true]\r\e[0KCloning submodules"
	#time make -f tools/MRS/Makefile $(subst -,_,$*) -s -j
	test -d src/FMS1/fms && echo Skipping submodule update || ( git submodule init && git submodule update )
	test -f ../../pkg/CVMix-src/README.md || (cd ../.. && git submodule init && git submodule update)
	@echo -e "\e[0Ksection_end:`date +%s`:clone-$*\r\e[0K"
	@echo -e "\e[0Ksection_start:`date +%s`:build-$*[collapsed=true]\r\e[0KCompiling executables for $*"
	make -f tools/MRS/Makefile.build build/gnu/env
	cd build/gnu && ../../src/mkmf/bin/list_paths -l ../../$(MOM6_SRC)/config_src/{drivers/solo_driver,memory/dynamic_symmetric,infra/FMS1,ext*} ../../$(MOM6_SRC)/src ../../src/FMS
	cd build/gnu && sed -i '/FMS\/.*\/test_/d' path_names
	cd build/gnu && ../../src/mkmf/bin/mkmf -t ../../src/mkmf/templates/ncrc-gnu.mk -p MOM6 -c"-Duse_libMPI -Duse_netCDF" path_names
	cd build/gnu && time (source ./env ; make NETCDF=3 REPRO=1 MOM6 -s -j)
	@echo -e "\e[0Ksection_end:`date +%s`:build-$*\r\e[0K"
pipeline-build-gnu-iceocean-nolibs:
	@echo -e "\e[0Ksection_start:`date +%s`:clone-$*[collapsed=true]\r\e[0KCloning submodules"
	test -d src/FMS1/fms && echo Skipping submodule update || ( git submodule init && git submodule update )
	test -f ../../pkg/CVMix-src/README.md || (cd ../.. && git submodule init && git submodule update)
	@echo -e "\e[0Ksection_end:`date +%s`:clone-$*\r\e[0K"
	@echo -e "\e[0Ksection_start:`date +%s`:build-$*[collapsed=true]\r\e[0KCompiling executables for $*"
	make -f tools/MRS/Makefile.build build/gnu/env
	cd build/gnu && ../../src/mkmf/bin/list_paths -l ../../$(MOM6_SRC)/config_src/{drivers/FMS_cap,memory/dynamic_nonsymmetric,infra/FMS1,ext*} ../../$(MOM6_SRC)/src ../../$(SIS2_SRC)/*src ../../src/{FMS,coupler,icebergs,ice_param,land_null,atmos_null}
	cd build/gnu && sed -i '/FMS\/.*\/test_/d' path_names
	cd build/gnu && ../../src/mkmf/bin/mkmf -t ../../src/mkmf/templates/ncrc-gnu.mk -p MOM6 -c"-Duse_libMPI -Duse_netCDF -D_USE_LEGACY_LAND_ -Duse_AM3_physics" path_names
	cd build/gnu && time (source ./env ; make NETCDF=3 REPRO=1 MOM6 -s -j)
	@echo -e "\e[0Ksection_end:`date +%s`:build-$*\r\e[0K"

# Gaea-stats-MOM6-examples gitlab pipelines (to be run from above MOM6-examples)
# Note: multiple targets for each job.
# These commands are run before each job stage
# - recursively clone submodules
# - clone other components
# - link to data sets
stats-pipeline-pre-script:
	echo Cache directory env var = $(CACHE_DIR)
	test -f MOM6-examples/README.md || git submodule init && git submodule update

# Run model
# - Fetch executables from cache
# - Create the manifest
# - Use Makefile.test to create tar files of the ocean.stats "in place" within MOM6-examples
# - Check the last was written
# - Cache all the tar files
stats-pipeline-run: $(CACHE_DIR)/results-$(CI_PIPELINE_ID).tgz
$(CACHE_DIR)/results-$(CI_PIPELINE_ID).tgz:
	@echo -e "\e[0Ksection_start:`date +%s`:uncache[collapsed=true]\r\e[0KUncaching executables"
	time tar vzxf $(CACHE_DIR)/build-repro-gnu-$(CI_PIPELINE_ID).tgz
	time tar vzxf $(CACHE_DIR)/build-repro-intel-$(CI_PIPELINE_ID).tgz
	time tar vzxf $(CACHE_DIR)/build-repro-pgi-$(CI_PIPELINE_ID).tgz
	bash tools/MRS/generate_manifest.sh . tools/MRS/excluded-expts.txt > manifest.mk
	make -f tools/MRS/Makefile.clone .datasets
	@echo -e "\e[0Ksection_end:`date +%s`:uncache\r\e[0K"
	@echo -e "\e[0Ksection_start:`date +%s`:run[collapsed=true]\r\e[0KRunning models"
	(echo '#!/bin/tcsh';echo 'time make -f tools/MRS/Makefile.run all -s -j') > job.sh
	sbatch --clusters=c4 --nodes=30 --time=0:12:00 --account=gfdl_o --qos=debug --job-name=mom6_full_regression --output=log.$(CI_PIPELINE_ID) --wait job.sh && ( echo -e "\e[0Ksection_start:`date +%s`:job-log[collapsed=true]\r\e[0KJob log" ; cat log.$(CI_PIPELINE_ID) ; echo -e "\e[0Ksection_end:`date +%s`:job-log\r\e[0K" ; echo Job returned normally ) || ( echo -e "\e[0Ksection_start:`date +%s`:job-log[collapsed=true]\r\e[0KJob log" ; cat log.$(CI_PIPELINE_ID) ; echo -e "\e[0Ksection_end:`date +%s`:job-log\r\e[0K" ; echo Job failed ; exit 911 )
	@echo -e "\e[0Ksection_end:`date +%s`:run\r\e[0K"
	@echo -e "\e[0Ksection_start:`date +%s`:cache[collapsed=true]\r\e[0KCaching results"
	time tar zvcf $@ `find . -name *.stats.*[a-z][a-z][a-z]` log.$(CI_PIPELINE_ID)
	@echo -e "\e[0Ksection_end:`date +%s`:cache\r\e[0K"

# Tests
# - unpack cached ocean.stats files
stats-pipeline-test:
	@echo -e "\e[0Ksection_start:`date +%s`:uncache[collapsed=true]\r\e[0KUncaching results"
	cd ../
	time tar vzxf $(CACHE_DIR)/results-$(CI_PIPELINE_ID).tgz
	@echo -e "\e[0Ksection_end:`date +%s`:uncache\r\e[0K"
	git status
	git diff --exit-code

# Manifest of experiments to run. This target scans the layout log files for PE sets, so assumes all are present and correct (clean checkout).
MANIFEST ?= $(MPTH)manifest.mk
manifest: $(MANIFEST)
$(MANIFEST): $(MPTH)excluded-expts.txt
	bash $(MPTH)/generate_manifest.sh $(CONFIGS) $< > $@

# `make run_sym`
# `make run_nonsym`
MEMORY ?= dynamic_symmetric
run_sym: MEMORY=dynamic_symmetric
run_nonsym: MEMORY=dynamic_nonsymmetric
run run_sym run_nonsym: gnu_all intel_all pgi_all
gnu_all intel_all pgi_all:
	$(MAKE) -f $(MPTH)/Makefile.run MEMORY=$(MEMORY) $@
