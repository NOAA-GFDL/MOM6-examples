import netCDF4
import numpy
import m6plot
import m6toolbox
import matplotlib.pyplot as plt
import matplotlib.colors
import matplotlib.patches as mpatches
import os
import sys

gridspec = '/archive/gold/datasets/OM4_025/mosaic.v20140610.unpacked'

x = netCDF4.Dataset(gridspec+'/ocean_hgrid.nc').variables['x'][::2,::2]
xcenter = netCDF4.Dataset(gridspec+'/ocean_hgrid.nc').variables['x'][1::2,1::2]
y = netCDF4.Dataset(gridspec+'/ocean_hgrid.nc').variables['y'][::2,::2]
ycenter = netCDF4.Dataset(gridspec+'/ocean_hgrid.nc').variables['y'][1::2,1::2]
msk = netCDF4.Dataset(gridspec+'/ocean_mask.nc').variables['mask'][:]
area = msk*netCDF4.Dataset(gridspec+'/ocean_hgrid.nc').variables['area'][:,:].reshape([msk.shape[0], 2, msk.shape[1], 2]).sum(axis=-3).sum(axis=-1)
depth = netCDF4.Dataset(gridspec+'/ocean_topog.nc').variables['depth'][:]

code = m6toolbox.genBasinMasks(xcenter, ycenter, depth)


cmap = matplotlib.colors.ListedColormap(['#a1a1a1','#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99',
                                         '#e31a1c','#fdbf6f','#ff7f00','#cab2d6','#6a3d9a'])

colors = ['#a1a1a1','#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99',
          '#e31a1c','#fdbf6f','#ff7f00','#cab2d6','#6a3d9a']

cmap = matplotlib.colors.ListedColormap(colors)

plt.figure()
plt.pcolormesh(code,cmap=cmap)
plt.title('Basin Mask')

ax = plt.gca()
proxy1 = plt.Rectangle((0, 0), 1, 1, fc=colors[1])
proxy2 = plt.Rectangle((0, 0), 1, 1, fc=colors[2])
proxy3 = plt.Rectangle((0, 0), 1, 1, fc=colors[3])
proxy4 = plt.Rectangle((0, 0), 1, 1, fc=colors[4])
proxy5 = plt.Rectangle((0, 0), 1, 1, fc=colors[5])
proxy6 = plt.Rectangle((0, 0), 1, 1, fc=colors[6])
proxy7 = plt.Rectangle((0, 0), 1, 1, fc=colors[7])
proxy8 = plt.Rectangle((0, 0), 1, 1, fc=colors[8])
proxy9 = plt.Rectangle((0, 0), 1, 1, fc=colors[9])
proxy10 = plt.Rectangle((0, 0), 1, 1, fc=colors[10])

labels = ['Southern Ocean (1)','Atlantic Ocean (2)','Pacific Ocean (3)','Arctic Ocean (4)',
          'Indian Ocean (5)','Mediterranean Sea (6)','Black Sea (7)','Hudson Bay (8)',
          'Baltic Sea (9)','Red Sea (10)']
proxies = [proxy1,proxy2,proxy3,proxy4,proxy5,proxy6,proxy7,proxy8,proxy9,proxy10]
ax.legend(proxies,labels,bbox_to_anchor=(0.01, -0.20), loc=2, borderaxespad=0., ncol=2)


