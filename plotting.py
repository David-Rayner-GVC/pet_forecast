"""

For plotting PET forecast data!


"""

import datetime
import matplotlib.dates as mdates
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import table
from pathlib import Path
from PIL import Image
from Stations import Stations
import config
import generic_lib

def forecast_plot(xr, output_dir='.', addTime=True, format='png', swedish=False):
  """
  make a plot, save to disk by default!
  
  import config
  import pet_git_integration_lib as pgi
  import plotting
  
  xr = pgi.RetrieveForecast(Name='Gothenburg')
  plotting.forecast_plot(xr)
  
  Inputs:
    xr         - xarray with forecast data
    output_dir - where to write to. Default '.'. None for no output file. 
    addTime    - append forecast time to the output filename
    format - file format
    swedish - not implemented
  Returns:
    plt, the plot. So call plt.close() to tidy up after yourself. 
  """
  
  base_fontsize=12
  
  def UsualSuspects(ax, topPlot=False, asInt=True):
    "internal function to format an axis"
    #pad = (ax.get_yticks()[-1] - ax.get_yticks()[0])/50
    #ax.set_ylim([ax.get_yticks()[0]-pad, ax.get_yticks()[-1]+pad])  
    if topPlot:
      ax.set_xticks(xticks)
      ax.set_xticklabels(xticklabels, fontsize=base_fontsize)
    else:
      ax.set_xticks(xticks2)
      ax.set_xticklabels(xticklabels2, fontsize=base_fontsize)
    ax.tick_params(axis='x', rotation=0)
    for tick in ax.xaxis.get_major_ticks():
      tick.label1.set_horizontalalignment('center')
    for index, value in enumerate(day_label_x):
      ax.text(value + datetime.timedelta(hours = 1), ax.get_ylim()[0], ' ' + day_label_labels[index], horizontalalignment='center',
       verticalalignment='bottom', color = "black", fontsize=base_fontsize, 
       rotation=90)
#    if asInt:
#      t = ax.get_yticks().astype(int)
#      #print(t)
#      ax.set_yticklabels(t, fontsize=base_fontsize*1.5)
#    else:
#      ax.set_yticklabels(np.round(ax.get_yticks(), decimals=4), fontsize=base_fontsize*1.5)
    ax.tick_params(axis='y', which='major', labelsize=base_fontsize)
    # 0.88 for inside
    ax.text(0.05, 1.14, plotTitle, horizontalalignment='left',
       verticalalignment='center', transform=ax.transAxes, fontsize=base_fontsize*2)
    td_offset = 1000000000000 #timedelta.Timedelta(hours=0.5)
    ax.set_xlim(df.index.values.min() - td_offset, df.index.values.max()+td_offset)
    ax.set_xlabel(None) 
    ax.set_ylabel(yLabel, fontsize=base_fontsize*1.5)
    ax.text(-0.015/(1 + topPlot), -0.085, "UTC", horizontalalignment='right',
       verticalalignment='center', transform=ax.transAxes, fontsize=base_fontsize)

  df = xr.to_dataframe()
  df['Date']=xr.time.values
  df = df.set_index('Date')     
  
  
  station_name  = str(xr.Name.values)

  # create filename from time and Name
  d = xr['time'].values[0]  
  if addTime:
   fname = station_name + '_' + np.datetime_as_string(d, unit='h',timezone='UTC') + '.' + format
  else:
   fname = station_name + '.' + format
   
  # linewidth
  linewidth = 3.0

  # x tick formatting
  idx =  (df.index.hour.values % 3) < 0.1 
  xticks = df.index[idx] 
  xticklabels = xticks.hour.values 
  
  idx =  (df.index.hour.values % 6) < 0.1 
  xticks2 = df.index[idx] 
  xticklabels2 = xticks2.hour.values 
  
  idx = df.index.hour.values == 0
  idx[0] = True
  day_label_x = df.index[idx] 
  day_label_labels = day_label_x.strftime('%Y-%m-%d')

#  fig, axes = plt.subplots(nrows=5, ncols=1, figsize=(14.4,9.0), dpi=100.0)
  fig = plt.figure(tight_layout=True, figsize=(14.4,9.0), dpi=100.0)
  gs = fig.add_gridspec(3,2)
  ax0 = fig.add_subplot(gs[0, :])
  ax1 = fig.add_subplot(gs[1, 0])
  ax2 = fig.add_subplot(gs[1, -1])
  ax3 = fig.add_subplot(gs[-1, 0])
  ax4 = fig.add_subplot(gs[-1, -1])

  fig.suptitle(str(xr.Name.values), y=0.99, fontsize=base_fontsize*3)

  # Tmrt, PET, air temp
  df['air_temperature'].plot(ax=ax0, color="silver", linewidth=linewidth, marker='o', label='Air temp.', grid=True)
  df['PET'].plot(ax=ax0, color="orchid", linewidth=linewidth, marker='o', label="PET", grid=True)
  df['UTCI'].plot(ax=ax0, color="darkorange", linewidth=linewidth, marker='o', label="UTCI", grid=True)
  plotTitle = 'Heat Indicators'
  yLabel = "($^\circ$C)"
  UsualSuspects(ax0,topPlot=True)
  ax0.legend(fontsize=base_fontsize)
  
  df['Tmrt'].plot(ax=ax1, color="royalblue", linewidth=linewidth, grid=True)
  plotTitle = "T$_{mrt}$"
  yLabel = "($^\circ$C)"
  UsualSuspects(ax1)

  df['relative_humidity'].plot(ax=ax2, color="royalblue", linewidth=linewidth, grid=True)
  plotTitle = 'Relative humidity'
  yLabel = "(%)"
  UsualSuspects(ax2)
  
  df['downward_diffuse'].plot(ax=ax3, color="skyblue",  label="Diffuse", linewidth=linewidth, grid=True)
  df['downward_direct'].plot(ax=ax3, color="darkorange",  label="Direct", linewidth=linewidth, grid=True)
  plotTitle = 'Solar radiation'
  yLabel = "(W.m$^2$.s)"
  UsualSuspects(ax3)
  ax3.legend(fontsize=base_fontsize)
  #ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
  
  df['wind_speed'].plot(ax=ax4, color="royalblue", linewidth=linewidth, grid=True)
  plotTitle = 'Wind speed'
  yLabel = "(m/s)"
  UsualSuspects(ax4)
  #ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
  
  im = Image.open('links.png')
  width = im.size[0]
  height = im.size[1]
  fig.figimage(im, fig.bbox.xmax - width, fig.bbox.ymax - height)
  
  #plt.tight_layout(rect=[0, 0.03, 1, 0.95])
  plt.show()
  if output_dir!=None:
    output_dir = Path(output_dir)
    LOCAL_NAME=output_dir / fname
    plt.savefig(LOCAL_NAME, facecolor=fig.get_facecolor(), transparent=True) 
  return plt

def UpdateLocalPlots(useLocalData=True, addTime=True, format='png', swedish=False):
  """
  Make plots for all stations
  
  desination set by config.plot_root
  """
  try:
   if config.plot_root==None:
    return
  except:
    return
  generic_lib.CheckDirExists(config.plot_root)
  
  st = Stations()
  
  if useLocalData:
    from pet_extraction_lib import RetrieveLocalForecast as RetrieveForecast
  else:
    from pet_git_integration_lib import RetrieveForecast 
    
  for name in st.AllNames():
    if config.debug:
      print('updating plot for location:'+name)
    xr = RetrieveForecast(name)
    plt = forecast_plot(xr, output_dir=config.plot_root,
                  addTime=addTime, format=format, swedish=swedish)
    plt.close()
    
    

  