#Import Statements
import matplotlib.pyplot as plt
import matplotlib.pylab as pylab
import numpy as np
from metpy.plots.mapping import CFProjection
import xarray as xr
import pandas as pd
import json
import plotly.graph_objects as go
from mpl_toolkits.axes_grid1 import make_axes_locatable

import geopandas as gpd
from shapely.geometry import LineString, MultiLineString
import plotly.graph_objs as go
import plotly.express as px
import plotly

import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import textwrap
from textwrap import wrap

import geopandas
import datetime
from datetime import date, timedelta, datetime
import requests, zipfile, io

import os
import glob

from geopy.geocoders import Nominatim
from scipy.spatial import cKDTree
from shapely.geometry import Point
from metpy.plots import ctables

import pyart

import pytz
import nexradaws
from scipy.special import y1_zeros

import boto3
import botocore
from botocore.client import Config
import cv2

import argparse  # Import the argparse module

# Setting Days
#day_yesterday = pd.to_datetime(date.today() - timedelta(days=1))
# Create the argument parser

parser = argparse.ArgumentParser(description='text file generation for a specific date.')
# Add the 'date_input' argument
parser.add_argument('date_input', type=str, help='Date in the format yymmdd (e.g., 230609 for June 9, 2023)')
# Parse the arguments
args = parser.parse_args()

# Extract year, month, day from args.date_input
year = int("20" + args.date_input[:2])  # Prefix "20" for years 2000-2099
month = int(args.date_input[2:4])
day = int(args.date_input[4:6])

# Create a datetime.date object
specific_date = date(year, month, day)

tomorrow = specific_date + timedelta(days=1)
tomorrow_test = tomorrow.strftime('%Y-%m-%d')

#Set days
#today = date.today()
#today_day = date.today().weekday()
#day_yesterday = pd.to_datetime(date.today() - timedelta(days=1))


#It was easier in this code to just rename the variables to the existing variables. 

day_yesterday = specific_date
today = tomorrow

#Read in files
sr_remarks = pd.read_csv('{t:%Y}_{t:%m}_{t:%d}_text_file.csv'.format(t=day_yesterday))

#sr_file = pd.read_csv('/work/wgallus/etirone2/hwt_2023/testing_data/2022_05_31_probs_sub.csv')
sr_file = pd.read_csv('{t:%Y}_{t:%m}_{t:%d}_probs_sub.csv'.format(t=day_yesterday))

sr_df = geopandas.GeoDataFrame(sr_file)
sr_df['stack_glm'] = ((1-sr_df['stack_glm'])*100).round(2)
sr_df['Remarks'] = sr_remarks['Remarks']
sr_df['Time'] = sr_remarks['Time']
sr_df['Lon'] = sr_df['lat']
sr_df['Lat'] = sr_df['lon']

sr_df = sr_df.drop(columns=['gbm', 'svmRadial', 'mxnetAdam', 'stack_rf', 'avg_ens', 'lon', 'lat', 'Unnamed: 0',	'Unnamed: 0.1']).reset_index(drop=True)
sr_df['remarks_new_line'] = np.zeros

#Format remarks to fit on lines better
def wrap(string, max_width):
	return '<br>'.join(textwrap.wrap(string,max_width))

for x in range(len(sr_df)):
	sr_df['remarks_new_line'][x] = (wrap(str(sr_df['Remarks'][x]), 40))

##Collect nearest radar to each storm report

radar_locs = pd.read_csv('radar_locs_updated.csv')

## Change to geodataframes
df_geo = geopandas.GeoDataFrame(sr_df, geometry=geopandas.points_from_xy(sr_df.Lon, sr_df.Lat))
radar_geo = geopandas.GeoDataFrame(radar_locs, geometry=geopandas.points_from_xy(radar_locs.lon_deg, radar_locs.lat_deg))

### Find nearest radar and concatenate radar information to df
# Initialize Nominatim API
geolocator = Nominatim(user_agent="MyApp")
def ckdnearest(gdA, gdB):

	nA = np.array(list(gdA.geometry.apply(lambda x: (x.x, x.y))))
	nB = np.array(list(gdB.geometry.apply(lambda x: (x.x, x.y))))
	btree = cKDTree(nB)
	dist, idx = btree.query(nA, k=1)
	gdB_nearest = gdB.iloc[idx].drop(columns="geometry").reset_index(drop=True)
	gdf = pd.concat(
	[
	gdA.reset_index(drop=True),
	gdB_nearest,
	pd.Series(dist, name='dist')
	],
	axis=1)

	return gdf

nearest = ckdnearest(df_geo, radar_geo)
print(nearest)

