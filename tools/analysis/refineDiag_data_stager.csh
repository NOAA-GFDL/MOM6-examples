#------------------------------------------------------------------------------
#  refineDiag_data_stager_globalAve.csh
#
#  2014/05/07 JPK
#
#  DESCRIPTION:
#    This script serves two primary functions:
#
#    1.  It unpacks the history tar file to the /ptmp file system.  It allows
#        for more efficient post-processing when individual components are 
#        called by frepp.  (i.e. when the frepp "atmos_month" post-processing
#        script runs, frepp will copy only the unpacked "*atmos_month*" .nc 
#        files from /ptmp to the $work directory rather than the entire history
#        tar file.
#
#    2.  It performs a global annual average of all 3D variables (time, lat, lon)
#        and stores the values in a sqlite database that resides in a parallel
#        directory to the frepp scripts and stdout
#
#------------------------------------------------------------------------------

echo ""
echo ""
echo ""
echo "  ---------- begin refineDiag_data_stager.csh ----------  "

cd $work/$hsmdate
pwd

#-- Unload any previous versions of Python and load the system default
module unload python
module unload cdat
module load python

#-- Unpack gridSpec file.  Right now this hardcoded and this is bad practice.  
#   It would be much better to have the refineDiag script know about the gridSpec location
#   through an already populated FRE variable.  Will talk to Amy L. about alternatives.
#set gridSpecFile = "/archive/cjg/mdt/awg/input/grid/c96_GIS_025_grid_v20140327.tar"
#set gsArchRoot = `echo ${gridSpecFile} | rev | cut -f 2-100 -d '/' | rev`
#set gsBaseName = `basename ${gridSpecFile} | cut -f 1 -d '.'`
#hsmget -v -a ${gsArchRoot} -p /ptmp/$USER/${gsArchRoot} -w `pwd` ${gsBaseName}/\*

#-- Create a directory to house the sqlite database (if it does not already exist)
set localRoot = `echo $scriptName | rev | cut -f 4-100 -d '/' | rev`
if (! -d ${localRoot}/db) then 
  mkdir -p ${localRoot}/db
