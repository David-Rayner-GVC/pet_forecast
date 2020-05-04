# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 15:44:35 2020

@author: xrayda
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import os
import glob
import shutil
import re
import subprocess
import datetime
from cdo import Cdo

import config
from generic_lib import *
import icon_url_lib as iu

try:
    from subprocess import DEVNULL # py3k
except ImportError:
    DEVNULL = open(os.devnull, 'wb')


def _ConvertGrib(source_file, target_dir):
  """
  Unzip/convert a single file
  
  source_file - path to .bz2 equiv file
  target_dir - path to where  .nc will be created
  """
  
  grib_source, ext  = os.path.splitext(source_file)

  if ext == '.bz2':
    if os.path.isfile(source_file):
      el = 'bunzip2 %s' % (source_file)
      if config.debug:
        print(el)
      subprocess.call(el, shell=True, stderr=DEVNULL)
    else:
      if config.debug:
        print('Missing bz2 file - skipping unzip: %s' % source_file)   
  else:
    # assume a grib2 file
    grib_source = source_file

  grib_path, grib_name = os.path.split(grib_source)
  
  nc_source, ext  = os.path.splitext(grib_name)
  nc_source = nc_source + '.nc'
  
  if ext == '.grib2':
    CheckDirExists(target_dir)
    full_nc_source = os.path.join(target_dir, nc_source)

    el = 'cdo -O -f nc setgridtype,regular %s %s ' % (grib_source, full_nc_source)
    if config.debug:
      print(el)
    p = subprocess.call(el, shell=True) #, stderr=DEVNULL)
  else:
    raise ValueError('File not a grib file: %s' % grib_source)
  
  if not os.path.isfile(full_nc_source):
      raise ValueError('Unable to create target file %s, return status' % p)
  return(full_nc_source)

def _ConvertVar(source_dir, target_dir):
  """
  Unzip/convert all files in a directory
  source_dir - path to dir containing .bz2 equiv file
  target_dir  - path to where .nc will be created
  """
  if config.debug:
    print(source_dir + ' -> ' + target_dir)
  D = os.listdir(source_dir)
  CG = lambda x : _ConvertGrib(os.path.join(source_dir,x) , target_dir)

  ND = list(map(CG,D)) 
  return(ND)
  
def _ConcatenateNetcdf(source_dir, target_dir):
  """
  concatenate all netcdf files in a directory!
  output is written to target_dir
  full path of target file is returned.
  """
  infiles = os.listdir(source_dir)
  
  template = infiles[0]
  if config.debug:
    print('template: %s' % template)

  result = re.split('_',template)
  nc_file = '_'.join(result[0:5]) + '_' + '_'.join(result[6:])
  target_file = os.path.join(target_dir, nc_file)
  
  CheckDirExists(target_dir)
  
  el = 'cd %s ; cdo -O mergetime %s %s' % (source_dir, '*.nc', target_file)
  if config.debug:
    print(el)
    
  p = subprocess.call(el, shell=True) #, stderr=DEVNULL)
  
  if not os.path.isfile(target_file):
    raise Exception('Could not create target file: %s' % target_file)
  return(target_file)

  
def DownloadPETForecastData( hh, target_root=None, vars=None, url_root=None, overwrite=False):
  """
  Step two of the processing chain!
  
  Download set of files for a forecast.
  Convert from grib to netcdf.
  
  Inputs.
    hh - eg '03'
    target_root. default from config.py eg '/mnt/c/Users/xrayda/LOCALDATA/PET__forecast/icon-eu/
    vars - default from config.py 
    url_root . default from config.py 'https://opendata.dwd.de/weather/nwp/icon-eu/'
Outputs
    dictionary of created files, keys are vars, values are full-paths.
	
  This function:
   - downloads the files to $target_root/grib
   - converts them to netcdf to $garget_root/netcdf
  It does concatenate or deaverage
  """
  
  ii = iu.icon_url_lib(url_root)
  
  if target_root==None:
    target_root = config.target_root
    
  if vars==None:
      vars = config.PET_vars
      
  for v in vars:
    grib_dir =  os.path.join(target_root,'grib',v )
    CheckDirExists(grib_dir)
    if len(os.listdir(grib_dir))==0  or overwrite:
      ii.DownloadCvarFiles(hh,v,grib_dir)
    nc_dir = os.path.join(target_root,'netcdf',v)
    _ConvertVar(grib_dir, nc_dir)

  
