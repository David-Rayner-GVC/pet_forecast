# pet_forecast
Create physiological equivalent temperature (PET) forecasts from opendata.dwd.de NWP.

 - modify config_RENAME_ME.py to represent your local setup
 
Three workflows are provided:
 - workflow to download and pre-process NWP files
 - workflow to extract (and optionally publish to GIT) forecast-time-series for a particular location.
 - workflow to download time-series for a particular location (for example to show in an app or on a website).
 
 Currently PET is NOT computed! that is, the client would have to do that themselves. We'll get around to that eventually...
 
