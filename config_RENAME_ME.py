# -*- coding: utf-8 -*-
"""
Genericly-useful variables.

@author: xrayda
"""

debug = True
abortOnLastErrorFile = None

# where to get the NWP outputs:
url_root_default = 'https://opendata.dwd.de/weather/nwp/icon-eu/grib/'

# where to download NWP data for processing:
target_root = '/LOCALDATA/PET__forecast/icon-eu/'

# where to retrieve the latest PET forecasts
git_url_root = 'https://raw.githubusercontent.com/David-Rayner-GVC/pet_data/master/'

# git local root - repository where we dump pet forecast time-series
git_local_root = '/LOCALDATA/PET__forecast/pet_data'

# csv file with locations. 
# EITHER a url or a local file name. Presumably uncomment one of:
locations_file = git_local_root + '/' + 'locations_config.csv'
#locations_file = git_url_root + 'locations_config.csv'

# stash_root - directory where we keep a record of forecasts as netcdf
stash_root = '/LOCALDATA/PET__forecast/pet_stash'   

# Where to write the plots. None for no plots
plot_root = '/LOCALDATA/PET__forecast/plots'

# temporary dir for processing, must be deletable!
tmp_dir = '/LOCALDATA/PET__forecast/icon-eu/tmp_'

PET_vars = ('ASWDIFD_S', 'ASWDIR_S', 'QV_2m','PMSL','T_2M','U_10M','V_10M')

variable_names = {'ASWDIFD_S':'ASWDIFD_S', 'ASWDIR_S':'ASWDIR_S', 'QV_2M':'QV_2M',
                  'PMSL':'prmsl','T_2M':'2t','U_10M':'10u','V_10M':'10v'}

standard_names = {'ASWDIFD_S':'downward_diffuse', 
'ASWDIR_S':'downward_direct',
'QV_2M':'specific_humidity',
'PMSL':'mslp',
'T_2M':'air_temperature',
'U_10M':'eastward_wind',
'V_10M':'northward_wind'}



