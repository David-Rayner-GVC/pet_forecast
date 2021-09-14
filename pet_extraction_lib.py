# -*- coding: utf-8 -*-
"""
Extract forecast data from the downloaded NETCDF files.
Return xarray, write to local files
"""

import config
import pet_stash_lib as ps
from Stations import Stations

from xarray import DataArray, Dataset
from datetime import datetime, timedelta
import json
import pandas as pd
import xarray as xr
import os
import glob
import re
import numpy as np
from pathlib import Path

# and this is a local one
#try:
#  sys.path.append(config.PETCalculatorWEB_path)
#except:
#  pass
from petprocessingprognose import petcalcprognose


def CalculatePET(xd):
  """
  CalculatePET - add PET and UTCI variables to a dataset!
  This is called internally in ExtractPETForecastData but
  it can be called stand-alone with an xd with suitable variables
  
  Input/output
  xd - xarray dataset 
  """
  timestamp = xd.time.data  
  lat = float(xd.lat.data) 
  lon = float(xd.lon.data) 
  UTC=0 # all times are UTC

  year = pd.to_datetime(timestamp).year  
  month = pd.to_datetime(timestamp).month  
  day =  pd.to_datetime(timestamp).day  
  hour =  pd.to_datetime(timestamp).hour  
  minu = pd.to_datetime(timestamp).minute 
   
  Ta = xd.air_temperature.data
  RH = xd.relative_humidity.data
  radD = xd.downward_diffuse.data
  radI = xd.downward_direct.data
  Ws = np.sqrt((xd.eastward_wind.data)**2 + (xd.northward_wind.data)**2)

  with np.errstate(invalid='ignore'):
    radI[radI < 0.] = 0.
    radD[radD < 0.] = 0.
  radG = radD + radI

  poi_save = petcalcprognose(Ta, RH, Ws, radG, radD, radI, year, month, day, hour, minu, lat, lon, UTC)

  xd['PET'] = (('time'), np.float32(poi_save[:, 32]) )
  xd.PET.data[0]=np.nan
  xd.PET.attrs = {"standard_name":"PET", "long_name":"physiological equivalent temperature", "units":"C"} 

  xd['UTCI'] = (('time'), np.float32(poi_save[:, 33]) )
  xd.UTCI.data[0]=np.nan
  xd.UTCI.attrs = {"standard_name":"UTCI", "long_name":"Universal Thermal Climate Index", "units":"C"} 
  
  xd['Tmrt'] = (('time'), np.float32(poi_save[:, 26]) )
  xd.Tmrt.data[0]=np.nan
  xd.Tmrt.attrs = {"standard_name":"Tmrt", "long_name":"Mean Radiant Temperature", "units":"C"}

  xd['IO'] = (('time'), np.float32(poi_save[:, 27]) )
  xd.IO.data[0]=np.nan
  xd.IO.attrs = {"standard_name":"IO", "long_name":"Clear-sky solar radiation", "units":"W/m/m"} 

  xd['altitude'] = (('time'), np.float32(poi_save[:, 5]) )
  xd.altitude.data[0]=np.nan
  xd.altitude.attrs = {"standard_name":"altitude", "long_name":"Solar altitude", "units":"deg"} 
  
  xd['azimuth'] = (('time'), np.float32(poi_save[:, 6]) )
  xd.azimuth.data[0]=np.nan
  xd.azimuth.attrs = {"standard_name":"azimuth", "long_name":"Solar azimuth", "units":"deg"}

  xd['wind_speed'] = (('time'), np.float32(Ws) )
  xd.wind_speed.data[0]=np.nan
  xd.wind_speed.attrs = {"standard_name":"wind_speed", "long_name":"Wind speed", "units":"m/s" } 

  return xd

def ExtractTimeSeries(filename, cvar, lat, lon):
  """
  Extract a time-series from a nc4classic regular lat/lon file
  Specify lon as 0-360
  """
  ds = xr.open_dataset(filename)
  # icon uses 0lon at 360? sometimes? 
  # whatever, sometimes the netcdf files are centered on 0.
  xlon = lon
  if float(ds.lon[0])>0 and float(lon)<float(ds.lon[0]):
    xlon = lon + 360 
  xd = ds[cvar].sel(lat=lat, lon=xlon, method='nearest')
  if xd.coords['lon'] > 360:
    xd.coords['lon'] = xd.coords['lon']-360
  xd = xd.squeeze()
  try:
    xd = xd.drop_vars('height')
  except:
    pass
  return xd

