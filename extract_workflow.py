# -*- coding: utf-8 -*-
"""
Just extrac time-series and update git-hosted PET forecast data.

@author: xrayda
"""
import config

import pet_extraction_lib as pel
pel.UpdateLocalForecast(stash=True)

import plotting
plotting.UpdateLocalPlots(useLocalData=True, addTime=False)

import pet_git_integration_lib as pgi
pgi.UpdatePublisehedForecasts()


if config.debug:
  print('Update complete')


