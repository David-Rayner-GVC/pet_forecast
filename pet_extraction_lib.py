# -*- coding: utf-8 -*-
"""
Extract forecast data from the downloaded NETCDF files.
Return xarray, write to local files
"""

import config

from xarray import DataArray, Dataset
from datetime import datetime, timedelta
import json
import pandas
import xarray as xr
import os
import glob
import re
import numpy as np


def ExtractTimeSeries(filename, cvar, lat, lon):
  """
  Extract a time-series from a nc4classic regular lat/lon file
  Specify lon as 0-360
  """
  ds = xr.open_dataset(filename)
  # icon uses 0lon at 360!
  xlon = lon
  if lon <336.5:
   xlon = lon + 360 
  xd = ds[cvar].sel(lat=lat, lon=xlon, method='nearest')
  if xd.coords['lon'] > 360:
    xd.coords['lon'] = xd.coords['lon']-360
  xd = xd.squeeze()
  try:
    xd = xd.drop_vars('height')
  except:
    pass
  return(xd)

def ExtractPETForecastData(lat, lon, netcdf_dir=None):
  """
  Extract time-series from standard netcdf files.
  
  netcdf_dir - director to look for netcdf files. Should be pre-processed (de-averaged). default is config.target_root/nc4classic
  lat, lon - coords for time-series, lon is 0-360
  
  Returns some xarray object stuff
  
  The files to use are specified in config.py as PET_vars
  """
  lon = np.float64(lon)
  lat = np.float64(lat)
  
  if netcdf_dir==None:
    netcdf_dir = os.path.join(config.target_root,'nc4classic')
    
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
  
  if config.debug:
    print(xr)
    
  xd = xr.merge(xList)
  xd['air_temperature'].data = xd['air_temperature'].data-273.15
  xd['air_temperature'].attrs['units']='C'   
  xd['time'].values = [x.replace('.000000000','')  for x in xd['time'].values.astype(str)]
  xd['time'].attrs['time_zone']='UTC'
  
  return xd
  
def WritePETForecastJSON(xd, json_file):
  """
  Write a forecast extracted with ExtractPETForecastData to file. 
  
  Inputs:
  xd - xarray from ExtractPETForecastData
  json_file  - output file. 
  """
  saved_dict = xd.to_dict()
  
  for key, value in saved_dict['data_vars'].items():
    saved_dict['data_vars'][key]['data'] = ['null' if np.isnan(x) else round(x,2) for x in value['data'] ]

  j = json.dumps(saved_dict)
   
  with open(json_file,'w') as f:
    f.write('%s\n' % j)
	

  
if __name__ == "__main__":
  # to run as a script
  pass
  
