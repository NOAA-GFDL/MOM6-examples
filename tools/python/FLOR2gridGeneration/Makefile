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

all: input forcing obs
	md5sum -c md5sums.txt

showenv:
	env
	-set
	-module list
	which python
	-python --version

input: ocean_hgrid.nc topog.nc basin_codes.nc

forcing: salt_restore.nc seawifs_1998-2006_smoothed_2X.nc tidal_amplitude.nc

obs: WOA05_ptemp_salt_monthly.nc WOA05_ptemp_salt_annual.nc

# Grid

ocean_hgrid.nc: local
	unlimit stacksize; setenv PYTHONPATH ./local/lib/python; python create_grids.py
	unlimit stacksize; setenv PYTHONPATH ./local/lib/python; python merge_grids.py
	./changeChar.py ocean_hgrid.nc tile tile1

# Topography
interpolated_topog.nc: ocean_hgrid.nc
	unlimit stacksize; setenv PYTHONPATH ./local/lib/python; python create_topo.py


topog.nc: edit_topog.nc interpolated_topog.nc
	./ice9.py edit_topog.nc --output topog.nc

basin_codes.nc: topog.nc
	unlimit stacksize; setenv PYTHONPATH ./local/lib/python; python make_basin_mask.py
	ncatted -h -a flag_meanings,basin,c,c,'1:Southern Ocean, 2:Atlantic Ocean, 3:Pacific Ocean, 4:Arctic Ocean, 5:Indian Ocean, 6:Mediterranean Sea, 7:Black Sea, 8:Hudson Bay, 9:Baltic Sea, 10:Red Sea, 11:Persian Gulf' basin_codes.nc
	ncatted -h -a flag_values,basin,c,c,'1,2,3,4,5,6,7,8,9,10,11' basin_codes.nc

WOA05_ptemp_salt_annual.nc: WOA05_ptemp_salt_monthly.nc
	ncra -h -O $< $@

WOA05_ptemp_salt_monthly.nc: ocean_hgrid.nc topog.nc /archive/gold/datasets/obs/WOA05_pottemp_salt.nc interpWOA05.py local
	unlimit stacksize; setenv PYTHONPATH ./local/lib/python; python interpWOA05.py
	ncatted -h -a modulo,TIME,c,c,' ' WOA05_ptemp_salt_monthly.nc

salt_restore.nc: ocean_hgrid.nc topog.nc /archive/gold/datasets/obs/WOA05_pottemp_salt.nc interpSaltRestore.py local
	unlimit stacksize; setenv PYTHONPATH ./local/lib/python; python interpSaltRestore.py
	ncatted -h -a modulo,TIME,c,c,' ' salt_restore.nc

seawifs_1998-2006_smoothed_2X.nc: ocean_hgrid.nc topog.nc /archive/gold/datasets/global/siena_201204/INPUT/seawifs_1998-2006_GOLD_smoothed_2X.nc interpCHL.py local
	unlimit stacksize; setenv PYTHONPATH ./local/lib/python; python interpCHL.py
	ncatted -h -a modulo,TIME,c,c,' ' seawifs_1998-2006_smoothed_2X.nc

tidal_amplitude.nc: DATA interpTides.py local
	unlimit stacksize; setenv PYTHONPATH ./local/lib/python; python interpTides.py

DATA: tpxo7_atlas_netcdf.tar.Z GEBCO_08_v2.nc
	tar xzvf tpxo7_atlas_netcdf.tar.Z
	touch DATA

tpxo7_atlas_netcdf.tar.Z:
	wget ftp://ftp.oce.orst.edu/dist/tides/Global/tpxo7_atlas_netcdf.tar.Z

MIDAS:
	git clone https://github.com/mjharriso/MIDAS.git

# Submodule method for obtaining MIDAS (used by frepp_local target) 
MIDAS/README.md:
	(cd ../../..; git submodule init tools/python/025gridGeneration/MIDAS)
	(cd ../../..; git submodule update tools/python/025gridGeneration/MIDAS)

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

GEBCO_08_v2.nc :
	cp /archive/gold/datasets/topography/$@ .

md5sums.txt: ocean_hgrid.nc  interpolated_topog.nc topog.nc basin_codes.nc salt_restore.nc seawifs_1998-2006_smoothed_2X.nc tidal_amplitude.nc WOA05_ptemp_salt_monthly.nc WOA05_ptemp_salt_annual.nc
	echo Grids > $@
	md5sum sgrid*.nc ocean_hgrid.nc >> $@
	echo >> $@
	echo Topography >> $@
	md5sum *topog*.nc >> $@
	md5sum basin_codes.nc >> $@
	echo >> $@
	echo Data >> $@
	md5sum salt_restore.nc seawifs_1998-2006_smoothed_2X.nc tidal_amplitude.nc >> $@
	echo >> $@
	echo Obs >> $@
	md5sum WOA05_ptemp_salt_{monthly,annual}.nc >> $@
