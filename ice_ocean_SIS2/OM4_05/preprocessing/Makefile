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
NP=8

all: ocean_grid ocean_mosaic c96_mosaic c192_mosaic forcing obs
	md5sum -c md5sums.txt

showenv:
	env
	-set
	-module list
	which python
	-python --version

forcing: salt_restore.nc seawifs_1998-2006_smoothed_2X.nc tidal_amplitude.nc mosaic_ocean.720x576/runoff.daitren.clim.v2011.02.10.720x576.nc mosaic_ocean.720x576/runoff.daitren.iaf.v2011.02.10.720x576.nc geothermal_davies2013_v1.nc

obs: WOA05_ptemp_salt_monthly.nc WOA05_ptemp_salt_annual.nc

# Grids
ocean_grid: ocean_hgrid.nc supergrid.nc mercator_supergrid.nc ncap_supergrid.nc antarctic_spherical_supergrid.nc
ocean_hgrid.nc supergrid.nc mercator_supergrid.nc ncap_supergrid.nc antarctic_spherical_supergrid.nc: OM4_05_grid/ocean_hgrid.nc
	cp OM4_05_grid/$@ $@
OM4_05_grid/ocean_hgrid.nc: OM4_05_grid/Makefile
	cd $(@D); make
OM4_05_grid/Makefile:
	git clone https://github.com/adcroft/OM4_05_grid.git

# Topography
interpolated_topog.nc: ncap_topog.nc ncap_topog_gebco.nc mercator_topog_gebco.nc so_topog_gebco.nc local
	unlimit stacksize; setenv PYTHONPATH ./local/lib/python; python merge_topog_tiles.py

ncap_topog.nc: ncap_supergrid.nc IBCAO_V3_500m_RR.grd local
	unlimit stacksize; setenv PYTHONPATH ./local/lib/python; python create_topo.py ncap

ncap_topog_gebco.nc: ncap_supergrid.nc GEBCO_08_v1.nc local
	unlimit stacksize; setenv PYTHONPATH ./local/lib/python; python create_topo.py ncap --use_gebco

mercator_topog_gebco.nc: mercator_supergrid.nc GEBCO_08_v1.nc local
	unlimit stacksize; setenv PYTHONPATH ./local/lib/python; python create_topo.py mercator

so_topog_bedmap2.nc: antarctic_spherical_supergrid.nc bedmap2.nc local
	unlimit stacksize; setenv PYTHONPATH ./local/lib/python; python create_topo.py scap

so_topog_gebco.nc: antarctic_spherical_supergrid.nc GEBCO_08_v1.nc local
	unlimit stacksize; setenv PYTHONPATH ./local/lib/python; python create_topo.py scap --use_gebco

edit_topog.nc: interpolated_topog.nc
	\cp $< $@
	./apply_edits.py topo_edits_020718.nc edit_topog.nc
topog.nc: edit_topog.nc
	\cp $< $@

ocean_topog.nc: topog.nc
	\cp $< $@
	setenv PYTHONPATH ./local/lib/python; python add_h2.py

basin_codes.nc: ocean_topog.nc
	unlimit stacksize; setenv PYTHONPATH ./local/lib/python; python make_basin_mask.py
	ncatted -h -a flag_meanings,basin,c,c,'1:Southern Ocean, 2:Atlantic Ocean, 3:Pacific Ocean, 4:Arctic Ocean, 5:Indian Ocean, 6:Mediterranean Sea, 7:Black Sea, 8:Hudson Bay, 9:Baltic Sea, 10:Red Sea, 11:Persian Gulf' basin_codes.nc
	ncatted -h -a flag_values,basin,c,c,'1,2,3,4,5,6,7,8,9,10,11' basin_codes.nc

WOA05_ptemp_salt_annual.nc: WOA05_ptemp_salt_monthly.nc
	ncra -h -O $< $@

WOA05_ptemp_salt_monthly.nc: ocean_hgrid.nc ocean_topog.nc  interpWOA05.py local
	unlimit stacksize; setenv PYTHONPATH ./local/lib/python; python interpWOA05.py
	ncatted -h -a modulo,TIME,c,c,' ' WOA05_ptemp_salt_monthly.nc

salt_restore.nc: ocean_hgrid.nc ocean_topog.nc PHC2_salx.2004_08_03.nc interpSaltRestore.py local
	unlimit stacksize; setenv PYTHONPATH ./local/lib/python; python interpSaltRestore.py
#	ncatted -h -a modulo,time,c,c,' ' salt_restore.nc
#	ncatted -h -a units,time,m,c,'days since 1900-01-01 00:00:00' salt_restore.nc


