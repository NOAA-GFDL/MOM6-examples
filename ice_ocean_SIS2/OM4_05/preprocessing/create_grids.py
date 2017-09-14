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


refine=2  # Set to 2 for GIS_025 grid and 4 for GIS_0125
lat0=-70 # This is a nominal starting latitude for Mercator grid
lon0=-300. # Starting longitude
lenlat=135 # nominal latitude range of Mercator grid
lenlon=360. 
nx=720*refine
ny=364*refine
ny2=54*refine
#ny_scap=80*refine
ny_ncap=119*refine
lat0_sp=-78.0
#r0_pole=0.20
#lon0_pole=100.0
#doughnut=0.12

#### Begin Mercator Grid

print 'constructing a mercator supergrid with (ny,nx) = ',ny,nx
print 'nominal starting lat and starting longitude =',lat0, lon0
print 'and nominal width in latitude = ',lenlat

mercator=supergrid(nx,ny,'mercator','degrees',lat0,lenlat,lon0,lenlon,cyclic_x=True)

mercator.grid_metrics()

#
# Add equatorial enhancement
#

from midas.rectgrid_gen import *
from midas.rectgrid import *
import numpy as np
from scipy.interpolate import interp1d

phi=mercator.y[:,0]
dphi=phi[1:]-phi[0:-1]

phi=mercator.y[:,0]
dphi=phi[1:]-phi[0:-1]
jind=np.where(phi>-30.)[0][0]
jind=jind+np.mod(jind,2)
phi=phi[0:jind]
dphi=dphi[0:jind]

N=130
phi_s = phi[-1]
dphi_s = dphi[-1]
phi_e = -5.
dphi_e = 0.13
nodes = [0,1,N-2,N-1]
phi_nodes = [phi_s,phi_s+dphi_s,phi_e-dphi_e,phi_e]
f2=interp1d(nodes,phi_nodes,kind=3)
jInd2=np.arange(N)
phi2=f2(jInd2)
dphi2=phi2[1:]-phi2[0:-1]
phi=np.concatenate((phi[0:-1],phi2))
dphi=phi[1:]-phi[0:-1]

N=40
phi_s = phi[-1]
phi2=np.linspace(phi_s,0,N)
dphi2=phi2[1:]-phi2[0:-1]
PHI=np.concatenate((phi[0:-1],phi2))
PHI=np.concatenate((PHI[0:-1],-PHI[::-1]))

DPHI=PHI[1:]-PHI[0:-1]

LAMBDA=np.linspace(lon0,lon0+360.,nx+1)
jind=np.where(PHI>-78.)[0][0]
jind=jind+np.mod(jind,2)
jind2=np.where(PHI>65.)[0][0]
jind2=jind2+np.mod(jind2,2)

PHI2=PHI[jind:jind2-1]
DPHI2=PHI2[1:]-PHI2[0:-1]
x,y = np.meshgrid(LAMBDA,PHI2)
mercator = supergrid(xdat=x,ydat=y,axis_units='degrees',cyclic_x=True)
mercator.grid_metrics()

mercator.write_nc('mercator_supergrid.nc')

print "mercator max/min latitude=", mercator.y.max(),mercator.y.min()
print "mercator nj,ni=", mercator.y.shape[0]-1,mercator.y.shape[1]-1
print "mercator starting longitude=",mercator.x[0,0]
print "mercator ending longitude=",mercator.x[0,-1]

#### Begin Tripolar Cap

lat0_tp=mercator.y.max()
dlat=90.0-lat0_tp

tripolar_n=supergrid(nx,ny_ncap,'spherical','degrees',lat0_tp,dlat,lon0,360.,tripolar_n=True)

tripolar_n.grid_metrics()
tripolar_n.write_nc('ncap_supergrid.nc')

print "generated a tripolar supergrid of size (ny,nx)= ",tripolar_n.y.shape[0]-1,tripolar_n.y.shape[1]-1
print "tripolar grid starting longitude = ",tripolar_n.x[0,0]
print "tripolar grid starting latitude = ",tripolar_n.y[0,0]



#### Begin Spherical Grid for Southern Ocean

print 'constructing a spherical supergrid with (ny,nx) = ',ny,nx
print 'nominal starting lat and starting longitude =',lat0, lon0
print 'and nominal width in latitude = ',lenlat


spherical=supergrid(nx,ny2,'spherical','degrees',lat0_sp,mercator.y.min()-lat0_sp,lon0,lenlon,cyclic_x=True)

spherical.grid_metrics()
spherical.write_nc('antarctic_spherical_supergrid.nc')

print "antarctic spherical max/min latitude=", spherical.y.max(),spherical.y.min()
print "spherical nj,ni=", spherical.y.shape[0]-1,spherical.y.shape[1]-1
print "spherical starting longitude=",spherical.x[0,0]
print "spherical ending longitude=",spherical.x[0,-1]


#### Begin Antarctic Cap

#print spherical.dy.shape
#lenlat=90.0+spherical.y.min()

#dy0=spherical.dy[0,0]*r0_pole

#x=spherical.x[0,:]
#y=np.linspace(-90.,0.5*(lat0_sp-90.0),ny_scap/8)
#y=np.concatenate((y,np.linspace(y.max(),lat0_sp,7*ny_scap/8+1)))
#X,Y=np.meshgrid(x,y)

##antarctic_cap=supergrid(nx,ny_scap,'spherical','degrees',-90.,lenlat,lon0,lenlon,displace_pole=True,r0_pole=r0_pole,lon0_pole=lon0_pole,doughnut=doughnut)
#antarctic_cap=supergrid(xdat=X,ydat=Y,axis_units='degrees',displace_pole=True,r0_pole=r0_pole,lon0_pole=lon0_pole,doughnut=doughnut)                  

#antarctic_cap.grid_metrics()
#antarctic_cap.write_nc('scap_supergrid.nc')


#print "generated a southern cap of size (ny,nx)= ",antarctic_cap.y.shape[0]-1,antarctic_cap.y.shape[1]-1



