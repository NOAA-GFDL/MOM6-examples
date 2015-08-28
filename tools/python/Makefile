# Makefile to create supergrid.nc and interpolated_topog.nc
# To use:
#   module load python
#   setenv PYTHONPATH $cwd/MIDAS
#
# then
#   make all
# or
#   make supergrid.nc
#   make interpolated_topog.nc

SHELL=tcsh -f

all: local

showenv:
	env
	-set
	-module list
	which python
	-python --version

MIDAS:
	git clone https://github.com/mjharriso/MIDAS.git
	(cd MIDAS; git checkout 446ea813e2d64a4a10f8209deea905bed64bc1b0)

# Submodule method for obtaining MIDAS (used by frepp_local target) 
MIDAS/README.md:
	(cd ../..; git submodule init tools/python/MIDAS)
	(cd ../..; git submodule update tools/python/MIDAS)

local: MIDAS 
	-rm -rf $</build/*
	mkdir -p $@
	cd $<; make -f Makefile_GFDL INSTALL_PATH=../local
	touch $@

# This is a target to allow frepp analysis scripts to build MIDAS only once and then clean up
frepp_local: MIDAS/README.md
	make local
	rm -rf MIDAS
	mkdir MIDAS
	touch $<
	touch local
