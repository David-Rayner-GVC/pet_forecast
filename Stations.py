"""
Stations.py

Class for getting rows from a 'locations_config.csv' file.

File should be csv, with columns:
Id,Name,Latitude,Longitude,Height (m)

where Id is a numeric label, Name is string.

Location is (by default) specified in config.locations_file

"""
import config
import os
import pandas as pd

class Stations:
  def __init__(self, fname=None):
    # load dictionary of stations
    if fname==None:
      fname = config.locations_file
    try:
      self.stations = pd.read_csv(fname) 
    except:
      print("Unable to read the dictionary of stations\n>>> Set config.locations_file to a local file in the pet_data clone, or a git hub raw url??\n")
      raise

    
  def GetRow(self, ID=None, Name=None):
    """
    Get a station by ID or name.
    Return a dictionary for the row. With both ID and name=None, return all rows.
    """
    df=self.stations
    if ID!=None:
      df = df.loc[df['Id'] == ID]
    if Name!=None:
      df = df.loc[df['Name'] == Name]
    return df

  def AllNames(self):
    "Return all the names as a list"
    return self.stations.Name.values.tolist()

