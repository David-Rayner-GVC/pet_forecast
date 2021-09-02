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

# where to commit PET forecasts
git_url_root = 'https://api.github.com/repos/David-Rayner-GVC/pet_data/contents/'

# git local root - repository where we dump pet forecast time-series
git_local_root = '/LOCALDATA/PET__forecast/pet_data'

# the name of the csv file with the locations for pet_forecasts
# JUST THE FILENAME - script looks in git_local_root folder!
locations_file_name = 'locations_config.csv'

# stash_root - directory where we keep a record of forecasts as netcdf
stash_root = '/LOCALDATA/PET__forecast/pet_stash'   

# temporary dir for processing, must be deletable!
tmp_dir = '/LOCALDATA/PET__forecast/icon-eu/tmp_'

PET_vars = ('ASWDIFD_S', 'ASWDIR_S', 'RELHUM_2M','T_2M','U_10M','V_10M')

variable_names = {'ASWDIFD_S':'ASWDIFD_S', 'ASWDIR_S':'ASWDIR_S', 'RELHUM_2M':'2r','T_2M':'2t','U_10M':'10u','V_10M':'10v'}

standard_names = {'ASWDIFD_S':'downward_diffuse', 
'ASWDIR_S':'downward_direct',
'RELHUM_2M':'relative_humidity',
'T_2M':'air_temperature',
'U_10M':'eastward_wind',
'V_10M':'northward_wind'}



