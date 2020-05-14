# -*- coding: utf-8 -*-
"""
Retrieve forecast data from GIT
"""

import config
import os
import json
import numpy as np

import base64
import requests
import git
import datetime

class Stations:
  def __init__(self):
    # load dictionary of stations
    import pandas as pd 
    fname = os.path.join(config.git_local_root, config.locations_file_name)
    self.stations = pd.read_csv(fname) 
    
  def Name(self,name):
    """
    Get a station by name.
    Return a dictionary for the row
    """
    df=self.stations
    rw=df.loc[df['Name'] == name]
    return rw   

  def ID(self,ID):
    """
    Get a station by ID.
    Return a dictionary for the row
    """
    df=self.stations
    rw=df.loc[df['Id'] == ID]
    return rw    


def GetContent(url, urlIsFull=True, asJSON=False, asString=False):
  """
  Internal function . Just get the content of a git url.
  If urlIsFull=False, append url to config.git_url_root
  If asJSON, assume content is JSON and convert it to a dict
  If asString, decode to UTF-8
  """
  if not(urlIsFull):
    url=config.git_url_root + url
  
  req = requests.get(url)
  if req.status_code == requests.codes.ok:
      req = req.json()  # the response is a JSON
      # req is now a dict with keys: name, encoding, url, size ...
      # and content. But it is encoded with base64.
      content = base64.b64decode(req['content'])
  else:
      print('Content was not found.')

  if asJSON:
    content = json.loads(content)  
    
  if asString:
    content = content.decode("utf-8")
  
  return content

def RetrieveForecast(Name=None, ID=None, asXarray=True, asDatetime64=True):
  """
  Retrieve a forecast from GitHub.
  
  ID - the numeric ID of the station that you want
  Name - the Name of the station that you want (no .json suffix)
  
  asXarray - return xarray, rather than a dictionary
  asDatetime64 - convert dates from string to asDatetime64
 
  """
  if (Name==None) and not(ID==None):
    # get the Name using the station list on git pet_json
    from io import StringIO
    import csv
    
    url = config.git_url_root + 'locations_config.csv'
    st = GetContent(url, asString=True)
    
    f = StringIO(st)
    reader = csv.reader(f, delimiter=',')
    for row in reader:
      if str(row[0])==ID:
        Name=row[1]
        break
  
  url = config.git_url_root + 'json/' + Name + '.json'
  
  data = GetContent(url, asJSON=True)
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


def UpdateLocalForecast(ID=None, name=None, stash=False, withPET=True):
  """
  Extract data, write to JSON
  File locations are controlled in config.py 
  ID is currently string name of forecast
  
  """
  import pet_extraction_lib as pel
  import pet_stash_lib as ps
  
  st = Stations()
  
  df=st.stations
  if not(ID==None):
    df=st.ID(ID)
  if not(name==None):
    df=st.Name(name)

  for index, d in df.iterrows():
    xd=pel.ExtractPETForecastData(lat=d['Latitude'], lon=d['Longitude'],withPET=withPET)
    xd=xd.assign_coords(Name=d['Name']) 
    xd=xd.assign_coords(Id=d['Id']) 

    json_file=os.path.join(config.git_local_root, 'json', d['Name'] + '.json')
    if config.debug:
      print('updating '+json_file)
    pel.WritePETForecastJSON(xd, json_file)
    if stash:
      # stash here
      ps.StashSingleForecast(xd)

def UpdatePublisehedForecasts():
  """
  Commit forecasts to the web.
  - requires that the git copy is set up correctly.
  - does not actually update the local files first, use UpdateLocalForecast for that.
  """
  repo_dir=config.git_local_root
  r = git.Repo.init(repo_dir)
  
  currentDT = datetime.datetime.now()
  timeStr = currentDT.strftime("%Y-%m-%d %H:%M:%S")
  r.git.add(update=True)
  if config.debug:
    print("Updating forecasts on git: " + timeStr)
  r.index.commit("Forecast updated: " + timeStr)
  r.remote('origin').push(force=True)
  

