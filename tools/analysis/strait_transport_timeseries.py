#!/usr/bin/env python
# This script sums the transport for all the straits requested for CMIP6/OMIP that are output in MOM6. If requested, it also
# average the output from daily to monthly
from netCDF4 import Dataset
import numpy as np
from fnmatch import filter as fn_filter
from os import listdir

def sum_transport_in_straits(runpath, monthly_average = False):

  strait = set_strait_info()
  nstraits = len(strait)
  # Calculate transport in each of the straits
  for sidx in range(0,nstraits):
    strait[sidx].transport = 0.
    if strait[sidx].is_zonal and strait[sidx].is_meridional:
      u_file = fn_filter(listdir(runpath), '*' + strait[sidx].mom6_name + '_U.nc')
      v_file = fn_filter(listdir(runpath), '*' + strait[sidx].mom6_name + '_V.nc')
      if (len(u_file)==0 and len(v_file)==0):
        print("Warning: File not found for %s" % strait[sidx].mom6_name)
        continue
      u_vargroup = Dataset(u_file[0]).variables
      v_vargroup = Dataset(v_file[0]).variables
    elif strait[sidx].is_zonal:
      v_file = fn_filter(listdir(runpath), '*' + strait[sidx].mom6_name + '*.nc')
      if (len(v_file)==0):
        print("Warning: File not found for %s" % strait[sidx].mom6_name)
        continue
      v_vargroup = Dataset(v_file[0]).variables
    elif strait[sidx].is_meridional:
      u_file = fn_filter(listdir(runpath), '*' + strait[sidx].mom6_name + '*.nc')
      if (len(u_file)==0):
        print("Warning: File not found for %s" % strait[sidx].mom6_name)
        continue
      u_vargroup = Dataset(u_file[0]).variables

    # Need to find the first interface deeper than or equal to the requested z-limit. If deeper, then we'll need to scale the
    # bottommost part of the column
    if strait[sidx].is_zonal:
      strait[sidx].time = v_vargroup['time'][:]
      if strait[sidx].zlim > 0.:
        z_i = v_vargroup['z_i'][:]
        zidx = np.sum(z_i<strait[sidx].zlim)
        if z_i[zidx] > strait[sidx].zlim:
          frac = min(1., (z_i[zidx] - strait[sidx].zlim)/(z_i[zidx]-z_i[zidx-1]))
          vmo[:,-1,:] = vmo[:,-1,:]*frac
      else:
        vmo = v_vargroup['vmo'][:,:,:,:]
      strait[sidx].transport += vmo.sum(axis=(1,2,3))
      Dataset(v_file[0]).close()

    if strait[sidx].is_meridional:
      strait[sidx].time = u_vargroup['time'][:]
      if strait[sidx].zlim > 0.:
        z_i = u_vargroup['z_i'][:]
        zidx = np.sum(z_i<strait[sidx].zlim)
        if z_i[zidx] > strait[sidx].zlim:
          frac = min(1., (z_i[zidx] - strait[sidx].zlim)/(z_i[zidx]-z_i[zidx-1]))
          umo[:,-1,:] = umo[:,-1,:]*frac
      else:
        umo = u_vargroup['umo'][:,:,:,:]
      strait[sidx].transport += umo.sum(axis=(1,2,3))
      Dataset(u_file[0]).close()
    if monthly_average:
      strait[sidx].transport = make_monthly_averages(strait[sidx].transport)
      strait[sidx].time = make_monthly_averages(strait[sidx].time)
    ntime = strait[sidx].time.size
    time = strait[sidx].time

  transport_array = np.zeros((ntime, nstraits))
  for sidx in range(0,nstraits):
    transport_array[:,sidx] = strait[sidx].transport
  return time, transport_array, strait

def make_monthly_averages(data):
  # This fundamentally assumes that the output is only one year long, any longer and we'd have to know the actual year to properly
  # handle leap years
  idx = daily_indices(data.size == 366)
  idx_r = [range(0,idx[0])] ;
  [idx_r.append(range(idx[t-1],idx[t])) for t in range(1,12)]
  return np.array([np.mean(data[idx_r[t]]) for t in range(0,12)])

def daily_indices(leap = False):
  days_in_months = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30 ,31, 30 ,31])
  if leap: # Change number of days in Feb if leapyear
    days_in_months[1] = 29
  return days_in_months.cumsum()


def set_strait_info():

  strait = []
  # The standard list of straits from CMIP/OMIP request
  strait.append(strait_type("barents_opening",                  "Barents_opening",        is_meridional = True))
  strait.append(strait_type("bering_strait",                    "Bering_Strait"  ,        is_zonal = True))
  strait.append(strait_type("carribean_windward_passage",       "Windward_Passage",       is_zonal = True))
  strait.append(strait_type("davis_strait",                     "Davis_Strait",           is_zonal = True))
  strait.append(strait_type("denmark_strait",                   "Denmark_Strait",         is_zonal = True))
  strait.append(strait_type("drake_passage",                    "Drake_Passage",          is_meridional = True))
  strait.append(strait_type("english_channel",                  "English_Channel",        is_meridional = True))
  strait.append(strait_type("faroe_scotland_channel",           "Faroe_Scotland",         is_meridional = True))
  strait.append(strait_type("florida_bahamas_strait",           "Florida_Bahamas",        is_zonal = True))
  strait.append(strait_type("fram_strait",                      "Fram_Strait",            is_zonal = True))
  strait.append(strait_type("gibraltar_strait",                 "Gibraltar_Strait",       is_meridional = True))
  strait.append(strait_type("iceland_faroe_channel",            "Iceland_Faroe",          is_meridional = True, is_zonal = True))
  strait.append(strait_type("mozambique_channel",               "Mozambique_Channel",     is_zonal = True))
  strait.append(strait_type("pacific_equatorial_undercurrent",  "Pacific_undercurrent",   is_meridional = True, zlim = 350))
  strait.append(strait_type("taiwan_and_luzon_straits",         "Taiwan_Luzon",           is_meridional = True))
  strait.append(strait_type("agulhas_section",                  "Agulhas_section",        is_meridional = True))
  strait.append(strait_type("indonesian_throughflow",           "Indonesian_Throughflow", is_zonal = True))

  return strait

class strait_type:
  def __init__(self, cmor_name, mom6_name, is_meridional = False, is_zonal = False, zlim = -1):
    self.cmor_name = cmor_name
    self.mom6_name = mom6_name
    self.is_meridional = is_meridional
    self.is_zonal = is_zonal
    self.zlim = zlim
    self.time = None
    self.transport = None


