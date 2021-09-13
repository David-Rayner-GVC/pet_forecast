# -*- coding: utf-8 -*-
"""
Full workflow to update git-hosted PET forecast data.

@author: xrayda
"""

# Workflow 1 - assemble grids on local host

import icon_url_lib as iu
import gridded_file_lib as gf
import config
import sys, os
from generic_lib import *

ole_file = config.abortOnLastErrorFile
if not(ole_file==None):
  if os.path.exists(ole_file):
    if config.debug:
      print('Aborting because of previous error')
    sys.exit(1)
  else:
    open(ole_file, 'a').close()

# download the latest forecast grids
ii = iu.icon_url_lib()

hh = ii.GetTimeOfMostRecent()
if config.debug:
  print('Latest forecast is hour '+hh)

gf.Cleanout()
gf.DownloadPETForecastData(hh)

# perform preprocessing on the grids
gf.Concatenate()
gf.PostProcessForecastData()

# Workflow 2 - extract time-series & udpate the distributed copies on GIT
import pet_extraction_lib as pel
pel.UpdateLocalForecast(stash=True)

import pet_git_integration_lib as pgi
pgi.UpdatePublisehedForecasts()

if not(ole_file==None):
  RemoveFile(ole_file)

if config.debug:
  print('Update complete')