seawifs_1998-2006_smoothed_2X.nc: ocean_hgrid.nc ocean_topog.nc /archive/gold/datasets/global/siena_201204/INPUT/seawifs_1998-2006_GOLD_smoothed_2X.nc interpCHL.py local
	unlimit stacksize; setenv PYTHONPATH ./local/lib/python; python interpCHL.py
	ncatted -h -a modulo,TIME,c,c,' ' seawifs_1998-2006_smoothed_2X.nc

geothermal_davies2013_v1.nc: OM4_05_preprocessing_geothermal/geothermal_davies2013_v1.nc
	cp $^ $@
OM4_05_preprocessing_geothermal/geothermal_davies2013_v1.nc: OM4_05_preprocessing_geothermal/Makefile
	cp ocean_hgrid.nc $(@D)/
	cd $(@D); make
OM4_05_preprocessing_geothermal/Makefile:
	git clone https://github.com/adcroft/OM4_05_preprocessing_geothermal.git

tidal_amplitude.nc: DATA interpTides.py ocean_topog.nc local
	unlimit stacksize; setenv PYTHONPATH ./local/lib/python; python interpTides.py


DATA: tpxo7_atlas_netcdf.tar.Z
	tar xzvf tpxo7_atlas_netcdf.tar.Z
	touch DATA

tpxo7_atlas_netcdf.tar.Z:
	wget ftp://ftp.oce.orst.edu/dist/tides/Global/tpxo7_atlas_netcdf.tar.Z

PHC2_salx.2004_08_03.nc:
	wget http://data1.gfdl.noaa.gov/~nnz/mom4/COREv1/support_data/PHC2_salx.2004_08_03.nc

MIDAS:
	git clone https://github.com/mjharriso/MIDAS.git
	(cd MIDAS; git checkout fd8160cf259fd33009749ee8d7cb4e7281ed0293)