def Concatenate():
  """
  Concatenate step in the processing:
  netcdf -> netcdf_concat
  """
  
  target_root = config.target_root
  vars = config.PET_vars
  
  concatFiles=dict()
      
  for v in vars:
    nc_dir = os.path.join(target_root,'netcdf',v)
    nccat_dir = os.path.join(target_root,'netcdf_concat')
    concatFiles[v] = _ConcatenateNetcdf(nc_dir, nccat_dir)
  return(concatFiles)
  
def Cleanout(target_root=None):
  """
  For now, just remove all files/directories under the top level
  """
    
  if target_root==None:
    target_root = config.target_root
    
  if config.debug:
      print('Cleaout %s' % target_root)
	  
  targets = ('grib', 'netcdf', 'netcdf_concat','netcdf_final','deaverage')
      
  for t in targets:
    fileList = glob.glob(os.path.join(target_root,t,'*'), recursive=False)
    for filePath in fileList:
      if os.path.isdir(filePath):
        shutil.rmtree(filePath)
      else:
        os.remove(filePath)

      
def _DeAccumulate(input,output):
  """
  de-aggregate a file - ie calculate time-step differences
  """
  cdx = Cdo()
  # calculate number of steps in the file:
  nstep = int(cdx.ntime(input=input)[0])
  #nstep=`cdo -s ntime $file`

  # do difference between steps 2:n and steps 1:(n-1)
  #cdo sub -seltimestep,2/$nstep $file -seltimestep,1/`expr $nstep - 1` $file  diff.nc
  inputs = (nstep, input, nstep-1, input)
  cdx.sub(input='-seltimestep,2/%i %s -seltimestep,1/%s %s' % inputs, output=output)
  
          
def _DeAverage(input, output, cvar, new_long_name, tmp_dir):
  """
  Some forecasts are given as average over the forecast time. 
  Needless to say, this is completely useless for any real-world application.
  This function de-averages the files.
  
  For such averaged files, the values for the first time-step is always zero.
  Thus, in the deaveraged files, the first time-step is one hour after the 
  first time-step in the input files, and the value is the average over the
  hour up to the time-stamp.
  
  input - input netcdf filename, multi-hour file.
  output - output netcdf file name. 
  cvar - name of the variable to de-average. Ok, I am lazy, I could have found 
         this by inspection...
  new_long_name - the string written to the variable long_name attribute.
  tmp_dir - director to write tmp files. Will be created in the function and
            deleted on completion (unless there is an error and debug=True), 
            so dont give '/tmp' or similar... 
  """ 
  cdx = Cdo()
  
  CheckDirExists(tmp_dir)
  
  success=False
  try:
   
   sumfile=os.path.join(tmp_dir,'sumfile.nc')
   difffile=os.path.join(tmp_dir,'difffile.nc')
   cdx.expr('\'%s= %s * (ctimestep()-1);\'' % (cvar, cvar), input=input, output=sumfile)
   _DeAccumulate(sumfile,difffile)
   cdx.setattribute('%s@long_name=\'%s\'' % (cvar,new_long_name), input=difffile, output=output)
   
