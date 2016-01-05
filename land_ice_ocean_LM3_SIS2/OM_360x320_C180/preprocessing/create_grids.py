#!/usr/bin/env python

#============================================================
# Generate tiles for the northern/southern caps
# and central mercator grid. For use in Antarctic ice-sheet
# modeling.
#
# 
# python create_topo.py
# Output: mercator_supergrid.nc, ncap_supergrid.nc, scap_supergrid.nc
# These are supergrids (2x grid tracer refinement) containing positions
# cell lengths, areas and angles.  
#
#============================================================



from midas.rectgrid_gen import *
from midas.rectgrid import *
import numpy as np
from scipy.interpolate import interp1d
lat0=-65.
lon0=-300.
lenlat=125.
lenlon=360.
nlon=360*2
nlat=500*2

mercator=supergrid(nlon,nlat,'mercator','degrees',lat0,lenlat,lon0,lenlon,cyclic_x=True)
mercator.grid_metrics()

phi=mercator.y[:,0]
dphi=phi[1:]-phi[0:-1]

phi=mercator.y[:,0]
dphi=phi[1:]-phi[0:-1]
jind=np.where(phi>-20.)[0][0]
jind=jind+np.mod(jind,2)
phi=phi[0:jind]
dphi=dphi[0:jind]

N=26
phi_s = phi[-1]
dphi_s = dphi[-1]
phi_e = -10.
dphi_e = 0.2
nodes = [0,1,N-2,N-1]
phi_nodes = [phi_s,phi_s+dphi_s,phi_e-dphi_e,phi_e]
f2=interp1d(nodes,phi_nodes,kind=3)
jInd2=np.arange(N)
phi2=f2(jInd2)
dphi2=phi2[1:]-phi2[0:-1]
phi=np.concatenate((phi[0:-1],phi2))
dphi=phi[1:]-phi[0:-1]

N=56
phi_s = phi[-1]
phi2=np.linspace(phi_s,0,N)
dphi2=phi2[1:]-phi2[0:-1]
PHI=np.concatenate((phi[0:-1],phi2))
PHI=np.concatenate((PHI[0:-1],-PHI[::-1]))

DPHI=PHI[1:]-PHI[0:-1]

LAMBDA=np.linspace(lon0,lon0+360.,nlon+1)
jind=np.where(PHI>-78.)[0][0]
jind=jind+np.mod(jind,2)
jind2=np.where(PHI>60.)[0][0]
jind2=jind2+np.mod(jind2,2)

PHI2=PHI[jind:jind2-1]
DPHI2=PHI2[1:]-PHI2[0:-1]
x,y = np.meshgrid(LAMBDA,PHI2)
gridA = supergrid(xdat=x,ydat=y,axis_units='degrees',cyclic_x=True)
gridA.grid_metrics()
gridA.write_nc('sgridA.nc')


ny_ncap=155
phi_tps = PHI2[-1]
dphi_tps = DPHI2[-1]
nodes = [0,1,ny_ncap-2,ny_ncap-1]
phi_tp_nodes = [phi_tps,phi_tps+dphi_tps,89.9,90.]
ftp=interp1d(nodes,phi_tp_nodes,kind=3)
jInd2=np.arange(ny_ncap)
phitp=ftp(jInd2)
dphitp=phitp[1:]-phitp[0:-1]

lat0_tp = PHI2[-1]
XTP,YTP=np.meshgrid(LAMBDA,phitp)
gridB=supergrid(xdat=XTP,ydat=YTP,axis_units='degrees',tripolar_n=True)
gridB.grid_metrics()
gridB.write_nc('sgridB.nc')





