# Makefile to test the analysis scripts called by frepp.

# Uncomment this link to put files into a folder
#OUTOPTS = -o tmp/

# Settings for the 0.5 degree configuration
EXPDIR = /archive/John.Dunne/ulm_201505_awg_v20151106_mom6sis2_2015.12.17/CM4_c96L32_am4g7_2000_OMp5_DR_H3_MEKE/gfdl.ncrc2-intel-prod-openmp
GRIDSPEC = /archive/gold/datasets/OM4_05/mosaic.v20151203.unpacked
WOA = /archive/gold/datasets/OM4_05/obs/WOA05_ptemp_salt_annual.v2015.12.03.nc

# Settings for the 0.25 degree configuration
#EXPDIR = /archive/Alistair.Adcroft/ulm_201505_awg_v20151106_mom6sis2_2016.01.16/CM4_c96L32_am4g7_2000_lowmix_hycom5_BS/gfdl.ncrc3-intel15-prod-openmp
#GRIDSPEC = /archive/gold/datasets/OM4_025/mosaic.v20140610.tar
#WOA =  /archive/gold/datasets/OM4_025/obs/WOA05_ptemp_salt_annual.v20150310.nc

all: sst sss zonalT zonalS zave sections moc mld heattransport

sst:
	./SST_bias_WOA05.py -w $(WOA) -g $(GRIDSPEC) -l 0001-0005 $(EXPDIR)/pp/ocean_annual_z/av/annual_5yr/ocean_annual_z.0001-0005.ann.nc $(OUTOPTS)

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

clean:
	rm -f *.png 
