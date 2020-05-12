# pet_forecast
Create physiological equivalent temperature (PET) forecasts from opendata.dwd.de NWP.

Installation:
Not really documented. 
 - You will need to be able to make git push to pet_json using ssh. GitPython
 - need cdo Climate Data Operators, and Python CDO (pycdo). Netcdf4, obviously. 
 - modify config_RENAME_ME.py to represent your local setup
 
The script full_workflow:
 - download and pre-process NWP files to local netcdf, one file for each variable. 
 - extract (and publish to GIT) forecast-time-series for a particular locations, based on pet_json
 - stash the forecasts in local netcdf files, one per location, for future analysis.
 
 To-Do
  - Currently PET is NOT computed! that is, the client would have to do that themselves. We'll get around to that eventually...
  - No checks whether local grid files are up-to-date, they are just downloaded. This can break things if a new forecast is being written (see below)
  - no optimization of the time-series extraction, it is just a loop over locations. So the netcdf files are opened/closed/re-opened many times. But hey, that is what file-system caching is for, and it seems to run fast enough. 
  
Things that can go wrong:
  - if the download starts before DWD has finished writing out the files for a new forecast, the script will fail with a warning about non-unique time-series. To minimize problems, the script is run at UTC+2 times:

local times for long runs:
6, 12, 18, 24
local times for short runs:
2,8,14,20

I guess this will break if we go back to winter time...

  - If you have a dev setup, you can stop the git updates as you create merge conflicts on the production setup. 