# Set colortable
cmap = ctables.registry.get_colortable('NWSReflectivity')



## Collect radar timestamps

### Loop through each of the reports and plot each one
## Save radar images based on index/event_id



today = pd.to_datetime(date.today()).replace(hour=12, minute=00)
yesterday = pd.to_datetime(date.today() - timedelta(days=1)).replace(hour=16, minute=30)

radar_files = []

for z in range(len(nearest)):
  print(nearest['event_id'][z])
  ## Pull all radar files for 1630-12z for one SRs nearest radar
  radar_id = nearest['STATION ID'][z]
  start = yesterday 
  end = today
  try:
    conn = nexradaws.NexradAwsInterface()
    scans = conn.get_avail_scans_in_range(start, end, radar_id)
    print(len(scans))

    ## Set timestamp given all radar scans over period
    link = []
    timestamp = []

    for x in range(len(scans)):
      if len(str(scans[x])) > 64:
        continue
      else:
        link.append(str(scans[x]))
        y = int(str(scans[x])[24:28])
        m = int(str(scans[x])[29:31])
        d = int(str(scans[x])[32:34])
        h = int(str(scans[x])[53:55])
        min = int(str(scans[x])[55:57])
        s = int(str(scans[x])[57:59])
        dt = datetime(y,m,d,h,min,s)
        timestamp.append(dt)

    #Make dataframe of the prefix and timestamp
    df = pd.DataFrame(link, timestamp).reset_index(drop=False)
    df = df.rename(columns={'index': 'Time', 0: 'prefix'})

    # Find time difference from the first SR to each of the prefixes
    diffs = []

    for x in range(len(df)):
      temp_time = datetime(year=nearest['year'][z],month=nearest['month'][z],day=nearest['day'][z],hour=nearest['hr'][z],minute=nearest['min'][z], second=0)
      time = df['Time'][x]
      time_diff = abs((temp_time-time).total_seconds())
      diffs.append(time_diff)

    df['time_diff'] = diffs

    #Get reference ID for minimum time difference
    id = df['time_diff'].idxmin()
    radar_prefix = df['prefix'][id]

    start_time2 = datetime(int(radar_prefix[24:28]), int(radar_prefix[29:31]), int(radar_prefix[32:34]), int(radar_prefix[53:55]), int(radar_prefix[55:57]), int(radar_prefix[57:59]))
    end_time2 = datetime(int(radar_prefix[24:28]), int(radar_prefix[29:31]),int(radar_prefix[32:34]),int(radar_prefix[53:55]),int(radar_prefix[55:57]),int(radar_prefix[57:59]))

    conn2 = nexradaws.NexradAwsInterface()

    print('trying to make images')
    scans_2 = conn2.get_avail_scans_in_range(start_time2, end_time2, radar_id)

    results = conn2.download(scans_2[0], './')

    fig = plt.figure(figsize=(48,16))
    for i,scan in enumerate(results.iter_success(),start=1):
        radar = scan.open_pyart()
        
        display = pyart.graph.RadarMapDisplay(radar)

        ax = plt.subplot(121, projection=ccrs.PlateCarree())

        display.plot_ppi_map(
              "reflectivity",
              sweep=0,
              ax=ax,
              colorbar_label="Equivalent Relectivity ($Z_{e}$) \n (dBZ)",
              vmin=-10,
              vmax=70,
              cmap=cmap
          )
        ax.grid(False)
        params = {'legend.fontsize': 25,
          'axes.labelsize': 25,
          'axes.titlesize': 30}
        pylab.rcParams.update(params)
        
        scatter_sr = ax.scatter(nearest['Lon'][z], sr_df['Lat'][z], transform=ccrs.PlateCarree(), marker='o', zorder=100, c='None', s=600, edgecolor='black', linewidth=4)
        
        plt.savefig('radar{}.png'.format(z))
        
        for radar in glob.glob("K*"):
            os.remove(radar)
        radar_files.append(z)
  except:
    print('there is no data here for some reason', z)

for i in radar_files:
        img = cv2.imread('radar{}.png'.format(i)) # Read in the image and convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = 255*(gray < 128).astype(np.uint8) # To invert the text to white
        coords = cv2.findNonZero(gray) # Find all non-zero points (text)
        x, y, w, h = cv2.boundingRect(coords) # Find minimum spanning bounding box
        rect = img[y:y+h, x:x+w] # Crop the image - note we do this on the original image
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        cv2.imwrite("radar_{}.png".format(i), rect) # Save the image
        
        for radar in glob.glob("radar{}.png".format(i)):
            os.remove(radar)
