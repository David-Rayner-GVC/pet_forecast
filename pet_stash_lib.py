# -*- coding: utf-8 -*-
"""
Merging a forecast to a local stash  
"""

import os
import config
import numpy as np
from generic_lib import *
import xarray as xr


def _MakeStashable(xd):
  """ 
  change time to offset, add time coord
  xd - as output from ExtractPETForecastData
  """
  offset_array = np.int32((xd.time - xd.time[0])*1e-9) 
  
  st = xd.copy()
  st=st.rename({'time':'offset'})
  st=st.assign_coords({"offset": offset_array})
  st=st.assign_coords(time=xd.time[0]) 
  return st
  
def StashSingleForecast(xd,filename=None,overwrite=False):
  """
  Add the forecast to an existing Stash file
  or create a new file if non exists.
  xd - from ExtractPETForecastData
  if no filename is specified, try to determine one from xd.Name
  """
  st = _MakeStashable(xd)
  if (filename==None):
    CheckDirExists(config.stash_root)
    filename=os.path.join(config.stash_root, str(st.Name.data)+'.nc')
      
  if overwrite or not(os.path.exists(filename)):
    if config.debug:
      print('Creating new stash file: '+filename)
    # just write it
    st.to_netcdf(filename)
  else:
    xList=list()    
    with xr.open_dataset(filename) as old_st:
      if st.time.data.max() > old_st.time.data.max():
        if config.debug:
          print('Appending to stash file: '+filename)
        xList.append(old_st)
        xList.append(st)
        # ok, but actually we want to concat a dataset to a netcdf!
        st_new = xr.concat(xList, dim='time')  
        RemoveFile(filename+'backup')
        os.rename(filename,filename+'backup')
        st_new.to_netcdf(filename)
      else:
        if config.debug:
          print('No new data to add to stash file '+filename)


    

  