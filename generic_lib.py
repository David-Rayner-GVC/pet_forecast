# -*- coding: utf-8 -*-
"""
Genericly-useful routines for processing ICON files for PET forecast.

@author: xrayda
"""

import os

import config



def CheckDirExists(dir_name):
  """
  If a directory doesn't exist, create it.
  Works recursively, like os.makedirs
  """
  if not os.path.isdir(dir_name):
    if config.debug:
      print('Creating dir %s' % dir_name)
    os.makedirs(dir_name)
    
def RemoveFile(fname):
   """
   remove a file, no questions
   """
   if os.path.exists(fname):
     os.remove(fname)