endif
set user = `whoami`
#-- Create the website entry for the experiment (if it does not already exist).
if ( ! -d /home/mdteam/internal_html/cm4/${user}/${name} ) then
  mkdir -p /home/mdteam/internal_html/cm4/${user}/${name}/
  gcp -v /home/mdteam/internal_html/cm4/.webTemplates/* /home/mdteam/internal_html/cm4/${user}/${name}
  ln -s /home/mdteam/internal_html/cm4/${user}/${name}/global.php /home/mdteam/internal_html/cm4/${user}/${name}/index.php
  mv -f /home/mdteam/internal_html/cm4/${user}/${name}/setup.php /home/mdteam/internal_html/cm4/${user}/${name}/setup.php.bak
  cat /home/mdteam/internal_html/cm4/${user}/${name}/setup.php.bak | sed "s|output_dir|${localRoot}|g" >> /home/mdteam/internal_html/cm4/${user}/${name}/setup.php
  sleep 2
  mv -f /home/mdteam/internal_html/cm4/${user}/${name}/setup.php /home/mdteam/internal_html/cm4/${user}/${name}/setup.php.bak
  cat /home/mdteam/internal_html/cm4/${user}/${name}/setup.php.bak | sed "s|experiment_name|${name}|g" >> /home/mdteam/internal_html/cm4/${user}/${name}/setup.php
  sqlite3 /home/Oar.Gfdl.Mdteam/internal_html/cm4/experiments.db "INSERT INTO experiments (user, experiment) VALUES ('${user}','${name}')"
endif

#-- If db exists, copy it for safe keeping and prevent file locks in the 
foreach reg (global nh sh tropics)
  cp -f ${localRoot}/db/${reg}AveAtmos.db ${localRoot}/db/.${reg}AveAtmos.db
  cp -f ${localRoot}/db/${reg}AveOcean.db ${localRoot}/db/.${reg}AveOcean.db
  cp -f ${localRoot}/db/${reg}AveLand.db ${localRoot}/db/.${reg}AveLand.db  
end

#-- Cat a Python script that performs the averages and writes to a copy of the DB
#   in case it is locked by another user
cat > global_atmos_ave.py <<EOF
import sqlite3, cdms2, cdutil, MV2, numpy, cdtime
import sys

# Set current year
fYear = "${oname}"

fgs1 = cdms2.open(fYear + '.grid_spec.tile1.nc')
fgs2 = cdms2.open(fYear + '.grid_spec.tile2.nc')
fgs3 = cdms2.open(fYear + '.grid_spec.tile3.nc')
fgs4 = cdms2.open(fYear + '.grid_spec.tile4.nc')
fgs5 = cdms2.open(fYear + '.grid_spec.tile5.nc')
fgs6 = cdms2.open(fYear + '.grid_spec.tile6.nc')

geoLat   = MV2.concatenate((MV2.array(fgs1('grid_latt')), MV2.array(fgs2('grid_latt')), MV2.array(fgs3('grid_latt')), MV2.array(fgs4('grid_latt')), MV2.array(fgs5('grid_latt')), MV2.array(fgs6('grid_latt'))),axis=0)
geoLon   = MV2.concatenate((MV2.array(fgs1('grid_lont')), MV2.array(fgs2('grid_lont')), MV2.array(fgs3('grid_lont')), MV2.array(fgs4('grid_lont')), MV2.array(fgs5('grid_lont')), MV2.array(fgs6('grid_lont'))),axis=0)
cellArea = MV2.concatenate((MV2.array(fgs1('area')), MV2.array(fgs2('area')), MV2.array(fgs3('area')), MV2.array(fgs4('area')), MV2.array(fgs5('area')), MV2.array(fgs6('area'))),axis=0)

#Read in 6 nc files
fdata1 = cdms2.open(fYear + '.atmos_month.tile1.nc')
fdata2 = cdms2.open(fYear + '.atmos_month.tile2.nc')
fdata3 = cdms2.open(fYear + '.atmos_month.tile3.nc')
fdata4 = cdms2.open(fYear + '.atmos_month.tile4.nc')
fdata5 = cdms2.open(fYear + '.atmos_month.tile5.nc')
fdata6 = cdms2.open(fYear + '.atmos_month.tile6.nc')

def areaMean(varName,cellArea,geoLat,geoLon,region='global'):
  var = MV2.concatenate((MV2.array(fdata1(varName)), MV2.array(fdata2(varName)), MV2.array(fdata3(varName)), MV2.array(fdata4(varName)), MV2.array(fdata5(varName)), MV2.array(fdata6(varName))),axis=1)
  var = cdutil.YEAR(var).squeeze()
  if (region == 'tropics'):
    var = MV2.masked_where(MV2.logical_or(geoLat < -30., geoLat > 30.),var)
    cellArea = MV2.masked_where(MV2.logical_or(geoLat < -30., geoLat > 30.),cellArea)
  elif (region == 'nh'):
    var  = MV2.masked_where(MV2.less_equal(geoLat,30.),var)
    cellArea  = MV2.masked_where(MV2.less_equal(geoLat,30.),cellArea)
  elif (region == 'sh'):
    var  = MV2.masked_where(MV2.greater_equal(geoLat,-30.),var)
    cellArea  = MV2.masked_where(MV2.greater_equal(geoLat,-30.),cellArea)
  elif (region == 'global'):
    var  = var
    cellArea = cellArea
  res = MV2.array(var*cellArea).sum()/cellArea.sum()
  return res

varDict = fdata1.variables
globalMeanDic={}
tropicsMeanDic={}
nhMeanDic={}
shMeanDic={}
for varName in varDict:
  if (len(varDict[varName].shape) == 3):
    
    conn = sqlite3.connect("${localRoot}/db/.globalAveAtmos.db")
    c = conn.cursor()
    globalMeanDic[varName] = areaMean(varName,cellArea,geoLat,geoLon,region='global')
    sql = 'create table if not exists ' + varName + ' (year integer primary key, value float)'
    sqlres = c.execute(sql)
    sql = 'insert or replace into ' + varName + ' values(' + fYear[:4] + ',' + str(globalMeanDic[varName]) + ')'
    try:
      sqlres = c.execute(sql)
      conn.commit()
    except:
      pass
    c.close()
    conn.close()
    
    conn = sqlite3.connect("${localRoot}/db/.tropicsAveAtmos.db")
    c = conn.cursor()
    globalMeanDic[varName] = areaMean(varName,cellArea,geoLat,geoLon,region='tropics')
    sql = 'create table if not exists ' + varName + ' (year integer primary key, value float)'
    sqlres = c.execute(sql)
    sql = 'insert or replace into ' + varName + ' values(' + fYear[:4] + ',' + str(globalMeanDic[varName]) + ')'
    try:
      sqlres = c.execute(sql)
      conn.commit()
    except:
      pass
    c.close()
    conn.close()
    
    conn = sqlite3.connect("${localRoot}/db/.nhAveAtmos.db")
    c = conn.cursor()
    globalMeanDic[varName] = areaMean(varName,cellArea,geoLat,geoLon,region='nh')
    sql = 'create table if not exists ' + varName + ' (year integer primary key, value float)'
    sqlres = c.execute(sql)
    sql = 'insert or replace into ' + varName + ' values(' + fYear[:4] + ',' + str(globalMeanDic[varName]) + ')'
    try:
      sqlres = c.execute(sql)
      conn.commit()
    except:
      pass
    c.close()
    conn.close()
    
    conn = sqlite3.connect("${localRoot}/db/.shAveAtmos.db")
    c = conn.cursor()
    globalMeanDic[varName] = areaMean(varName,cellArea,geoLat,geoLon,region='sh')
    sql = 'create table if not exists ' + varName + ' (year integer primary key, value float)'
    sqlres = c.execute(sql)
    sql = 'insert or replace into ' + varName + ' values(' + fYear[:4] + ',' + str(globalMeanDic[varName]) + ')'
    try:
      sqlres = c.execute(sql)
      conn.commit()
    except:
      pass
    c.close()
    conn.close()

EOF

cat > global_land_ave.py <<EOF
import sqlite3, cdms2, cdutil, MV2, numpy, cdtime
import sys, re
import urllib2
import pickle

# Set current year
fYear = "${oname}"

# Test to see if sqlite database existsm if notm then create it
dbFile = "${localRoot}/db/.globalAveLand.db"

# Read in gridSpec files
fgs1 = cdms2.open(fYear + '.land_static.tile1.nc')
fgs2 = cdms2.open(fYear + '.land_static.tile2.nc')
fgs3 = cdms2.open(fYear + '.land_static.tile3.nc')
fgs4 = cdms2.open(fYear + '.land_static.tile4.nc')
fgs5 = cdms2.open(fYear + '.land_static.tile5.nc')
fgs6 = cdms2.open(fYear + '.land_static.tile6.nc')

geoLat   = MV2.concatenate((MV2.array(fgs1('geolat_t')), MV2.array(fgs2('geolat_t')), MV2.array(fgs3('geolat_t')), MV2.array(fgs4('geolat_t')), MV2.array(fgs5('geolat_t')), MV2.array(fgs6('geolat_t'))),axis=0)
geoLon   = MV2.concatenate((MV2.array(fgs1('geolon_t')), MV2.array(fgs2('geolon_t')), MV2.array(fgs3('geolon_t')), MV2.array(fgs4('geolon_t')), MV2.array(fgs5('geolon_t')), MV2.array(fgs6('geolon_t'))),axis=0)
cellArea = MV2.concatenate((MV2.array(fgs1('land_area')), MV2.array(fgs2('land_area')), MV2.array(fgs3('land_area')), MV2.array(fgs4('land_area')), MV2.array(fgs5('land_area')), MV2.array(fgs6('land_area'))),axis=0)
cellFrac = MV2.concatenate((MV2.array(fgs1('land_frac')), MV2.array(fgs2('land_frac')), MV2.array(fgs3('land_frac')), MV2.array(fgs4('land_frac')), MV2.array(fgs5('land_frac')), MV2.array(fgs6('land_frac'))),axis=0)

fdata1 = cdms2.open(fYear + '.land_month.tile1.nc')
fdata2 = cdms2.open(fYear + '.land_month.tile2.nc')
fdata3 = cdms2.open(fYear + '.land_month.tile3.nc')
fdata4 = cdms2.open(fYear + '.land_month.tile4.nc')
fdata5 = cdms2.open(fYear + '.land_month.tile5.nc')
fdata6 = cdms2.open(fYear + '.land_month.tile6.nc')

depth = fdata1.axes['zhalf_soil'][:]
cellDepth = []
for i in range(1,len(depth)):
  thickness = round((depth[i] - depth[i-1]),2)
  cellDepth.append(thickness)
soilArea = MV2.concatenate((MV2.array(fdata1('soil_area')), MV2.array(fdata2('soil_area')), MV2.array(fdata3('soil_area')), MV2.array(fdata4('soil_area')), MV2.array(fdata5('soil_area')), MV2.array(fdata6('soil_area'))),axis=1)
soilFrac = MV2.array(soilArea/(cellArea*cellFrac))

def getWebsiteVariablesDic():
  varDic = pickle.load(open("${script_dir}/LM3_variable_dictionary.pkl",'rb'))
  #--- Code below can be used to regenerate the dictionary, if needed
  #varDic={}
  #response = urllib2.urlopen("http://cobweb.gfdl.noaa.gov/~slm/lm3-diag-fields.html")
  #html = response.readlines()
  #for line in html:
  #  line = line.rstrip()
  #  if (line.startswith("<tr")) and 'class="head"' not in line:
  #    line = re.sub(r'<.*?>', ',', line)
  #    parts = line.split(',,')
  #    varDic[parts[2]] = parts[1]
  return varDic

def dbEntry(db,varName,varSum,varAvg,fYear):
  conn = sqlite3.connect(db)
  c = conn.cursor()
  sql = 'create table if not exists ' + varName + ' (year integer primary key, sum float, avg float)'
  sqlres = c.execute(sql)
  sql = 'insert or replace into ' + varName + ' values(' + fYear[:4] + ',' + str(varSum) + ',' + str(varAvg) + ')'
  try:
    sqlres = c.execute(sql)
    conn.commit()
  except:
    pass
  c.close()
  conn.close()
  return

def areaMean(varName,cellArea,cellFrac,soilFrac,geoLat,geoLon,region='global'):
  moduleDic = getWebsiteVariablesDic()
  var = MV2.concatenate((MV2.array(fdata1(varName)), MV2.array(fdata2(varName)), MV2.array(fdata3(varName)), MV2.array(fdata4(varName)), MV2.array(fdata5(varName)), MV2.array(fdata6(varName))),axis=1)
  var = cdutil.YEAR(var).squeeze()
  soilFrac = soilFrac[0,:,:]
  try:
    module = moduleDic[varName]
  except:
    try:
      module = moduleDic[varName.lower()]
    except:
      return None
  if (region == 'tropics'):
    var = MV2.masked_where(MV2.logical_or(geoLat < -30., geoLat > 30.),var)
    cellArea = MV2.masked_where(MV2.logical_or(geoLat < -30., geoLat > 30.),cellArea)
    cellFrac = MV2.masked_where(MV2.logical_or(geoLat < -30., geoLat > 30.),cellFrac)
    soilFrac = MV2.masked_where(MV2.logical_or(geoLat < -30., geoLat > 30.),soilFrac)
  elif (region == 'nh'):
    var = MV2.masked_where(MV2.less_equal(geoLat,30.),var)
    cellArea = MV2.masked_where(MV2.less_equal(geoLat,30.),cellArea)
    cellFrac = MV2.masked_where(MV2.less_equal(geoLat,30.),cellFrac)
    soilFrac = MV2.masked_where(MV2.less_equal(geoLat,30.),soilFrac)
  elif ( region == 'sh'):
    var = MV2.masked_where(MV2.greater_equal(geoLat,-30.),var)
    cellArea = MV2.masked_where(MV2.greater_equal(geoLat,-30.),cellArea)
    cellFrac = MV2.masked_where(MV2.greater_equal(geoLat,-30.),cellFrac)
    soilFrac = MV2.masked_where(MV2.greater_equal(geoLat,-30.),soilFrac)
  elif (region == 'global'):
    var = var
    cellArea = cellArea
    cellFrac = cellFrac
    soilFrac = soilFrac
  if module != 'vegn':  
    varSum = MV2.array(var*cellArea*cellFrac).sum()
    varAvg = varSum/(cellArea*cellFrac).sum()
  elif module == 'vegn':
    varSum = MV2.array(var*cellArea*cellFrac*soilFrac).sum()
    varAvg = varSum/(cellArea*cellFrac*soilFrac).sum()
  return varSum, varAvg

def areaMean3D(varName,cellArea,cellFrac,cellDepth,soilFrac,geoLat,geoLon,region='global'):
  var = MV2.concatenate((MV2.array(fdata1(varName)), MV2.array(fdata2(varName)), MV2.array(fdata3(varName)), MV2.array(fdata4(varName)), MV2.array(fdata5(varName)), MV2.array(fdata6(varName))),axis=2)
  soilFrac = cdutil.YEAR(soilFrac).squeeze()
  moduleDic = getWebsiteVariablesDic()
  try:
    module = moduleDic[varName]
  except:
    try:
      module = moduleDic[varName.lower()]
    except:
      return None
  if (var.getAxis(1).id == 'zfull_soil'):
    var = cdutil.YEAR(var).squeeze()
    sums = []
    avgs = []
    for i in range(0,len(cellDepth)):
      if (region == 'tropics'):
        cellArea = MV2.masked_where(MV2.logical_or(geoLat < -30., geoLat > 30.),cellArea)
        cellFrac = MV2.masked_where(MV2.logical_or(geoLat < -30., geoLat > 30.),cellFrac)
        soilFrac = MV2.masked_where(MV2.logical_or(geoLat < -30., geoLat > 30.),soilFrac)
        varSlice = MV2.masked_where(MV2.logical_or(geoLat < -30., geoLat > 30.),var[i,:,:])
      elif (region == 'nh'):
        cellArea = MV2.masked_where(MV2.less_equal(geoLat,30.),cellArea)
        cellFrac = MV2.masked_where(MV2.less_equal(geoLat,30.),cellFrac)
        soiLFrac = MV2.masked_where(MV2.less_equal(geoLat,30.),soilFrac)
        varSlice = MV2.masked_where(MV2.less_equal(geoLat,30.),var[i,:,:])
      elif (region == 'sh'):
        cellArea = MV2.masked_where(MV2.greater_equal(geoLat,-30.),cellArea)
        cellFrac = MV2.masked_where(MV2.greater_equal(geoLat,-30.),cellFrac)
        soilFrac = MV2.masked_where(MV2.greater_equal(geoLat,-30.),soilFrac)
        varSlice = MV2.masked_where(MV2.greater_equal(geoLat,-30.),var[i,:,:])
      elif (region == 'global'):
        cellArea = cellArea
        cellFrac = cellFrac
        soilFrac = soilFrac
        varSlice = var[i,:,:]
      if ('m3' in fdata1(varName).units):
        varSum = MV2.array(varSlice*cellArea*cellFrac*cellDepth[i]).sum()
        varAvg = varSum/(cellArea*cellFrac*cellDepth[i]).sum()
      else:
        varSum = MV2.array(varSlice*cellArea*cellFrac).sum()
        varAvg = varSum/(cellArea*cellFrac).sum()
      sums.append(varSum)
      avgs.append(varAvg)
      return numpy.sum(sums), numpy.average(avgs)

  elif (var.getAxis(1).id == 'band'):
    var = cdutil.YEAR(var).squeeze()
    for i in range(0,1):
      if (region == 'tropics'):
        cellArea = MV2.masked_where(MV2.logical_or(geoLat < -30., geoLat > 30.),cellArea)
        cellFrac = MV2.masked_where(MV2.logical_or(geoLat < -30., geoLat > 30.),cellFrac)
        soilFrac = MV2.masked_where(MV2.logical_or(geoLat < -30., geoLat > 30.),soilFrac)
        var[i,:,:] = MV2.masked_where(MV2.logical_or(geoLat < -30., geoLat > 30.),var[i,:,:])
      elif (region == 'nh'):
        cellArea = MV2.masked_where(MV2.less_equal(geoLat,30.),cellArea)
        cellFrac = MV2.masked_where(MV2.less_equal(geoLat,30.),cellFrac)
        soilFrac = MV2.masked_where(MV2.less_equal(geoLat,30.),soilFrac)
        var[i,:,:] = MV2.masked_where(MV2.less_equal(geoLat,30.),var[i,:,:])
      elif (region == 'sh'):
        cellArea = MV2.masked_where(MV2.greater_equal(geoLat,-30.),cellArea)
        cellFrac = MV2.masked_where(MV2.greater_equal(geoLat,-30.),cellFrac)
        soilFrac = MV2.masked_where(MV2.greater_equal(geoLat,-30.),soilFrac)
        var[i,:,:] = MV2.masked_where(MV2.greater_equal(geoLat,-30.),var[i,:,:])
      elif (region == 'global'):
        cellArea = cellArea
        cellFrac = cellFrac
        soilFrac = soilFrac
        var[i,:,:] = var[i,:,:]
    if (module != 'vegn'):
      topSum = MV2.array(var[0,:,:]*cellArea*cellFrac).sum()
      topAvg = topSum/(cellArea*cellFrac).sum()
      botSum = MV2.array(var[1,:,:]*cellArea*cellFrac).sum()
      botAvg = botSum/(cellArea*cellFrac).sum()
    elif (module == 'vegn'):
      topSum = MV2.array(var[0,:,:]*cellArea*cellFrac*soilFrac).sum()
      topAvg = topSum/(cellArea*cellFrac*soilFrac).sum()
      botSum = MV2.array(var[1,:,:]*cellArea*cellFrac*soilFrac).sum()
      botAvg = botSum/(cellarea*cellFrac*soilFrac).sum()
    return topSum, topAvg, botSum, botAvg

  else:
    return None
  

varDict = fdata1.variables
globalMeanDic={}
tropicsMeanDic={}
nhMeanDic={}
shMeanDic={}
for varName in varDict:
  if (len(varDict[varName].shape) == 3):

    globalMeanDic[varName] = areaMean(varName,cellArea,cellFrac,soilFrac,geoLat,geoLon,region='global')
    if globalMeanDic[varName] != None:
      dbEntry("${localRoot}/db/.globalAveLand.db",varName,globalMeanDic[varName][0], globalMeanDic[varName][1],fYear)

    globalMeanDic[varName] = areaMean(varName,cellArea,cellFrac,soilFrac,geoLat,geoLon,region='tropics')
    if globalMeanDic[varName] != None:
      dbEntry("${localRoot}/db/.tropicsAveLand.db",varName,globalMeanDic[varName][0], globalMeanDic[varName][1],fYear)

    globalMeanDic[varName] = areaMean(varName,cellArea,cellFrac,soilFrac,geoLat,geoLon,region='nh')
    if globalMeanDic[varName] != None:
      dbEntry("${localRoot}/db/.nhAveLand.db",varName,globalMeanDic[varName][0], globalMeanDic[varName][1],fYear)

    globalMeanDic[varName] = areaMean(varName,cellArea,cellFrac,soilFrac,geoLat,geoLon,region='sh')
    if globalMeanDic[varName] != None:
      dbEntry("${localRoot}/db/.shAveLand.db",varName,globalMeanDic[varName][0], globalMeanDic[varName][1],fYear)

  if (len(varDict[varName].shape) == 4):
    globalMeanDic[varName] = areaMean3D(varName,cellArea,cellFrac,cellDepth,soilFrac,geoLat,geoLon,region='global')
    if globalMeanDic[varName] != None:
      if len(globalMeanDic[varName]) == 2:
        dbEntry("${localRoot}/db/.globalAveLand.db",varName, globalMeanDic[varName][0], globalMeanDic[varName][1], fYear)
      elif len(globalMeanDic[varName]) == 4:
        dbEntry("${localRoot}/db/.globalAveLand.db","%s0" % varName, globalMeanDic[varName][0], globalMeanDic[varName][1], fYear)
        dbEntry("${localRoot}/db/.globalAveLand.db","%s1" % varName, globalMeanDic[varName][2], globalMeanDic[varName][3], fYear)

    globalMeanDic[varName] = areaMean3D(varName,cellArea,cellFrac,cellDepth,soilFrac,geoLat,geoLon,region='tropics')
    if globalMeanDic[varName] != None:
      if len(globalMeanDic[varName]) == 2:
        dbEntry("${localRoot}/db/.tropicsAveLand.db",varName, globalMeanDic[varName][0], globalMeanDic[varName][1], fYear)
      elif len(globalMeanDic[varName]) == 4:
        dbEntry("${localRoot}/db/.tropicsAveLand.db", "%s0" % varName, globalMeanDic[varName][0], globalMeanDic[varName][1], fYear)
        dbEntry("${localRoot}/db/.tropicsAveLand.db", "%s1" % varName, globalMeanDic[varName][2], globalMeanDic[varName][3], fYear)

    globalMeanDic[varName] = areaMean3D(varName,cellArea,cellFrac,cellDepth,soilFrac,geoLat,geoLon,region='nh')
    if globalMeanDic[varName] != None:
      if len(globalMeanDic[varName]) == 2:
        dbEntry("${localRoot}/db/.nhAveLand.db",varName, globalMeanDic[varName][0], globalMeanDic[varName][1], fYear)
      elif len(globalMeanDic[varName]) == 4:
        dbEntry("${localRoot}/db/.nhAveLand.db", "%s0" % varName, globalMeanDic[varName][0], globalMeanDic[varName][1], fYear)
        dbEntry("${localRoot}/db/.nhAveLand.db", "%s1" % varName, globalMeanDic[varName][2], globalMeanDic[varName][3], fYear)

    globalMeanDic[varName] = areaMean3D(varName,cellArea,cellFrac,cellDepth,soilFrac,geoLat,geoLon,region='sh')
    if globalMeanDic[varName] != None:
      if len(globalMeanDic[varName]) == 2:
        dbEntry("${localRoot}/db/.shAveLand.db",varName,globalMeanDic[varName][0], globalMeanDic[varName][1],fYear)
      elif len(globalMeanDic[varName]) == 4:
        dbEntry("${localRoot}/db/.shAveLand.db", "%s0" % varName, globalMeanDic[varName][0], globalMeanDic[varName][1], fYear)
        dbEntry("${localRoot}/db/.shAveLand.db", "%s1" % varName, globalMeanDic[varName][2], globalMeanDic[varName][3], fYear)

EOF

cat > global_ocean_ave.py <<EOF
import sqlite3, cdms2, cdutil, MV2, numpy, cdtime
import sys

# Set current year
fYear = "${oname}"

# Test to see if sqlite databse exits, if not, then create it
dbFile = "${localRoot}/db/.globalAveOcean.db"

#Read in gridSpec files
fgs = cdms2.open(fYear + '.ocean_static.nc')

cellArea = fgs('area_t') 
geoLat   = fgs('geolat') 
geoLon   = fgs('geolon') 

#Read in data nc files
fdata = cdms2.open(fYear + '.ocean_month.nc')

def areaMean(varName,cellArea,geoLat,geoLon,region='global'):
  var = fdata(varName)
  var = cdutil.YEAR(var).squeeze()
  if (region == 'tropics'):
    var = MV2.masked_where(MV2.logical_or(geoLat < -30., geoLat > 30.),var)
    cellArea = MV2.masked_where(MV2.logical_or(geoLat < -30., geoLat > 30.),cellArea)
  elif (region == 'nh'):
    var  = MV2.masked_where(MV2.less_equal(geoLat,30.),var)
    cellArea  = MV2.masked_where(MV2.less_equal(geoLat,30.),cellArea)
  elif (region == 'sh'):
    var  = MV2.masked_where(MV2.greater_equal(geoLat,-30.),var)
    cellArea  = MV2.masked_where(MV2.greater_equal(geoLat,-30.),cellArea)
  elif (region == 'global'):
    var  = var
    cellArea = cellArea
  res = MV2.array(var*cellArea).sum()/cellArea.sum()
  return res

varDict = fdata.variables
globalMeanDic={}
tropicsMeanDic={}
nhMeanDic={}
shMeanDic={}
for varName in varDict:
  if (len(varDict[varName].shape) == 3):
    if (fdata(varName).getAxis(1).id == 'yh' and fdata(varName).getAxis(2).id == 'xh'):
      
      conn = sqlite3.connect("${localRoot}/db/.globalAveOcean.db")
      c = conn.cursor()
      globalMeanDic[varName] = areaMean(varName,cellArea,geoLat,geoLon,region='global')
      sql = 'create table if not exists ' + varName + ' (year integer primary key, value float)'
      sqlres = c.execute(sql)
      sql = 'insert or replace into ' + varName + ' values(' + fYear[:4] + ',' + str(globalMeanDic[varName]) + ')'
      try:
        sqlres = c.execute(sql)
        conn.commit()
      except:
  	pass
      c.close()
      conn.close()
      
      conn = sqlite3.connect("${localRoot}/db/.tropicsAveOcean.db")
      c = conn.cursor()
      globalMeanDic[varName] = areaMean(varName,cellArea,geoLat,geoLon,region='tropics')
      sql = 'create table if not exists ' + varName + ' (year integer primary key, value float)'
      sqlres = c.execute(sql)
      sql = 'insert or replace into ' + varName + ' values(' + fYear[:4] + ',' + str(globalMeanDic[varName]) + ')'
      try:
        sqlres = c.execute(sql)
        conn.commit()
      except:
  	 pass
      c.close()
      conn.close()
      
      conn = sqlite3.connect("${localRoot}/db/.nhAveOcean.db")
      c = conn.cursor()
      globalMeanDic[varName] = areaMean(varName,cellArea,geoLat,geoLon,region='nh')
      sql = 'create table if not exists ' + varName + ' (year integer primary key, value float)'
      sqlres = c.execute(sql)
      sql = 'insert or replace into ' + varName + ' values(' + fYear[:4] + ',' + str(globalMeanDic[varName]) + ')'
      try:
        sqlres = c.execute(sql)
        conn.commit()
      except:
	pass
      c.close()
      conn.close()
      
      conn = sqlite3.connect("${localRoot}/db/.shAveOcean.db")
      c = conn.cursor()
      globalMeanDic[varName] = areaMean(varName,cellArea,geoLat,geoLon,region='sh')
      sql = 'create table if not exists ' + varName + ' (year integer primary key, value float)'
      sqlres = c.execute(sql)
      sql = 'insert or replace into ' + varName + ' values(' + fYear[:4] + ',' + str(globalMeanDic[varName]) + ')'
      try:
        sqlres = c.execute(sql)
        conn.commit()
      except:
	pass
      c.close()
      conn.close()

EOF

#-- Run the averager script
python global_atmos_ave.py
python global_ocean_ave.py
python global_land_ave.py

#-- Copy the database back to its original location
foreach reg (global nh sh tropics)
  cp -f ${localRoot}/db/.${reg}AveAtmos.db ${localRoot}/db/${reg}AveAtmos.db
  cp -f ${localRoot}/db/.${reg}AveOcean.db ${localRoot}/db/${reg}AveOcean.db
  cp -f ${localRoot}/db/.${reg}AveLand.db ${localRoot}/db/${reg}AveLand.db  
end

echo "  ---------- end refineDiag_data_stager.csh ----------  "
echo ""
echo ""
echo ""

exit
