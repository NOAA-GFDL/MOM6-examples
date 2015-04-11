#!python

#============================================================
# Generate tiles for the northern/southern caps
# and central mercator grid.
#
# python create_topo.py
# Output: mercator_supergrid.nc, ncap_supergrid.nc, scap_supergrid.nc
# These are supergrids (2x grid tracer refinement) containing positions
# cell lengths, areas and angles
#
# Generate topography for grid tiles using BEDMAP for the Antarctic cap
# GEBCO 2 minute data for the Mercator grid and either
# IBCAO or GEBCO for the Northern cap (these files need to be linked to the
# current directory prior to running this command)

# python create_topo.py --tile ncap|scap|mercator 
#
#============================================================



from midas.rectgrid import *
from midas.rectgrid_gen import *
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, cm
from mpl_toolkits.basemap import interp 
import argparse

sgrid=supergrid(file='ocean_hgrid.nc',cyclic_x=True,tripolar_n=True)
grid=quadmesh(supergrid=sgrid)

ingrid=quadmesh('GEBCO_08_v2.nc',var='depth',simple_grid=True,cyclic=True)
TOPO=state('GEBCO_08_v2.nc',grid=ingrid,fields=['depth'])
TOPO.rename_field('depth','topo')
TOPO.var_dict['topo']['Ztype']='Fixed'

fnam='interpolated_topog.nc'   
R=TOPO.subtile('topo',target=grid)
R.rename_field('mean','depth')
R.write_nc(fnam,['depth','max','min','std','count'])