def ExtractPETForecastData(lat, lon, netcdf_dir=None, withPET=True):
  """
  Extract time-series from standard netcdf files.
  
  netcdf_dir - director to look for netcdf files. Should be pre-processed (de-averaged). default is config.target_root/'netcdf_final'
  lat, lon - coords for time-series, lon is 0-360
  
  withPET=True => calculate Tmrt, PET, UTCI etc for the extracted time-series.
  
  Returns some xarray object stuff.
  
  The files to use are specified in config.py as PET_vars
  """
  if config.debug:
    print('ExtractPETForecastData lat=%f, lon=%f'%(lat, lon))
    
  if netcdf_dir==None:
    netcdf_dir = os.path.join(config.target_root,'netcdf_final')
    
  xList=list()
  fileList = glob.glob(os.path.join(netcdf_dir,'*'), recursive=False)
  for filePath in fileList:
    path_, name_ = os.path.split(filePath)
    root_, ext  = os.path.splitext(name_)
    result = re.split('_',root_)
    fileLabel = '_'.join(result[5:])
    if fileLabel in config.PET_vars:
      cvar = config.variable_names[fileLabel]
      xa = ExtractTimeSeries(filePath, cvar, lat, lon)
      xa.name=config.standard_names[fileLabel] 
      xList.append(xa)
    
  xd = xr.merge(xList)
  xd['air_temperature'].data = xd['air_temperature'].data-273.15
  xd['air_temperature'].attrs['units']='C'  
  xd['time'].attrs['time_zone']='UTC'
  
  # now add PET and UTCI
  if withPET:
    CalculatePET(xd)
  
  return xd
  
def WritePETForecastJSON(xd, json_file):
  """
  Write a forecast extracted with ExtractPETForecastData to file. 
  
  Inputs:
  xd - xarray from ExtractPETForecastData
  json_file  - output file. 
  """
  # convert time to str, as datetime is not serlializable as json
  #xd.assign_coords(time=[x.replace('.000000000','')  for x in xd['time'].values.astype(str)])  
  #xd['time'].values = [x.replace('.000000000','')  for x in xd['time'].values.astype(str)]

  saved_dict = xd.to_dict()
  
  saved_dict['coords']['time']['data'] = [x.replace('.000000000','')  for x in xd['time'].values.astype(str)]

  for key, value in saved_dict['data_vars'].items():
    saved_dict['data_vars'][key]['data'] = ['null' if np.isnan(x) else round(x,2) for x in value['data'] ]

  j = json.dumps(saved_dict)
   
  with open(json_file,'w') as f:
    f.write('%s\n' % j)
	
def WritePETForecastCSV(xd, csv_file):
  """
  Write a forecast extracted with ExtractPETForecastData to csv file. 
  
  Inputs:
  xd - xarray from ExtractPETForecastData
  csv_file  - output file. 
  """

  xd.to_dataframe.to_csv(csv_file)

def UpdateLocalForecast(ID=None, name=None, stash=False, withPET=True):
  """
  Extract data, write to JSON
  File locations are controlled in config.py 
  ID is currently string name of forecast
  
  """
  
  df = Stations().GetRow(ID=ID,name=name)
  
  for index, d in df.iterrows():
    xd=ExtractPETForecastData(lat=d['Latitude'], lon=d['Longitude'],withPET=withPET)
    xd=xd.assign_coords(Name=d['Name']) 
    xd=xd.assign_coords(Id=d['Id']) 

    json_file=os.path.join(config.git_local_root, 'json', d['Name'] + '.json')
    if config.debug:
      print('updating '+json_file)
    WritePETForecastJSON(xd, json_file)
    if stash:
      # stash here
      ps.StashSingleForecast(xd)


def RetrieveLocalForecast(Name=None, ID=None, asXarray=True, asDatetime64=True):
  """ read a forecast json file from local repo  
  
  ID - the numeric ID of the station that you want, OR
  Name - the Name of the station that you want
  
  asXarray - return xarray, rather than a dictionary
  asDatetime64 - convert dates from string to asDatetime64
 
  """
  if ID!=None and Name==None:
    df = Stations().GetRow(ID=ID)
    Name = df.Name.values[0]
  fname =  Name + '.json'

  url = Path(config.git_local_root) / 'json' / fname 
  
  with open(url) as f:
    data = json.load(f)

  for key, value in data['data_vars'].items():
   data['data_vars'][key]['data'] = [np.nan if isinstance(x,str) else x for x in value['data'] ]

  # re-create xarray Dataset
  if asXarray:
    data = Dataset.from_dict(data)

  # Convert time from string to datetime64 if you want. 
  if asDatetime64:
    if not(asXarray):
      raise ValueError('asXarray must be set for asDatetime64 converstion')
    import pandas
    data['time'].values = pandas.to_datetime(data['time'].values)

  return(data)

  
if __name__ == "__main__":
  # to run as a script
  pass
  
