# -*- coding: utf-8 -*-
"""
Update/Retrieve forecast data from GIT.

You don't need a local clone of the pet_data repository just to retrieve data!

"""

import config
import os
import json
import numpy as np

import base64
import requests
import datetime

from Stations import Stations

def RetrieveForecast(Name=None, ID=None, asXarray=True, asDatetime64=True):
  """
  Retrieve a forecast from GitHub, does not require any local respository
  (but need config.git_url_root specified)
  
  ID - the numeric ID of the station that you want, OR
  Name - the Name of the station that you want
  
  asXarray - return xarray, rather than a dictionary
  asDatetime64 - convert dates from string to asDatetime64
 
  """
  assert ID!=None or Name!=None, "You must specify ID or Name"

  if ID!=None:
    # get name from station list
    df = Stations(config.git_url_root + 'locations_config.csv').GetRow(ID=ID)
    Name = df.iloc[0]['Name']

  url = config.git_url_root + 'json/' + Name + '.json'
  
  data = requests.get(url).json()

  for key, value in data['data_vars'].items():
   data['data_vars'][key]['data'] = [np.nan if isinstance(x,str) else x for x in value['data'] ]

  # re-create xarray Dataset
  if asXarray:
    from xarray import DataArray, Dataset
    data = Dataset.from_dict(data)

  # Convert time from string to datetime64 if you want. 
  if asDatetime64:
    if not(asXarray):
      raise ValueError('asXarray must be set for asDatetime64 converstion')
    import pandas
    data['time'].values = pandas.to_datetime(data['time'].values)

  return(data)



def UpdatePublisehedForecasts():
  """
  Commit forecasts to the web.
  - requires that the git copy is set up correctly.
  - does not actually update the local files first, use UpdateLocalForecast from pet_extraction_lib for that.
  """
  import git

  repo_dir=config.git_local_root
  r = git.Repo.init(repo_dir)
  
  currentDT = datetime.datetime.now()
  timeStr = currentDT.strftime("%Y-%m-%d %H:%M:%S")
  r.git.add(update=True)
  if config.debug:
    print("Updating forecasts on git: " + timeStr)
  r.index.commit("Forecast updated: " + timeStr)
  r.remote('origin').push(force=True)
  

