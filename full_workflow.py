# -*- coding: utf-8 -*-
"""
Full workflow to update git-hosted PET forecast data.

NO PET is calculated, yet! Just the met data!

@author: xrayda
"""

# Workflow 1 - assemble grids on local host

import icon_url_lib as iu
import gridded_file_lib as gf

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
import pet_git_integration_lib as pgi

pgi.UpdateLocalForecast()
pgi.UpdatePublisehedForecasts()