#   ntime = int(cdx.ntime(input=input)[0])
#   op1 = '-seltimestep,1/%i/1 %s' % (ntime-1, input)
#   op2 = '-shifttime,+1hour %s' % op1
#   p_tr3 = os.path.join(tmp_dir,'p_tr3.nc')
#   cdx.chname('%s,prev' % cvar, input=op2, output=p_tr3)
#   
#   mergefile=os.path.join(tmp_dir,'mergefile.nc')
#   difffile=os.path.join(tmp_dir,'difffile.nc')
#   op3 = '-seltimestep,2/%i/1 %s' % (ntime,input)
#   cdx.merge(input=op3 +' '+p_tr3, output=mergefile)  
#   cdx.expr('\'%s=(%s-prev) * ctimestep();\'' % (cvar, cvar), input=mergefile, output=difffile)
#   
#   cdx.setattribute('%s@long_name=\'%s\'' % (cvar,new_long_name), input=difffile, output=output)
   
   success = True
   if config.debug:
     print('DeAaverage %s -> %s' % (input, output))
  finally:
   if success or not(config.debug):
    shutil.rmtree(tmp_dir)  
    
def IndexLocalForecastData(target_root=None):
  """
  This is a debugging function to index the netcdf_concat directory so you
  can test postprocessing without having to run    DownloadPETForecastData
  """
  if target_root==None:
    target_root = config.target_root
    
  concatFiles=dict()
  fileList = glob.glob(os.path.join(target_root,'netcdf_concat','*'), recursive=False)
  for filePath in fileList:
    path_, name_ = os.path.split(filePath)
    root_, ext  = os.path.splitext(name_)
    result = re.split('_',root_)
    cvar = '_'.join(result[5:])
    concatFiles[cvar] = filePath
  return(concatFiles)
    
def PostProcessForecastData(tmp_dir=None):
  """
  Perform post-processing steps:
  create deaverage files for aswdir_s and aswdifd_s
  """
  if tmp_dir==None:
    tmp_dir = config.tmp_dir
  
  target_root = config.target_root
  
  CheckDirExists(os.path.join(target_root,'deaverage'))
  CheckDirExists(os.path.join(target_root,'netcdf_final'))
  
  cvar = 'ASWDIR_S'
  input = glob.glob(os.path.join(target_root,'netcdf_concat','*'+cvar+'*'), recursive=False)[0]
  fpath, filename = os.path.split(input)
  output = os.path.join(target_root,'deaverage',filename)
  new_long_name= "Downward direct short wave radiation flux at surface (mean over hour time time-stamp)"
  _DeAverage(input, output, cvar, new_long_name, tmp_dir)
  # and a symlink for netcdf_final
  lnk = os.path.join(target_root,'netcdf_final',filename)
  RemoveFile(lnk)
  os.symlink(output, lnk) 
  
  cvar = 'ASWDIFD_S'
  input = glob.glob(os.path.join(target_root,'netcdf_concat','*'+cvar+'*'), recursive=False)[0]
  fpath, filename = os.path.split(input)
  output = os.path.join(target_root,'deaverage',filename)
  new_long_name= "Downward diffusive short wave radiation flux at surface (mean over hour time time-stamp)"
  _DeAverage(input, output, cvar, new_long_name, tmp_dir)
  # and a symlink for netcdf_final
  lnk = os.path.join(target_root,'netcdf_final',filename)
  RemoveFile(lnk)
  os.symlink(output, lnk) 
  
  vars2 = list(config.PET_vars)
  vars2.remove('ASWDIFD_S')
  vars2.remove('ASWDIR_S')
      
  for cvar in vars2:
    input = glob.glob(os.path.join(target_root,'netcdf_concat','*'+cvar+'*'), recursive=False)[0]
    fpath, filename = os.path.split(input)
    lnk = os.path.join(target_root,'netcdf_final',filename)
    RemoveFile(lnk)
    os.symlink(input, lnk) 
    

  # for key, value in files2copy.items():
    # fpath, filename = os.path.split(value)
    # output = os.path.join(target_dir, 'nc4classic', filename)
  # # now move to nc4classic
  # CheckDirExists(os.path.join(target_dir,'nc4classic'))


          
if __name__ == "__main__":
  # to run as a script
  ii = iu.icon_url_lib()
  
  hh = ii.GetTimeOfMostRecent()
  #hh = '15'
  
  Cleanout()
  DownloadPETForecastData(hh)
  Concatenate()
  PostProcessForecastData()
  

  
