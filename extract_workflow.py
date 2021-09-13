# -*- coding: utf-8 -*-
"""
Just extrac time-series and update git-hosted PET forecast data.

@author: xrayda
"""
import config

# Workflow 2 - extract time-series & udpate the distributed copies on GIT
import pet_git_integration_lib as pgi
import pet_extraction_lib as pel

pel.UpdateLocalForecast(stash=True)
pgi.UpdatePublisehedForecasts()

import plotting
plotting.UpdateLocalPlots(useLocalData=True, addTime=False)


if config.debug:
  print('Update complete')