local: MIDAS
	-rm -rf $</build/*
	mkdir -p $@
	cd $<; make -f Makefile_GFDL INSTALL_PATH=../local
	touch $@

bedmap2.nc GEBCO_08_v1.nc IBCAO_V3_500m_RR.grd:
	cp /archive/gold/datasets/topography/$@ .

FRE_NCTOOLS = fre_nctools/tools

fre_nctools:
	echo $@
	git clone http://gitlab.gfdl.noaa.gov/fre/fre-nctools.git $@
	(cd $@; git checkout 168f6a5a2717bc80961da6ba751509cd8c7ace0d)
#	(cd $@; git checkout user/z1l/dev)
fre_nctools/tools: fre_nctools
fre_nctools/tools/make_solo_mosaic/make_solo_mosaic fre_nctools/tools/make_quick_mosaic/make_quick_mosaic \
fre_nctools/tools/make_coupler_mosaic/make_coupler_mosaic fre_nctools/tools/make_coupler_mosaic/make_coupler_mosaic_parallel\
fre_nctools/tools/runoff_regrid/runoff_regrid fre_nctools/tools/runoff_regrid/runoff_regrid_parallel: fre_nctools/tools
	(cd $(@D); make SITE=pan -f fre-nctools.mk $(@F))

OCN_MOSAIC = $(foreach f,atmos_mosaic_tile1Xland_mosaic_tile1.cdl atmos_mosaic_tile1Xocean_mosaic_tile1.cdl grid_spec.cdl land_mask.cdl\
                         land_mosaic_tile1Xocean_mosaic_tile1.cdl ocean_mask.cdl ocean_mosaic.cdl runoff.daitren.clim.v2011.02.10.720x576.nc runoff.daitren.iaf.v2011.02.10.720x576.nc,mosaic_ocean.720x576/$f)
C96_MOSAIC = $(foreach f,C96_grid.tile1.nc C96_grid.tile2.nc C96_grid.tile3.nc C96_grid.tile4.nc C96_grid.tile5.nc C96_grid.tile6.nc C96_mosaic.nc\
                         C96_mosaic_tile1XC96_mosaic_tile1.cdl C96_mosaic_tile1Xocean_mosaic_tile1.cdl C96_mosaic_tile2XC96_mosaic_tile2.cdl C96_mosaic_tile2Xocean_mosaic_tile1.cdl\
                         C96_mosaic_tile3XC96_mosaic_tile3.cdl C96_mosaic_tile3Xocean_mosaic_tile1.cdl C96_mosaic_tile4XC96_mosaic_tile4.cdl C96_mosaic_tile4Xocean_mosaic_tile1.cdl\
                         C96_mosaic_tile5XC96_mosaic_tile5.cdl C96_mosaic_tile5Xocean_mosaic_tile1.cdl C96_mosaic_tile6XC96_mosaic_tile6.cdl C96_mosaic_tile6Xocean_mosaic_tile1.cdl\
                         land_mask_tile1.cdl land_mask_tile2.cdl land_mask_tile3.cdl land_mask_tile4.cdl land_mask_tile5.cdl land_mask_tile6.cdl\
                         mosaic.cdl ocean_mask.cdl,mosaic_c96.720x576/$f)
C192_MOSAIC = $(foreach f,C192_grid.tile1.nc C192_grid.tile2.nc C192_grid.tile3.nc C192_grid.tile4.nc C192_grid.tile5.nc C192_grid.tile6.nc C192_mosaic.nc\
                          C192_mosaic_tile1XC192_mosaic_tile1.cdl C192_mosaic_tile1Xocean_mosaic_tile1.cdl C192_mosaic_tile2XC192_mosaic_tile2.cdl C192_mosaic_tile2Xocean_mosaic_tile1.cdl\
                          C192_mosaic_tile3XC192_mosaic_tile3.cdl C192_mosaic_tile3Xocean_mosaic_tile1.cdl C192_mosaic_tile4XC192_mosaic_tile4.cdl C192_mosaic_tile4Xocean_mosaic_tile1.cdl\
                          C192_mosaic_tile5XC192_mosaic_tile5.cdl C192_mosaic_tile5Xocean_mosaic_tile1.cdl C192_mosaic_tile6XC192_mosaic_tile6.cdl C192_mosaic_tile6Xocean_mosaic_tile1.cdl\
                          land_mask_tile1.cdl land_mask_tile2.cdl land_mask_tile3.cdl land_mask_tile4.cdl land_mask_tile5.cdl land_mask_tile6.cdl\
                          mosaic.cdl ocean_mask.cdl,mosaic_c192.720x576/$f)
ocean_mosaic: $(OCN_MOSAIC) basin_codes.nc
c96_mosaic: $(C96_MOSAIC)
c192_mosaic: $(C192_MOSAIC)

$(filter-out mosaic_ocean.720x576/grid_spec.nc mosaic_ocean.720x576/ocean_mosaic.nc,$(OCN_MOSAIC:.cdl=.nc)): mosaic_ocean.720x576/grid_spec.nc
mosaic_ocean.720x576/ocean_mosaic.nc: ocean_hgrid.nc ocean_topog.nc $(FRE_NCTOOLS)/make_solo_mosaic/make_solo_mosaic
	mkdir -p $(@D)
	(cd $(@D); ln -sf ../ocean_hgrid.nc ../ocean_topog.nc .)
	(cd $(@D); ../$(FRE_NCTOOLS)/make_solo_mosaic/make_solo_mosaic --num_tiles 1 --dir . --mosaic_name ocean_mosaic --tile_file ocean_hgrid.nc --periodx 360.)
mosaic_ocean.720x576/grid_spec.nc: mosaic_ocean.720x576/ocean_mosaic.nc $(FRE_NCTOOLS)/make_quick_mosaic/make_quick_mosaic
	(cd $(@D); ../$(FRE_NCTOOLS)/make_quick_mosaic/make_quick_mosaic --reproduce_siena --input_mosaic ocean_mosaic.nc --mosaic_name grid_spec --ocean_topog ocean_topog.nc )

mosaic_ocean.720x576/runoff_tmp.nc: fre_nctools/tools/runoff_regrid/runoff_regrid_parallel mosaic_ocean.720x576/ocean_mosaic.nc mosaic_ocean.720x576/ocean_topog.nc
	(cd $(@D); time mpirun -np $(NP) ../fre_nctools/tools/runoff_regrid/runoff_regrid_parallel --input_file ../runoff.daitren.clim.v2011.02.10.nc --input_fld_name runoff --output_mosaic ocean_mosaic.nc --output_topog ocean_topog.nc --output_file $(@F))
mosaic_ocean.720x576/runoff.daitren.clim.v2011.02.10.720x576.nc: mosaic_ocean.720x576/runoff_tmp.nc
	(cd $(@D); ncks -h -3 runoff_tmp.nc $(@F))
	(cd $(@D); ncatted -h -O -a 'modulo,Time,c,c, ' $(@F))

mosaic_ocean.720x576/runoff_tmp2.nc: fre_nctools/tools/runoff_regrid/runoff_regrid_parallel mosaic_ocean.720x576/ocean_mosaic.nc mosaic_ocean.720x576/ocean_topog.nc
	(cd $(@D); time mpirun -np $(NP) ../fre_nctools/tools/runoff_regrid/runoff_regrid_parallel --input_file ../runoff.daitren.iaf.v2011.02.10.nc --input_fld_name runoff --output_mosaic ocean_mosaic.nc --output_topog ocean_topog.nc --output_file $(@F))
mosaic_ocean.720x576/runoff.daitren.iaf.v2011.02.10.720x576.nc: mosaic_ocean.720x576/runoff_tmp2.nc
	(cd $(@D); ncks -h -3 runoff_tmp2.nc $(@F))
	(cd $(@D); ncatted -h -O -a 'modulo,Time,c,c, ' $(@F))

$(filter-out mosaic_c96.720x576/mosaic.nc,$(C96_MOSAIC:.cdl=.nc)): mosaic_c96.720x576/mosaic.nc
mosaic_c96.720x576/mosaic.nc: mosaic_ocean.720x576/ocean_mosaic.nc ocean_topog.nc $(FRE_NCTOOLS)/make_coupler_mosaic/make_coupler_mosaic_parallel
	mkdir -p $(@D)
	(cd $(@D); ln -sf ../ocean_hgrid.nc ../ocean_topog.nc .)
	(cd $(@D); ln -sf ../mosaic_ocean.720x576/ocean_mosaic.nc .)
	(cd $(@D); tar xf /archive/cjg/awg/input/grid/C96_CM2G_grid.tar C96_grid.\* C96_mosaic.nc)
	(cd $(@D); time mpirun -np $(NP) ../$(FRE_NCTOOLS)/make_coupler_mosaic/make_coupler_mosaic_parallel --reproduce_siena --atmos_mosaic C96_mosaic.nc --ocean_mosaic ocean_mosaic.nc --mosaic_name mosaic --ocean_topog ocean_topog.nc)

$(filter-out mosaic_c192.720x576/mosaic.nc,$(C192_MOSAIC:.cdl=.nc)): mosaic_c192.720x576/mosaic.nc
mosaic_c192.720x576/mosaic.nc: mosaic_ocean.720x576/ocean_mosaic.nc ocean_topog.nc $(FRE_NCTOOLS)/make_coupler_mosaic/make_coupler_mosaic_parallel
	mkdir -p $(@D)
	(cd $(@D); ln -sf ../ocean_hgrid.nc ../ocean_topog.nc .)
	(cd $(@D); ln -sf ../mosaic_ocean.720x576/ocean_mosaic.nc .)
	(cd $(@D); tar xf /archive/cjg/awg/input/grid/c192_CM2_grid_20130423.tar C192_grid.\* C192_mosaic.nc)
	(cd $(@D); time mpirun -np $(NP) ../$(FRE_NCTOOLS)/make_coupler_mosaic/make_coupler_mosaic_parallel --reproduce_siena --atmos_mosaic C192_mosaic.nc --ocean_mosaic ocean_mosaic.nc --mosaic_name mosaic --ocean_topog ocean_topog.nc)

%.cdl: %.nc
	ncdump $< | egrep -v 'code_version|history' > $@

clean:
	-rm -rf fre_nctools local MIDAS OM4_05_* DATA mosaic_*
	-rm -f *grid.nc salt*.nc seaw*.nc tidal_*.nc WOA*.nc geoth*.nc *topog*.nc PHC*.nc basin*.nc logfile* input.nml runoff*.nc

md5sums.txt: ocean_hgrid.nc antarctic_spherical_supergrid.nc mercator_supergrid.nc ncap_supergrid.nc supergrid.nc interpolated_topog.nc mercator_topog_gebco.nc ncap_topog_gebco.nc ncap_topog.nc so_topog_gebco.nc ocean_topog.nc $(OCN_MOSAIC) $(C96_MOSAIC) $(C192_MOSAIC) basin_codes.nc salt_restore.nc seawifs_1998-2006_smoothed_2X.nc tidal_amplitude.nc WOA05_ptemp_salt_monthly.nc WOA05_ptemp_salt_annual.nc geothermal_davies2013_v1.nc mosaic_ocean.720x576/runoff.daitren.iaf.v2011.02.10.720x576.nc mosaic_ocean.720x576/runoff.daitren.clim.v2011.02.10.720x576.nc
	echo Grids > $@
	md5sum *supergrid.nc ocean_hgrid.nc >> $@
	echo >> $@
	echo Topography >> $@
	md5sum *topog*.nc >> $@
	md5sum basin_codes.nc >> $@
	echo >> $@
	echo Mosaics >> $@
	md5sum $(OCN_MOSAIC) >> $@
	md5sum $(C96_MOSAIC) >> $@
	md5sum $(C192_MOSAIC) >> $@
	echo >> $@
	echo Data >> $@
	md5sum salt_restore.nc seawifs_1998-2006_smoothed_2X.nc tidal_amplitude.nc >> $@
	md5sum geothermal_davies2013_v1.nc >> $@
	echo >> $@
	echo Obs >> $@
	md5sum WOA05_ptemp_salt_{monthly,annual}.nc >> $@
