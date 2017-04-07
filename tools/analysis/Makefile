# Makefile to test the analysis scripts called by frepp.

# Uncomment this link to put files into a folder
# OUTOPTS = -o tmp/

# Note that the matplotlib png checksums are repeatable, based on the lack of any
# additional metadata encoded in the png file.  These checksums can be used to 
# validate analysis figures.

# Settings for the 0.5 degree configuration
EXPDIR = /archive/John.Dunne/ulm_201505_awg_v20151106_mom6sis2_2015.12.17/CM4_c96L32_am4g7_2000_OMp5_DR_H3_MEKE/gfdl.ncrc2-intel-prod-openmp
GRIDSPEC = /archive/gold/datasets/OM4_05/mosaic.v20151203.unpacked
WOA = /archive/gold/datasets/OM4_05/obs/WOA05_ptemp_salt_annual.v2015.12.03.nc
WOA_M = /archive/gold/datasets/OM4_05/obs/WOA05_ptemp_salt_monthly.v2015.12.03.nc

# Settings for the 0.25 degree configuration
#EXPDIR = /archive/ogrp/verona_201701_awg_v20170208_g12_mom6_2017.03.17/CM4_c96L32_g12r17_2010_OM25_10d_s3lt_FK10/gfdl.ncrc4-intel15c3exec-prod-openmp
#GRIDSPEC = /archive/gold/datasets/OM4_025/mosaic.v20140610.tar
#WOA =  /archive/gold/datasets/OM4_025/obs/WOA05_ptemp_salt_annual.v20150310.nc
#WOA_M = /archive/gold/datasets/OM4_025/obs/WOA05_ptemp_salt_monthly.v20150310.nc

all: sst sst_monthly sss zonalT zonalS zave sections moc mld heattransport checksums

sst:
	./SST_bias_WOA05.py -w $(WOA) -g $(GRIDSPEC) -l 0001-0005 $(EXPDIR)/pp/ocean_annual_z/av/annual_5yr/ocean_annual_z.0001-0005.ann.nc $(OUTOPTS)

sst_monthly:
	./SST_monthly_bias_WOA05.py -w $(WOA_M) -g $(GRIDSPEC) -l 0001-0005 $(EXPDIR)/pp/ocean_monthly/av/monthly_5yr/ocean_monthly.0001-0005.01.nc $(EXPDIR)/pp/ocean_monthly/av/monthly_5yr/ocean_monthly.0001-0005.08.nc $(OUTOPTS)

sss:
	./SSS_bias_WOA05.py -w $(WOA) -g $(GRIDSPEC) -l 0001-0005 $(EXPDIR)/pp/ocean_annual_z/av/annual_5yr/ocean_annual_z.0001-0005.ann.nc $(OUTOPTS)

zonalT:
	./zonal_T_bias_WOA05.py -w $(WOA) -g $(GRIDSPEC) -l 0001-0005 $(EXPDIR)/pp/ocean_annual_z/av/annual_5yr/ocean_annual_z.0001-0005.ann.nc $(OUTOPTS)

zonalS:
	./zonal_S_bias_WOA05.py -w $(WOA) -g $(GRIDSPEC) -l 0001-0005 $(EXPDIR)/pp/ocean_annual_z/av/annual_5yr/ocean_annual_z.0001-0005.ann.nc $(OUTOPTS)

zave:
	./depth_average_T_bias.py -zb 100 -w $(WOA) -g $(GRIDSPEC) -l 0001-0005 $(EXPDIR)/pp/ocean_annual_z/av/annual_5yr/ocean_annual_z.0001-0005.ann.nc $(OUTOPTS)
	./depth_average_T_bias.py -zb 300 -w $(WOA) -g $(GRIDSPEC) -l 0001-0005 $(EXPDIR)/pp/ocean_annual_z/av/annual_5yr/ocean_annual_z.0001-0005.ann.nc $(OUTOPTS)
	./depth_average_T_bias.py -zb 700 -w $(WOA) -g $(GRIDSPEC) -l 0001-0005 $(EXPDIR)/pp/ocean_annual_z/av/annual_5yr/ocean_annual_z.0001-0005.ann.nc $(OUTOPTS)
	./depth_average_T_bias.py -zb 2000 -w $(WOA) -g $(GRIDSPEC) -l 0001-0005 $(EXPDIR)/pp/ocean_annual_z/av/annual_5yr/ocean_annual_z.0001-0005.ann.nc $(OUTOPTS)
	./depth_average_T_bias.py -zb 6500 -w $(WOA) -g $(GRIDSPEC) -l 0001-0005 $(EXPDIR)/pp/ocean_annual_z/av/annual_5yr/ocean_annual_z.0001-0005.ann.nc $(OUTOPTS)

sections:
	./vertical_sections_annual_bias_WOA05.py -w $(WOA) -g $(GRIDSPEC) -l 0001-0005 $(EXPDIR)/pp/ocean_annual_z/av/annual_5yr/ocean_annual_z.0001-0005.ann.nc $(OUTOPTS)

moc:
	./meridional_overturning.py -g $(GRIDSPEC) $(EXPDIR)/pp/ocean_annual_z/av/annual_5yr/ocean_annual_z.0001-0005.ann.nc $(OUTOPTS)

mld:
	./MLD_003.py -g $(GRIDSPEC) $(EXPDIR)/pp/ocean_monthly/ts/monthly/5yr/ocean_monthly.000101-000512.MLD_003.nc $(OUTOPTS)

heattransport:
	./poleward_heat_transport.py -l 0001-0005 -g $(GRIDSPEC) $(EXPDIR)/pp/ocean_annual/av/annual_5yr/ocean_annual.0001-0005.ann.nc $(OUTOPTS)

checksums:
	md5sum *.png > analysis_figure_checksums.md5

clean:
	rm -f *.png analysis_figure_checksums.md5
