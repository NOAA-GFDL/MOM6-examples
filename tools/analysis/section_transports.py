#!/usr/bin/env python

import netCDF4
import numpy
import m6plot
import m6toolbox
import matplotlib.pyplot as plt
import os

try: import argparse
except: raise Exception('This version of python is not new enough. python 2.7 or newer is required.')

def run():
  parser = argparse.ArgumentParser(description='''Script for plotting depth vs. time plots of temperature and salinity drift''')
  parser.add_argument('ts_directory', type=str, help='''Top-level post-processing directory for an experiment (i.e <some_path>/pp/)''')
  parser.add_argument('-l','--label', type=str, default='', help='''Label to add to the plot.''')
  parser.add_argument('-s','--suptitle', type=str, default='', help='''Super-title for experiment.  Default is to read from netCDF file.''')
  parser.add_argument('-o','--outdir', type=str, default='.', help='''Directory in which to place plots.''')
  parser.add_argument('-t','--trange', type=str, default=None, help='''Tuple containing start and end years to plot''')
  cmdLineArgs = parser.parse_args()
  main(cmdLineArgs)

def main(cmdLineArgs,stream=None):

  if cmdLineArgs.ts_directory[-1] != '/': cmdLineArgs.ts_directory = cmdLineArgs.ts_directory+'/'

  class Transport():
    def __init__(self, cmdLineArgs, section, var, label=None, ylim=None, mks2Sv=True):
      if not isinstance(section,list):
        section = [section]
      if not isinstance(var,list):
        var = [var]
      self.section = section[0]
      self.var = var
      if label != None: self.label = label
      else: self.label = section[0]
      self.ylim = ylim
      for k in range(0,len(section)):
        try: rootGroup = netCDF4.MFDataset( cmdLineArgs.ts_directory + section[k] + '/ts/120hr/20yr/*.'+var[k]+'.nc')
        except: rootGroup = netCDF4.MFDataset( cmdLineArgs.ts_directory + section[k] + '/ts/120hr/5yr/*.'+var[k]+'.nc')
        if k == 0: total = numpy.ones(rootGroup.variables[var[k]][:].shape[0])*0.0
        trans = rootGroup.variables[var[k]][:].sum(axis=1)  # Depth summation
        if   var[k] == 'umo': total = total + trans.sum(axis=1).squeeze()
        elif var[k] == 'vmo': total = total + trans.sum(axis=2).squeeze()
        else: raise ValueError('Unknown variable name')
      if mks2Sv == True: total = total * 1.e-9
      self.data = total
      self.time = rootGroup.variables['time'][:]*(1/365.0)
      if cmdLineArgs.suptitle != '':  self.suptitle = cmdLineArgs.suptitle + ' ' + cmdLineArgs.label
      else: self.suptitle = rootGroup.title + ' ' + cmdLineArgs.label

  def plotPanel(section,n,observedFlows=None,autolim=True,colorCode=True):
    ax = plt.subplot(6,3,n)
    color = '#c3c3c3'; obsLabel = None
    if section.label in observedFlows.keys():
      if isinstance(observedFlows[section.label],tuple):
        if colorCode == True:
          if min(observedFlows[section.label]) <= section.data.mean() <= max(observedFlows[section.label]):
            color = '#90ee90'
          else: color = '#f26161'
        obsLabel = str(min(observedFlows[section.label])) + ' to ' + str(max(observedFlows[section.label]))
      else: obsLabel = str(observedFlows[section.label])
    plt.plot(section.time,section.data,color=color)
    plt.title(section.label,fontsize=12)
    plt.text(0.04,0.11,'Mean = '+'{0:.2f}'.format(section.data.mean()),transform=ax.transAxes,fontsize=10)
    if obsLabel != None: plt.text(0.04,0.04,'Obs. = '+obsLabel,transform=ax.transAxes,fontsize=10)
    if autolim == False:
      if section.ylim != None: plt.ylim(section.ylim)
    if n in [1,4,7,10,13,16]: plt.ylabel('Transport (Sv)')

  reference = 'Griffies et al., 2016: Experimental and diagnostic protocol for the physical component of the\nCMIP6 Ocean Model Intercomparison Project (OMIP)  Geosci. Model Dev., Submitted'
  observedFlows = {'reference':reference,'Bering Strait':(0.7,1.1),
                   'Barents Opening':2.0, 'Canadian Archipelago':(0.5,1.0), 'Denmark Strait':(-4.8,-2.0), 
                   'Drake Passage':(129.8,143.6), 'English Channel':(0.1,0.2), 'Faroe-Scotland':(0.8,1.0), 'Florida-Bahamas':(28.9,34.3), 
                   'Fram Strait':(6.2,7.0), 'Gibraltar Strait':0.11, 'Iceland-Faroe':(4.35,4.85), 
                   'Indonesian Throughflow':-13., 'Mozambique Channel':(-25.6,-7.8), 'Pacific Equatorial Undercurrent':(24.,36.), 
                   'Taiwan-Luzon Strait':(-3.0,-1.8), 'Windward Passage':(-15.,5.)}
 
  plotSections = []

  try: res = Transport(cmdLineArgs,'ocean_Agulhas_section','umo',label='Agulhas',ylim=(120,180)); plotSections.append(res)
  except: print('WARNING: unable to process ocean_Agulhas_section')

  try: res = Transport(cmdLineArgs,'ocean_Bering_Strait','vmo',label='Bering Strait',ylim=(-2,8)); plotSections.append(res)
  except: print('WARNING: unable to process ocean_Barents_opening')
  
  try: res = Transport(cmdLineArgs,'ocean_Barents_opening','umo',label='Barents Opening',ylim=(-2,8)); plotSections.append(res)
  except: print('WARNING: unable to process ocean_Barents_opening')

  try: res = Transport(cmdLineArgs,'ocean_Canadian_Archipelago','vmo',label='Canadian Archipelago',ylim=(-4.5,0.)); plotSections.append(res)
  except: print('WARNING: unable to process ocean_Canadian_Archipelago')

  try: res = Transport(cmdLineArgs,'ocean_Denmark_Strait','vmo',label='Denmark Strait',ylim=(-20,5)); plotSections.append(res)
  except: print('WARNING: unable to process ocean_Denmark_Strait')

  try: res = Transport(cmdLineArgs,'ocean_Drake_Passage','umo',label='Drake Passage',ylim=(20,180)); plotSections.append(res)
  except: print('WARNING: unable to process ocean_Drake_Passage')

  try: res = Transport(cmdLineArgs,'ocean_English_Channel','umo',label='English Channel',ylim=(-0.2,0.3)); plotSections.append(res)
  except: print('WARNING: unable to process ocean_English_Channel')

  try: res = Transport(cmdLineArgs,'ocean_Faroe_Scotland','umo',label='Faroe-Scotland',ylim=(-10,15)); plotSections.append(res)
  except: print('WARNING: unable to process ocean_Faroe_Scotland')

  try: res = Transport(cmdLineArgs,'ocean_Florida_Bahamas','vmo',label='Florida-Bahamas',ylim=(5,25)); plotSections.append(res)
  except: print('WARNING: unable to process ocean_Florida_Bahamas')

  try: res = Transport(cmdLineArgs,'ocean_Fram_Strait','vmo',label='Fram Strait',ylim=(-8,4)); plotSections.append(res)
  except: print('WARNING: unable to process ocean_Fram_Strait')

  try: res = Transport(cmdLineArgs,'ocean_Gibraltar_Strait','umo',label='Gibraltar Strait',ylim=(-2.5,0.5)); plotSections.append(res)
  except: print('WARNING: unable to process ocean_Gibraltar_Strait')

  try: res = Transport(cmdLineArgs,['ocean_Iceland_Faroe_U','ocean_Iceland_Faroe_V'],['umo','vmo'],label='Iceland-Faroe'); plotSections.append(res)
  except: print('WARNING: unable to process ocean_Iceland_Faroe_U and ocean_Iceland_Faroe_V')

  try: res = Transport(cmdLineArgs,'ocean_Iceland_Norway','vmo',label='Iceland-Norway',ylim=(-5,20)); plotSections.append(res)
  except: print('WARNING: unable to process ocean_Iceland_Norway')

  try: res = Transport(cmdLineArgs,'ocean_Indonesian_Throughflow','vmo',label='Indonesian Throughflow',ylim=(-40,40)); plotSections.append(res)
  except: print('WARNING: unable to process ocean_Indonesian_Throughflow')

  try: res = Transport(cmdLineArgs,'ocean_Mozambique_Channel','vmo',label='Mozambique Channel',ylim=(-40,50)); plotSections.append(res)
  except: print('WARNING: unable to process ocean_Mozambique_Channel')

  try: res = Transport(cmdLineArgs,'ocean_Pacific_undercurrent','umo',label='Pacific Equatorial Undercurrent',ylim=(-8,8)); plotSections.append(res)
  except: print('WARNING: unable to process ocean_Pacific_undercurrent')

  try: res = Transport(cmdLineArgs,'ocean_Taiwan_Luzon','umo',label='Taiwan-Luzon Strait',ylim=(-15,10)); plotSections.append(res)
  except: print('WARNING: unable to process ocean_Taiwan_Luzon')

  try: res = Transport(cmdLineArgs,'ocean_Windward_Passage','vmo',label='Windward Passage',ylim=(-15,15)); plotSections.append(res)
  except: print('WARNING: unable to process ocean_Windward_Passage')

  fig = plt.figure(figsize=(13,17))
  for n in range(0,len(plotSections)): plotPanel(plotSections[n],n,observedFlows=observedFlows)
  fig.text(0.5,0.955,str(plotSections[n-1].suptitle),horizontalalignment='center',fontsize=14)
  fig.text(0.5,0.925,'Observations summarized in '+observedFlows['reference'],horizontalalignment='center',fontsize=11)
  plt.subplots_adjust(hspace=0.3)
  if stream != None: fig.text(0.5,0.05,str('Generated by dora.gfdl.noaa.gov'),horizontalalignment='center',fontsize=12)
  plt.show(block=False)

  if stream != None: objOut = stream[0]
  else: objOut = cmdLineArgs.outdir+'/section_flows.png'
  plt.savefig(objOut)

if __name__ == '__main__':
  run()

