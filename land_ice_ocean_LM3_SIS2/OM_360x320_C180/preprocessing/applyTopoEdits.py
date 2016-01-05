#!/usr/bin/env python

import pandas
import netCDF4 as nc
import argparse

"""
Read a list of edits which were provided by and apply them to a topo file.
"""

parser = argparse.ArgumentParser()
parser.add_argument('--orig',type=str,help='path to original netCDF file',default=None)
parser.add_argument('--edits',type=str,help='path to edits file',default=None)
parser.add_argument('--output',type=str,help='path to output netCDF file',default='topog_edits.nc')




args=parser.parse_args()


if args.orig is None:

    print "Need to supply the original topography netCDF file"
    raise

if args.edits is None:

    print "Need to supply the path to edits "
    raise

f=nc.Dataset(args.orig)
depth=f.variables['depth'][:]
Edits=pandas.read_csv(args.edits,header=None,names=['jEdit','iEdit','New'])
jEdits=[]
for a in Edits.jEdit:
    jEdits.append(int(a.replace('(','')))

iEdits=[]
for a in Edits.iEdit:
    iEdits.append(int(a))

New=[]
for a in Edits.New:
    New.append(float(a.replace(')','')))
        
Orig=[]
for i,j,new in zip(iEdits,jEdits,New):
    Orig.append(depth[j,i])
    print i,j,depth[j,i],new

g=nc.Dataset(args.output,'w',format='NETCDF3_CLASSIC')

dims=[]
for d in f.dimensions:
    dimvals=f.variables[d][:]
    dims.append((d,len(f.dimensions[d]),dimvals))


for d in dims:
    g.createDimension(d[0],d[1])
    
g.createDimension('nEdits',None)

dimv=[]
for d in dims:
    dimv.append(g.createVariable(d[0],'f8',(d[0])))
    dimv[-1].units='degrees'

for v,d in zip(dimv,dims):
    v[:]=d[2]
    
for v in f.variables:
    if v.find('longitude')==-1 and v.find('latitude')==-1 and v.find('count')==-1 and v.find('min')==-1 and v.find('max')==-1:
        varout=g.createVariable(v,'f4',('latitude','longitude'))
        try:
            units=f.variables[v].units
            varout.units=units
        except:
            pass
        try:
            standard_name=f.variables[v].standard_name
            varout.standard_name=standard_name
        except:
            pass
        try:
            description=f.variables[v].description
            varout.description=description
        except:
            pass
        try:
            long_name=f.variables[v].long_name
            varout.long_name=long_name
        except:
            pass

        dat=f.variables[v][:]

        if v.find('depth')>-1:
            for i,j,d in zip(iEdits,jEdits,New):
                print 'Modifying Elevation at j,i= ',j,i,' Old= ',dat[j,i],' New= ',-d
                dat[j,i]=-d

        varout[:]=dat

        
ivar=g.createVariable('iEdit','i4',('nEdits'))
jvar=g.createVariable('jEdit','i4',('nEdits'))
kvar=g.createVariable('zEdit','f4',('nEdits'))

n=0
for i,j,d in zip(iEdits,jEdits,Orig):
    ivar[n]=i
    jvar[n]=j
    kvar[n]=d
    n=n+1

g.sync()
g.close()
