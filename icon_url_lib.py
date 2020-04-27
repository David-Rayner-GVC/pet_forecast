
# -*- coding: utf-8 -*-
"""
Base routines for processing ICON files for PET forecast.

This library contains routines that are independent of the ICON data structure.

@author: xrayda
"""

import os
import requests
from lxml import html
from urllib.parse import urljoin
import re
import datetime
import wget

import config
import icon_generic_lib

class icon_url_lib:
  def __init__(self, url_root=None ):
    if url_root == None:
      self.url_root = config.url_root_default
    if re.match('\S+grib', self.url_root)==None:
        self.url_root = urljoin(self.url_root ,'grib/')
        
  def GetFileNames(self,hh,cvar):
    """
    Get list with the names of all bz2 for a variable
    eg
    GetFileNames('15','aswdir_s')
    """
    url = urljoin(self.url_root , hh + '/' + cvar + '/')
    page = requests.get(url)
    tree = html.fromstring(page.content)
    file_list = tree.xpath('//pre/a/@href')[1:]
    
    if not file_list:
        raise Exception('file_list was empty or problem for %s' % url)
    return(file_list)

  def DownloadCvarFiles(self, hh, cvar, grib_dir):
    """
    Download all bz2 for a climate variable.
    Inputs:
      ii.DownloadCvarFiles('15','aswdir_s', grib_dir)
      grib_dir - where to download to. An actual directory, not a subdir of config.target_dir
      cvar string. is not case-sensitive
    """
    file_list=self.GetFileNames(hh,cvar.lower())
    icon_generic_lib.CheckDirExists(grib_dir)
    
    for f in file_list:
      u = urljoin(self.url_root , hh + '/' + cvar.lower() + '/' + f)
      target_file = os.path.join(grib_dir,f)
      wget.download(u, target_file)
      if config.debug:
        print('download %s' % u)

  def GetFirstDate(self, hh):
    """
    Get date-stamp of first variable for a forecast hour.
    Inputs - hh - time as str eg '15'
    Return as datetime.
    """
    url = urljoin(self.url_root , hh + '/')
    page = requests.get(url)
    tree = html.fromstring(page.content)
    date_as_text = tree.xpath('//pre/text()')[1].rstrip()[0:-1].strip()
    date_time_obj = datetime.datetime.strptime(date_as_text, '%d-%b-%Y %H:%M')
    return(date_time_obj)
    
  def GetTimeOfMostRecent(self):
    """
    return string time of most recently-updated forecast

    """

    hh_list = ('00','03','06','09','12','15','18','21')
    CG = lambda x : self.GetFirstDate(urljoin(self.url_root , x))
    ND = list(map(CG, hh_list) )
    return(hh_list[ND.index(max(ND))])
