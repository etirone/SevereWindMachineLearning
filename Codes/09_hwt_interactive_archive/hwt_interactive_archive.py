#Import Statements
import matplotlib.pyplot as plt
import numpy as np
from metpy.plots.mapping import CFProjection
import xarray as xr
#from skimage.morphology import binary_dilation
import pandas as pd
import json
import plotly.graph_objects as go

import geopandas as gpd
from shapely.geometry import LineString, MultiLineString
import plotly.graph_objs as go
import plotly.express as px
import plotly

from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import textwrap
from textwrap import wrap

import geopandas
import datetime
from datetime import date, timedelta, datetime
import requests, zipfile, io

import os
import glob

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


# Setting Days
#day_yesterday = pd.to_datetime(date.today() - timedelta(days=1))
#day_today = pd.to_datetime(date.today() - timedelta(days=5))

####Read in files
#sr_file = pd.read_csv('2020_08_22_text_file.csv')
sr_file = pd.read_csv('{t:%Y}_{t:%m}_{t:%d}_probs_labeled.csv'.format(t=day_yesterday))
print(len(sr_file))

sr_df = geopandas.GeoDataFrame(sr_file)


sr_df['GBM'] = sr_df['GBM'].round(2)
sr_df['GLM'] = sr_df['GLM'].round(2)

##Read in subsevere file
asos_file = pd.read_csv('{t:%Y}_{t:%m}_{t:%d}_sub_severe_reports.csv'.format(t=day_yesterday))


####Download shapefiles from spc
url = 'https://www.spc.noaa.gov/products/outlook/archive/{t:%Y}/day1otlk_{t:%Y}{t:%m}{t:%d}_1630-shp.zip'.format(t=day_yesterday)
r = requests.get(url)
z = zipfile.ZipFile(io.BytesIO(r.content))
z.extractall()

wind = geopandas.read_file('day1otlk_{t:%Y}{t:%m}{t:%d}_1630_wind.shp'.format(t=day_yesterday))
df = pd.DataFrame(wind)

sr_df['remarks_new_line'] = np.zeros

#today = date.today()
today_day = date.today().weekday()


#Format remarks to fit on lines better
def wrap(string, max_width):
    return '<br>'.join(textwrap.wrap(string,max_width))

for x in range(len(sr_df)):
  sr_df['remarks_new_line'][x] = (wrap(str(sr_df['Remarks'][x]), 40))

sr_df.head(1)

##To get hover text
#GBM version 1
m1_text = []
for txt in range(len(sr_df.index)):
  allstring = "event_id: {v1}, <br>Time: {v9},  <br><b>GBM: {v2}%</b>, <br>GLM: {v5}%, <br>remarks: {v8}, <br>magnitude: {v10} ".format(
                          v1= str(sr_df['event_id'][txt]),
                          v9 = str(sr_df['Time'][txt]),
                          v2= str(sr_df['GBM'][txt]), 
                          v5= str(sr_df['GLM'][txt]),
                          v8= str(sr_df['remarks_new_line'][txt]),
                          v10 = str(sr_df['magnitude'][txt]))
  m1_text.append(allstring)


#GLM version 1
m2_text = []
for txt in range(len(sr_df.index)):
  allstring = "event_id: {v1}, <br>Time: {v9}, <br>GBM: {v2}%, <br><b>GLM: {v5}%</b>, <br>remarks: {v8}, <br>magnitude: {v10}".format(
                          v1= str(sr_df['event_id'][txt]),
                          v9 = str(sr_df['Time'][txt]),
                          v2= str(sr_df['GBM'][txt]),
                          v5= str(sr_df['GLM'][txt]), 
                          v8= str(sr_df['remarks_new_line'][txt]),
                          v10 = str(sr_df['magnitude'][txt]))
  m2_text.append(allstring)





#splits up spc outlook
grouped = wind.groupby(['DN'])
DN = wind['DN'].values

if 60 in DN:
  spc_5 = grouped.get_group(5)
  spc_15 = grouped.get_group(15)
  spc_30 = grouped.get_group(30)
  spc_45 = grouped.get_group(45)
  spc_60 = grouped.get_group(60)
if 45 in DN and 60 not in DN:
  spc_5 = grouped.get_group(5)
  spc_15 = grouped.get_group(15)
  spc_30 = grouped.get_group(30)
  spc_45 = grouped.get_group(45)
if 30 in DN and 45 not in DN:
  spc_5 = grouped.get_group(5)
  spc_15 = grouped.get_group(15)
  spc_30 = grouped.get_group(30)
if 15 in DN and 30 not in DN:
  spc_5 = grouped.get_group(5)
  spc_15 = grouped.get_group(15)
if 5 in DN and 15 not in DN:
  spc_5 = grouped.get_group(5)

#converts each outlook into a json file

###
if 5 in DN:
  spc_5.to_file("path_to_GeoJSON _file", driver = "GeoJSON")
  with open("path_to_GeoJSON _file") as geofile:
    j_5 = json.load(geofile)

  i=1
  for feature in j_5["features"]:
          feature ['id'] = str(i).zfill(2)
          i += 1
###
if 15 in DN:
  spc_15.to_file("path_to_GeoJSON _file", driver = "GeoJSON")
  with open("path_to_GeoJSON _file") as geofile:
    j_15 = json.load(geofile)

  i=1
  for feature in j_15["features"]:
          feature ['id'] = str(i).zfill(2)
          i += 1
###
if 30 in DN:
  spc_30.to_file("path_to_GeoJSON _file", driver = "GeoJSON")
  with open("path_to_GeoJSON _file") as geofile:
    j_30 = json.load(geofile)

  i=1
  for feature in j_30["features"]:
          feature ['id'] = str(i).zfill(2)
          i += 1
###
if 45 in DN:
  spc_45.to_file("path_to_GeoJSON _file", driver = "GeoJSON")
  with open("path_to_GeoJSON _file") as geofile:
    j_45 = json.load(geofile)

  i=1
  for feature in j_45["features"]:
          feature ['id'] = str(i).zfill(2)
          i += 1

###
if 60 in DN:
  spc_60.to_file("path_to_GeoJSON _file", driver = "GeoJSON")
  with open("path_to_GeoJSON _file") as geofile:
    j_60 = json.load(geofile)

  i=1
  for feature in j_60["features"]:
          feature ['id'] = str(i).zfill(2)
          i += 1


#https://towardsdatascience.com/discrete-colour-scale-in-plotly-python-26f2d6e21c77
def generateDiscreteColourScale(colour_set):
    #colour set is a list of lists
    colour_output = []
    num_colours = len(colour_set)
    divisions = 1./num_colours
    c_index = 0.
    # Loop over the colour set
    for cset in colour_set:
        num_subs = len(cset)
        sub_divisions = divisions/num_subs
        # Loop over the sub colours in this set
        for subcset in cset:
            colour_output.append((c_index,subcset))
            colour_output.append((c_index + sub_divisions-
                .001,subcset))
            c_index = c_index + sub_divisions
    colour_output[-1]=(1,colour_output[-1][1])
    return colour_output

#https://colorbrewer2.org/#type=diverging&scheme=BrBG&n=10
color_schemes_2 = [['rgb(165,0,38)', 'rgb(215,48,39)'],
                 ['rgb(244,109,67)', 'rgb(253,174,97)'],
                 ['rgb(254,224,139)', 'rgb(217,239,139)'],
                 ['rgb(166,217,106)', 'rgb(102,189,99)'],
                 ['rgb(26,152,80)', 'rgb(0,104,55)']]

color_schemes = [['rgb(0,0,139)', 'rgb(49,54,149)'],
                 [ 'rgb(69,117,180)', 'rgb(116,173,209)'],
                 ['rgb(171,217,233)','rgb(254,224,144)'], #first in this row was 'rgb(224,243,248)',
                 ['rgb(253,174,97)', 'rgb(244,109,67)'],
                 ['rgb(215,48,39)', 'rgb(165,0,38)' ]]

colorscale = generateDiscreteColourScale(color_schemes)
colorscale_2 = generateDiscreteColourScale(color_schemes_2)


print(sr_file['magnitude'][0])
#Separate between measured and estimated for buttons
sr_type = []
for x in range(len(sr_file)):
  if sr_file['magnitude'][x] == 'UNK':
    sr_type.append('EG')
    print('eg test')
  else:
    sr_type.append('MG')

sr_file['type'] = sr_type

sr_groups = sr_file.groupby(['type'])
MG = sr_groups.get_group('MG')
EG = sr_groups.get_group('EG')

#measured text
m1_mg = []
for txt in MG.index:
  allstring = "event_id: {v1}, <br>Time: {v9}, <br><b>GBM: {v2}%</b>, <br>GLM: {v5}%, <br>remarks: {v8},<br>magnitude: {v10}".format(
                          v1= str(MG['event_id'][txt]), 
                          v9= str(MG['Time'][txt]),
                          v2= str(MG['GBM'][txt]), 
                          v5= str(MG['GLM'][txt]),  
                          v8= str(MG['remarks_new_line'][txt]),
			  v10=str(MG['magnitude'][txt]))
  m1_mg.append(allstring)


m2_mg = []
for txt in MG.index:
  allstring = "event_id: {v1}, <br>Time: {v9}, <br>GBM: {v2}%, <br><b>GLM: {v5}%</b>, <br>remarks: {v8},<br>magnitude: {v10}".format(
                          v1= str(MG['event_id'][txt]),
                          v9= str(MG['Time'][txt]),
                          v2= str(MG['GBM'][txt]), 
                          v5= str(MG['GLM'][txt]),
                          v8= str(MG['remarks_new_line'][txt]),
                          v10=str(MG['magnitude'][txt]))
  m2_mg.append(allstring)



#estimated text###################################################################
m1_eg = []
for txt in EG.index:
  allstring = "event_id: {v1}, <br>Time: {v9}, <br><b>GBM: {v2}%</b>, <br>GLM: {v5}%, <br>remarks: {v8},<br>magnitude: {v10}".format(
                          v1= str(EG['event_id'][txt]),
                          v9= str(EG['Time'][txt]),
                          v2= str(EG['GBM'][txt]), 
                          v5= str(EG['GLM'][txt]),
                          v8= str(EG['remarks_new_line'][txt]),
                          v10=str(EG['magnitude'][txt]))
  m1_eg.append(allstring)

m2_eg = []
for txt in EG.index:
  allstring = "event_id: {v1}, <br>Time: {v9}, <br>GBM: {v2}%, <br><b>GLM: {v5}%</b>, <br>remarks: {v8},<br>magnitude: {v10}".format(
                          v1= str(EG['event_id'][txt]),
                          v9= str(EG['Time'][txt]),
                          v2= str(EG['GBM'][txt]),
                          v5= str(EG['GLM'][txt]),
                          v8= str(EG['remarks_new_line'][txt]),
                          v10=str(EG['magnitude'][txt]))
  m2_eg.append(allstring)




##To get hover text subsevere reports
sub_text = []
for txt in range(len(asos_file.index)):
  allstring = "station_id: {v1}, <br>Time: {v2}, <br><b>Max max_gust: {v3} kts</b>".format(
                          v1= str(asos_file['station_id'][txt]),
                          v2= str(asos_file['timestamp'][txt]), 
                          v3= str(asos_file['max_gust'][txt]))
  sub_text.append(allstring)



#Make buttons for estimated and measured
mapbox_access_token = 'pk.eyJ1IjoiZXRpcm9uZSIsImEiOiJja2s2Mm1ucWgwMGI4MnRwb25lZHN6MHowIn0.Zfgu5YBuGcoB3t93kZweHQ'

values_m1 = sr_df['GBM']
values_m2 = sr_df['GLM']

m1_MG = MG['GBM']
m2_MG = MG['GLM']

m1_EG = EG['GBM']
m2_EG = EG['GLM']


#### Save Data ####
data = [
        ## Sub-severe reports
        go.Scattermapbox(customdata=asos_file['max_gust'], lon=asos_file['lon'], lat=asos_file['lat'],
                     hovertext=sub_text, showlegend=True, text='ASOS/AWOS Reports', name='ASOS/AWOS Reports',
                     marker=dict(symbol='star')
                     ),

    # All SRs
    go.Scattermapbox(customdata=sr_df['GBM'], lon=sr_df['LON'], lat=sr_df['LAT'],
                     hovertext=m1_text, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=values_m1, 
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),       
    go.Scattermapbox(customdata=sr_df['GLM'], lon=sr_df['LON'], lat=sr_df['LAT'],
                     hovertext=m2_text, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=values_m2,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
        
    
  # Measured Data Models 1 & 2
   go.Scattermapbox(customdata=MG['GBM'], lon=MG['LON'], lat=MG['LAT'],
                     hovertext=m1_mg, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=m1_MG,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
    go.Scattermapbox(customdata=MG['GLM'], lon=MG['LON'], lat=MG['LAT'],
                     hovertext=m2_mg, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=m2_MG,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
        
    #Estimated Data Models 1 & 2 
    go.Scattermapbox(customdata=EG['GBM'], lon=EG['LON'], lat=EG['LAT'],
                     hovertext=m1_eg, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=m1_EG,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
    go.Scattermapbox(customdata=EG['GLM'], lon=EG['LON'], lat=EG['LAT'],
                     hovertext=m2_eg, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=m2_EG,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers")
    
    ]

layout = go.Layout(
    height=700,
    width=1200,
    autosize=True,
    hovermode='closest',
    mapbox=dict(
        layers=[
        ],
        accesstoken='pk.eyJ1IjoiZXRpcm9uZSIsImEiOiJja2s2Mm1ucWgwMGI4MnRwb25lZHN6MHowIn0.Zfgu5YBuGcoB3t93kZweHQ',
        bearing=0,
        center=dict(
            lat=53,
             lon=0
        ),
        pitch=0,
        zoom=3.4,
        style='light'
     ),
     showlegend = False
)

updatemenus=list([
      dict(
          buttons=list([
                  dict(
                  args=['mapbox.style', 'light', {"visible": [True, True, False,  False, False, False, False]}],
                  label='Light',
                  method='relayout'
              ),
              dict(
                  args=['mapbox.style', 'satellite-streets', {"visible": [ True, True, False,  False, False, False, False]}],
                  label='Satellite with Streets',
                  method='relayout'
              )                
          ]),
          direction = 'up',
          x = 0.8,
          xanchor = 'left',
          y = 0.01,
          yanchor = 'bottom',
          # specify font size and colors
          bgcolor = 'white',
          bordercolor = '#FFFFFF',
          font = dict(size=11)
      ),   
      # drop-down 2: All Storm Reports
      dict(
          buttons=list([
                  dict(
                    label = "GBM",
                    method = "update", 
                    args = [{"visible": [True, True, False, False, False, False, False]},{"title": "GBM (All SR)"}]
                ),
                dict(
                    label = "GLM",
                    method = "update", 
                    args = [{"visible": [True, False, True, False, False, False, False]},{"title": "GLM (All SR)"}]
                ),
              ]),
              direction="down",
              pad={"r": 10, "t": 10},
              showactive=True,
              x=0.27,
              xanchor="left",
              y=1.01,
              yanchor="bottom"
          ),
          # drop-down 3: Only Measured Reports
      dict(
          buttons=list([
                  dict(
                    label = "GBM",
                    method = "update", 
                    args = [{"visible": [True, False, False, True, False, False, False]},{"title": "GBM (measured)"}]
                ),
                dict(
                    label = "GLM",
                    method = "update", 
                    args = [{"visible": [True, False, False, False, True, False, False]},{"title": "GLM (measured)"}]
                ),
              ]),
              direction="down",
              pad={"r": 10, "t": 10},
              showactive=True,
              x=0.47,
              xanchor="left",
              y=1.01,
              yanchor="bottom"
          ),
      # drop-down 4: Only Estimated Reports
      dict(
          buttons=list([
                  dict(
                    label = "GBM",
                    method = "update", 
                    args = [{"visible": [True, False, False, False, False, True, False]},{"title": "GBM (estimated)"}]
                ),
                dict(
                    label = "GLM",
                    method = "update", 
                    args = [{"visible": [True, False, False, False, False, False, True]},{"title": "GLM (estimated)"}]
                ),
              ]),
              direction="down",
              pad={"r": 10, "t": 10},
              showactive=True,
              x=0.68,
              xanchor="left",
              y=1.01,
              yanchor="bottom"
          )
      ])



layout['updatemenus'] = updatemenus
fig = go.Figure(data=data, layout=layout)
fig.update_mapboxes(center_lat=37.9)
fig.update_mapboxes(center_lon=-95.77)

fig.update_layout(showlegend=True)
fig.update_layout(legend=dict(
    yanchor="bottom",
    y=0,
    xanchor="right",
    x=0.5,
    orientation="h"
))

fig.update_layout(
    annotations=[
        dict(text="All Storm Reports:", x=0.29, xref="paper", y=1.14, yref="paper",
                             align="left", showarrow=False, font_size=13),
        dict(text="<b>Machine Learning Model:</b>", x=-.02, xref="paper", y=1.2, yref="paper",
                             align="left", showarrow=False, font_size=13),
        dict(text="Measured Storm Reports:", x=0.55, xref="paper", y=1.14, yref="paper",
                             align="left", showarrow=False, font_size=13),
        dict(text="Estimated Storm Reports:", x=0.855, xref="paper", y=1.14, yref="paper",
                             align="left", showarrow=False, font_size=13),
        dict(text="Toggle ASOS/AWOS Reports:", x=.413, y=.05, xref='paper', yref='paper', align='left', #.34
                            showarrow=False,bgcolor="white", font=dict(family='Times New Roman', size=15)),
                 ])

#plotly.offline.plot(fig, filename = 'interactive_no_outlook.html', auto_open=False, image_width=400, image_height=400, include_plotlyjs='cdn')
#plotly.offline.plot(fig, filename = '{t:%Y}_{t:%m}_{t:%d}_interactive_no_outlook.html'.format(t=day_yesterday), auto_open=False, image_width=400, image_height=400, include_plotlyjs='cdn')


wind.to_file("path_to_GeoJSON _file", driver = "GeoJSON")
with open("path_to_GeoJSON _file") as geofile:
  outlook = json.load(geofile)

i=1
for feature in outlook["features"]:
          feature ['id'] = str(i).zfill(2)
          i += 1

if 5 in DN:
  pts=[]#list of points defining boundaries of polygons
  for  feature in j_5['features']:
      if feature['geometry']['type']=='Polygon':
          pts.extend(feature['geometry']['coordinates'][0])    
          pts.append([None, None])#mark the end of a polygon   

      elif feature['geometry']['type']=='MultiPolygon':
          for polyg in feature['geometry']['coordinates']:
              pts.extend(polyg[0])
              pts.append([None, None])#end of polygon
      else: raise ValueError("geometry type irrelevant for map") 
  lons_5, lats_5=zip(*pts)

if 15 in DN:
  pts=[]#list of points defining boundaries of polygons
  for  feature in j_15['features']:
      if feature['geometry']['type']=='Polygon':
          pts.extend(feature['geometry']['coordinates'][0])    
          pts.append([None, None])#mark the end of a polygon   

      elif feature['geometry']['type']=='MultiPolygon':
          for polyg in feature['geometry']['coordinates']:
              pts.extend(polyg[0])
              pts.append([None, None])#end of polygon
      else: raise ValueError("geometry type irrelevant for map") 
  lons_15, lats_15=zip(*pts)

if 30 in DN:
  pts=[]#list of points defining boundaries of polygons
  for  feature in j_30['features']:
      if feature['geometry']['type']=='Polygon':
          pts.extend(feature['geometry']['coordinates'][0])    
          pts.append([None, None])#mark the end of a polygon   

      elif feature['geometry']['type']=='MultiPolygon':
          for polyg in feature['geometry']['coordinates']:
              pts.extend(polyg[0])
              pts.append([None, None])#end of polygon
      else: raise ValueError("geometry type irrelevant for map") 
  lons_30, lats_30=zip(*pts)

if 45 in DN:
  pts=[]#list of points defining boundaries of polygons
  for  feature in j_45['features']:
      if feature['geometry']['type']=='Polygon':
          pts.extend(feature['geometry']['coordinates'][0])    
          pts.append([None, None])#mark the end of a polygon   

      elif feature['geometry']['type']=='MultiPolygon':
          for polyg in feature['geometry']['coordinates']:
              pts.extend(polyg[0])
              pts.append([None, None])#end of polygon
      else: raise ValueError("geometry type irrelevant for map") 
  lons_45, lats_45=zip(*pts)

if 60 in DN:
  pts=[]#list of points defining boundaries of polygons
  for  feature in j_60['features']:
      if feature['geometry']['type']=='Polygon':
          pts.extend(feature['geometry']['coordinates'][0])    
          pts.append([None, None])#mark the end of a polygon   

      elif feature['geometry']['type']=='MultiPolygon':
          for polyg in feature['geometry']['coordinates']:
              pts.extend(polyg[0])
              pts.append([None, None])#end of polygon
      else: raise ValueError("geometry type irrelevant for map") 
  lons_60, lats_60=zip(*pts)

pts=[]#list of points defining boundaries of polygons
for  feature in outlook['features']:
    if feature['geometry']['type']=='Polygon':
        pts.extend(feature['geometry']['coordinates'][0])    
        pts.append([None, None])#mark the end of a polygon   

    elif feature['geometry']['type']=='MultiPolygon':
        for polyg in feature['geometry']['coordinates']:
            pts.extend(polyg[0])
            pts.append([None, None])#end of polygon
    else: raise ValueError("geometry type irrelevant for map") 
lons_out, lats_out=zip(*pts)



values_m1 = sr_df['GBM']
values_m2 = sr_df['GLM']
m1_MG = MG['GBM'] 
m2_MG = MG['GLM'] 
m1_EG = EG['GBM'] 
m2_EG = EG['GLM']

if 5 not in DN:
  data = [
    ## Sub-severe reports
    go.Scattermapbox(customdata=asos_file['max_gust'], lon=asos_file['lon'], lat=asos_file['lat'],
                     hovertext=sub_text, showlegend=True, text='ASOS/AWOS Reports', name='ASOS/AWOS Reports',
                     marker=dict(symbol='star')
                     ),
    ## All SRs
    go.Scattermapbox(customdata=sr_df['GBM'], lon=sr_df['LON'], lat=sr_df['LAT'],
                     hovertext=m1_text, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=values_m1,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
    go.Scattermapbox(customdata=sr_df['GLM'], lon=sr_df['LON'], lat=sr_df['LAT'],
                     hovertext=m2_text, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=values_m2,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
    
  # Measured Data Models 1 & 2 
   go.Scattermapbox(customdata=MG['GBM'], lon=MG['LON'], lat=MG['LAT'],
                     hovertext=m1_mg, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=m1_MG,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),       
    go.Scattermapbox(customdata=MG['GLM'], lon=MG['LON'], lat=MG['LAT'],
                     hovertext=m2_mg, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=m2_MG,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
        
    #Estimated Data Models 1 & 2 
    go.Scattermapbox(customdata=EG['GBM'], lon=EG['LON'], lat=EG['LAT'],
                     hovertext=m1_eg, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=m1wq_EG,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
    go.Scattermapbox(customdata=EG['GLM'], lon=EG['LON'], lat=EG['LAT'],
                     hovertext=m2_eg, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=m2_EG,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers")
        
          ]
############################## 5% ############################################
    
if 5 in DN and 15 not in DN:
  data = [
    ## Sub-severe reports
    go.Scattermapbox(customdata=asos_file['max_gust'], lon=asos_file['lon'], lat=asos_file['lat'],
                     hovertext=sub_text, showlegend=True, text='ASOS/AWOS Reports', name='ASOS/AWOS Reports',
                     marker=dict(symbol='star')
                     ),
    # outlook
    go.Scattermapbox(lon=lons_5, lat=lats_5, fill='toself', fillcolor='rgba(139, 69, 19, .2)', opacity=.3, mode='lines', line=dict(width=2, color='rgb(139, 69, 19)'),
                           name='5%', showlegend=True, text='SPC 5% Wind Probability'),
    #All SRs
    go.Scattermapbox(customdata=sr_df['GBM'], lon=sr_df['LON'], lat=sr_df['LAT'],
                     hovertext=m1_text, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=values_m1,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
    go.Scattermapbox(customdata=sr_df['GLM'], lon=sr_df['LON'], lat=sr_df['LAT'],
                     hovertext=m2_text, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=values_m2,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
    
        
   # Measured Data  
   go.Scattermapbox(customdata=MG['GBM'], lon=MG['LON'], lat=MG['LAT'],
                     hovertext=m1_mg, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=m1_MG,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
    go.Scattermapbox(customdata=MG['GLM'], lon=MG['LON'], lat=MG['LAT'],
                     hovertext=m2_mg, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=m2_MG,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
    
    #Estimated Data 
    go.Scattermapbox(customdata=EG['GBM'], lon=EG['LON'], lat=EG['LAT'],
                     hovertext=m1_eg, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=m1_EG,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
    go.Scattermapbox(customdata=EG['GLM'], lon=EG['LON'], lat=EG['LAT'],
                     hovertext=m2_eg, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=m2_EG,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers")
        ]
############################## 15% ############################################
if 15 in DN and 30 not in DN:
  data = [
    ## Sub-severe reports
    go.Scattermapbox(customdata=asos_file['max_gust'], lon=asos_file['lon'], lat=asos_file['lat'],
                     hovertext=sub_text, showlegend=True, text='ASOS/AWOS Reports', name='ASOS/AWOS Reports',
                     marker=dict(symbol='star')
                     ),
    #Outlooks   
    go.Scattermapbox(lon=lons_5, lat=lats_5, fill='toself', fillcolor='rgba(139, 69, 19, .2)', opacity=.3, mode='lines', line=dict(width=2, color='rgb(139, 69, 19)'),
                           name='5%', showlegend=True, text='SPC 5% Wind Probability'),
    go.Scattermapbox(lon=lons_15, lat=lats_15, fill='toself', fillcolor='rgba(255, 255, 0, .2)', opacity=.3, mode='lines', line=dict(width=2, color='rgb(255, 200, 0)'),
                           name='15%', showlegend=True, text='SPC 15% Wind Probability'),
    
    #All SRs
    go.Scattermapbox(customdata=sr_df['GBM'], lon=sr_df['LON'], lat=sr_df['LAT'],
                     hovertext=m1_text, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=values_m1,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),    
    go.Scattermapbox(customdata=sr_df['GLM'], lon=sr_df['LON'], lat=sr_df['LAT'],
                     hovertext=m2_text, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=values_m2,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
    
        
    # Measured Data
    go.Scattermapbox(customdata=MG['GBM'], lon=MG['LON'], lat=MG['LAT'],
                     hovertext=m1_mg, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=m1_MG,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
    go.Scattermapbox(customdata=MG['GLM'], lon=MG['LON'], lat=MG['LAT'],
                     hovertext=m2_mg, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=m2_MG,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
    
    #Estimated Data 
    go.Scattermapbox(customdata=EG['GBM'], lon=EG['LON'], lat=EG['LAT'],
                     hovertext=m1_eg, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=m1_EG,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
    go.Scattermapbox(customdata=EG['GLM'], lon=EG['LON'], lat=EG['LAT'],
                     hovertext=m2_eg, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=m2_EG,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
        ]
  
############################## 30% ############################################
if 30 in DN and 45 not in DN:
  data = [
    ## Sub-severe reports
    go.Scattermapbox(customdata=asos_file['max_gust'], lon=asos_file['lon'], lat=asos_file['lat'],
                     hovertext=sub_text, showlegend=True, text='ASOS/AWOS Reports', name='ASOS/AWOS Reports',
                     marker=dict(symbol='star')
                     ),
    #Outlooks
    go.Scattermapbox(lon=lons_5, lat=lats_5, fill='toself', fillcolor='rgba(139, 69, 19, .2)', opacity=.3, mode='lines', line=dict(width=2, color='rgb(139, 69, 19)'),
                           name='5%', showlegend=True, text='SPC 5% Wind Probability'),
    go.Scattermapbox(lon=lons_15, lat=lats_15, fill='toself', fillcolor='rgba(255, 255, 0, .2)', opacity=.3, mode='lines', line=dict(width=2, color='rgb(255, 200, 0)'),
                           name='15%', showlegend=True, text='SPC 15% Wind Probability'),
    go.Scattermapbox(lon=lons_30, lat=lats_30, fill='toself', fillcolor='rgba(255, 0, 90, .3)', opacity=.3, mode='lines', line=dict(width=2, color='rgb(255, 0, 0)'),
                           name='30%', showlegend=True, text='SPC 30% Wind Probability'),
    
    # All SRs
    go.Scattermapbox(customdata=sr_df['GBM'], lon=sr_df['LON'], lat=sr_df['LAT'],
                     hovertext=m1_text, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=values_m1,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
    go.Scattermapbox(customdata=sr_df['GLM'], lon=sr_df['LON'], lat=sr_df['LAT'],
                     hovertext=m2_text, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=values_m2,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
    
        
    # Measured Data
    go.Scattermapbox(customdata=MG['GBM'], lon=MG['LON'], lat=MG['LAT'],
                     hovertext=m1_mg, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=m1_MG,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
    go.Scattermapbox(customdata=MG['GLM'], lon=MG['LON'], lat=MG['LAT'],
                     hovertext=m2_mg, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=m2_MG,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
        
    #Estimated Data
    go.Scattermapbox(customdata=EG['GBM'], lon=EG['LON'], lat=EG['LAT'],
                     hovertext=m1_eg, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=m1_EG,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),        
    go.Scattermapbox(customdata=EG['GLM'], lon=EG['LON'], lat=EG['LAT'],
                     hovertext=m2_eg, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=m2_EG,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
        ]
  
############################## 45% ############################################
if 45 in DN and 60 not in DN:
  data = [
    ## Sub-severe reports
    go.Scattermapbox(customdata=asos_file['max_gust'], lon=asos_file['lon'], lat=asos_file['lat'],
                      hovertext=sub_text, showlegend=True, text='ASOS/AWOS Reports', name='ASOS/AWOS Reports',
                      marker=dict(symbol='star')
                      ),
    # Outlooks
    go.Scattermapbox(lon=lons_5, lat=lats_5, fill='toself', fillcolor='rgba(139, 69, 19, .2)', opacity=.3, mode='lines', line=dict(width=2, color='rgb(139, 69, 19)'),
                           name='5%', showlegend=True, text='SPC 5% Wind Probability'),
    go.Scattermapbox(lon=lons_15, lat=lats_15, fill='toself', fillcolor='rgba(255, 255, 0, .2)', opacity=.3, mode='lines', line=dict(width=2, color='rgb(255, 200, 0)'),
                           name='15%', showlegend=True, text='SPC 15% Wind Probability'),
    go.Scattermapbox(lon=lons_30, lat=lats_30, fill='toself', fillcolor='rgba(255, 0, 90, .3)', opacity=.3, mode='lines', line=dict(width=2, color='rgb(255, 0, 0)'),
                           name='30%', showlegend=True, text='SPC 30% Wind Probability'),
    go.Scattermapbox(lon=lons_45, lat=lats_45, fill='toself', fillcolor='rgba(150, 0, 255, .2)', opacity=.3, mode='lines', line=dict(width=2, color='rgb(255, 0, 255)'),
                           name='45%', showlegend=True, text='SPC 45% Wind Probability'),
  
    # All SRs
    go.Scattermapbox(customdata=sr_df['GBM'], lon=sr_df['LON'], lat=sr_df['LAT'],
                     hovertext=m1_text, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=values_m1,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
    go.Scattermapbox(customdata=sr_df['GLM'], lon=sr_df['LON'], lat=sr_df['LAT'],
                     hovertext=m2_text, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=values_m2,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
        
    # Measured Data
    go.Scattermapbox(customdata=MG['GBM'], lon=MG['LON'], lat=MG['LAT'],
                     hovertext=m1_mg, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=m1_MG,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
    go.Scattermapbox(customdata=MG['GLM'], lon=MG['LON'], lat=MG['LAT'],
                     hovertext=m2_mg, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=m2_MG,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
        
        
    #Estimated Data
    go.Scattermapbox(customdata=EG['GBM'], lon=EG['LON'], lat=EG['LAT'],
                     hovertext=m1_eg, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=m1_EG,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
    go.Scattermapbox(customdata=EG['GLM'], lon=EG['LON'], lat=EG['LAT'],
                     hovertext=m2_eg, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=m2_EG,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
        ]
############################## 60% ############################################
if 60 in DN:
  data = [
    ## Sub-severe reports
    go.Scattermapbox(customdata=asos_file['max_gust'], lon=asos_file['lon'], lat=asos_file['lat'],
                     hovertext=sub_text, showlegend=True, text='ASOS/AWOS Reports', name='ASOS/AWOS Reports',
                     marker=dict(symbol='star')
                     ),
    # Outlooks
    go.Scattermapbox(lon=lons_5, lat=lats_5, fill='toself', fillcolor='rgba(139, 69, 19, .2)', opacity=.3, mode='lines', line=dict(width=2, color='rgb(139, 69, 19)'),
                           name='5%', showlegend=True, text='SPC 5% Wind Probability'),
    go.Scattermapbox(lon=lons_15, lat=lats_15, fill='toself', fillcolor='rgba(255, 255, 0, .2)', opacity=.3, mode='lines', line=dict(width=2, color='rgb(255, 255, 0)'),
                           name='15%', showelegend=True, text='SPC 15% Wind Probability'),
    go.Scattermapbox(lon=lons_30, lat=lats_30, fill='toself', fillcolor='rgba(255, 0, 90, .3)', opacity=.3, mode='lines', line=dict(width=2, color='rgb(255, 0, 0)'),
                           name='30%', showlegend=True, text='SPC 30% Wind Probability'),
    go.Scattermapbox(lon=lons_45, lat=lats_45, fill='toself', fillcolor='rgba(150, 0, 255, .2)', opacity=.3, mode='lines', line=dict(width=2, color='rgb(255, 0, 255)'),
                           name='45%', showlegend=True, text='SPC 45% Wind Probability'),
    go.Scattermapbox(lon=lons_60, lat=lats_60, fill='toself', fillcolor='rgba(10, 0, 200, .2)', opacity=.3, mode='lines', line=dict(width=2, color='rgb(128, 0, 128)'),
                           name='5%', showlegend=True, text='SPC 60% Wind Probability'),
    # All SRs
    go.Scattermapbox(customdata=sr_df['GBM'], lon=sr_df['LON'], lat=sr_df['LAT'],
                     hovertext=m1_text, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=values_m1,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
    go.Scattermapbox(customdata=sr_df['GLM'], lon=sr_df['LON'], lat=sr_df['LAT'],
                     hovertext=m2_text, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=values_m2,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
    
        
    # Measured Data 
    go.Scattermapbox(customdata=MG['GBM'], lon=MG['LON'], lat=MG['LAT'],
                     hovertext=m1_mg, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=m1_MG,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
    go.Scattermapbox(customdata=MG['GLM'], lon=MG['LON'], lat=MG['LAT'],
                     hovertext=m2_mg, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=m2_MG,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
        
        
    #Estimated Data 
    go.Scattermapbox(customdata=EG['GBM'], lon=EG['LON'], lat=EG['LAT'],
                     hovertext=m1_eg, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=m1_EG,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
    go.Scattermapbox(customdata=EG['GLM'], lon=EG['LON'], lat=EG['LAT'],
                     hovertext=m2_eg, showlegend=False,
                     marker=dict(size=7,cmax=100,cmin=0,color=m2_EG,
                     colorbar=dict(title="Probability <br>SR > 50kts (%)<br> "),colorscale=colorscale), mode="markers"),
        ]

layout = go.Layout(
    height=700,
    width=1200,
    autosize=True,
    hovermode='closest',
    mapbox=dict(
        layers=[
        ],
        accesstoken='pk.eyJ1IjoiZXRpcm9uZSIsImEiOiJja2s2Mm1ucWgwMGI4MnRwb25lZHN6MHowIn0.Zfgu5YBuGcoB3t93kZweHQ',
        bearing=0,
        center=dict(
            lat=53,
             lon=0
        ),
        pitch=0,
        zoom=3.4,
        style='light'
     ),
     showlegend = False )


#Buttons
############################## no outlook ############################################
if 5 not in DN:
  updatemenus=list([
      dict(
          buttons=list([
                  dict(
                  args=['mapbox.style', 'light', {"visible": [True, True, False, False, False, False, False]}],
                  label='Light',
                  method='relayout'
              ),
              dict(
                  args=['mapbox.style', 'satellite-streets', {"visible": [ True, True, False, False, False, False, False]}],
                  label='Satellite with Streets',
                  method='relayout'
              )
          ]),
          direction = 'up',
          x = 0.8,
          xanchor = 'left',
          y = 0.01,
          yanchor = 'bottom',
          # specify font size and colors
          bgcolor = 'white',
          bordercolor = '#FFFFFF',
          font = dict(size=11)
      ),
      # drop-down 2: All Storm Reports
      dict(
          buttons=list([
                  dict(
                    label = "GBM",
                    method = "update",
                    args = [{"visible": [True, True, False, False, False, False, False]},{"title": "GBM (All SR)"}]
                ),
                dict(
                    label = "GLM",
                    method = "update",
                    args = [{"visible": [True, False, True, False, False, False, False]},{"title": "GLM (All SR)"}]
                ),
              ]),
              direction="down",
              pad={"r": 10, "t": 10},
              showactive=True,
              x=0.27,
              xanchor="left",
              y=1.01,
              yanchor="bottom"
          ),
          # drop-down 3: Only Measured Reports
      dict(
          buttons=list([
                  dict(
                    label = "GBM",
                    method = "update",
                    args = [{"visible": [True, False, False, True, False, False, False]},{"title": "GBM (measured)"}]
                ),
                dict(
                    label = "GLM",
                    method = "update",
                    args = [{"visible": [True, False, False, False, True, False, False]},{"title": "GLM (measured)"}]
                ),
              ]),
              direction="down",
              pad={"r": 10, "t": 10},
              showactive=True,
              x=0.47,
              xanchor="left",
              y=1.01,
              yanchor="bottom"
          ),
      # drop-down 4: Only Estimated Reports
      dict(
          buttons=list([
                  dict(
                    label = "GBM",
                    method = "update",
                    args = [{"visible": [True, False, False, False, False, True, False]},{"title": "GBM (estimated)"}]
                ),
                dict(
                    label = "GLM",
                    method = "update",
                    args = [{"visible": [True, False, False, False, False, False, True]},{"title": "GLM (estimated)"}]
                ),
              ]),
              direction="down",
              pad={"r": 10, "t": 10},
              showactive=True,
              x=0.68,
              xanchor="left",
              y=1.01,
              yanchor="bottom"
          )
      ])
############################## 5% ############################################
if 5 in DN and 15 not in DN:
  updatemenus=list([
      dict(
          buttons=list([
                  dict(
                  args=['mapbox.style', 'light', {"visible": [True, True, True, False, False, False, False, False]}],
                  label='Light',
                  method='relayout'
              ),
              dict(
                  args=['mapbox.style', 'satellite-streets', {"visible": [True, True, True, False, False, False, False, False]}],
                  label='Satellite with Streets',
                  method='relayout'
              )
          ]),
          direction = 'up',
          x = 0.8,
          xanchor = 'left',
          y = 0.01,
          yanchor = 'bottom',
          # specify font size and colors
          bgcolor = 'white',
          bordercolor = '#FFFFFF',
          font = dict(size=11)
      ),
      # drop-down 2: All Storm Reports
      dict(
          buttons=list([
                  dict(
                    label = "GBM",
                    method = "update",
                    args = [{"visible": [True, True, True, False, False, False, False, False]},{"title": "GBM (All SR)"}]
                ),
                dict(
                    label = "GLM",
                    method = "update",
                    args = [{"visible": [True, True, False, True, False, False, False, False]},{"title": "GLM (All SR)"}]
                ),
              ]),
              direction="down",
              pad={"r": 10, "t": 10},
              showactive=True,
              x=0.27,
              xanchor="left",
              y=1.01,
              yanchor="bottom"
          ),
          # drop-down 3: Only Measured Reports
      dict(
          buttons=list([
                  dict(
                    label = "GBM",
                    method = "update",
                    args = [{"visible": [True, True, False, False, True, False, False, False]},{"title": "GBM (measured)"}]
                ),
                dict(
                    label = "GLM",
                    method = "update",
                    args = [{"visible": [True, True, False, False, False, True, False, False]},{"title": "GLM (measured)"}]
                ),
              ]),
              direction="down",
              pad={"r": 10, "t": 10},
              showactive=True,
              x=0.47,
              xanchor="left",
              y=1.01,
              yanchor="bottom"
          ),
      # drop-down 4: Only Estimated Reports
      dict(
          buttons=list([
                  dict(
                    label = "GBM",
                    method = "update",
                    args = [{"visible": [True, True, False, False, False, False, True, False]},{"title": "GBM (estimated)"}]
                ),
                dict(
                    label = "GLM",
                    method = "update",
                    args = [{"visible": [True, True, False, False, False, False, False, True]},{"title": "GLM (estimated)"}]
                ),
              ]),
              direction="down",
              pad={"r": 10, "t": 10},
              showactive=True,
              x=0.68,
              xanchor="left",
              y=1.01,
              yanchor="bottom"
          )
      ])
  
############################## 15% ############################################
if 15 in DN and 30 not in DN:
  updatemenus=list([
      dict(
          buttons=list([
                  dict(
                  args=['mapbox.style', 'light', {"visible": [True, True, True, True, False, False, False, False, False]}],
                  label='Light',
                  method='relayout'
              ),
              dict(
                  args=['mapbox.style', 'satellite-streets', {"visible": [True, True, True, True, False, False, False, False, False]}],
                  label='Satellite with Streets',
                  method='relayout'
              )
          ]),
          direction = 'up',
          x = 0.8,
          xanchor = 'left',
          y = 0.01,
          yanchor = 'bottom',
          # specify font size and colors
          bgcolor = 'white',
          bordercolor = '#FFFFFF',
          font = dict(size=11)
      ),
      # drop-down 2: All Storm Reports
      dict(
          buttons=list([
                  dict(
                    label = "GBM",
                    method = "update",
                    args = [{"visible": [True, True, True, True, False, False, False, False, False]},{"title": "GBM (All SR)"}]
                ),
                dict(
                    label = "GLM",
                    method = "update",
                    args = [{"visible": [True, True, True, False, True, False, False, False, False]},{"title": "GLM (All SR)"}]
                ),
              ]),
              direction="down",
              pad={"r": 10, "t": 10},
              showactive=True,
              x=0.27,
              xanchor="left",
              y=1.01,
              yanchor="bottom"
          ),
          # drop-down 3: Only Measured Reports
      dict(
          buttons=list([
                  dict(
                    label = "GBM",
                    method = "update",
                    args = [{"visible": [True, True, True, False, False, True, False, False, False]},{"title": "GBM (measured)"}]
                ),
                dict(
                    label = "GLM",
                    method = "update",
                    args = [{"visible": [True, True, True, False, False, False, True, False, False]},{"title": "GLM (measured)"}]
                ),
              ]),
              direction="down",
              pad={"r": 10, "t": 10},
              showactive=True,
              x=0.47,
              xanchor="left",
              y=1.01,
              yanchor="bottom"
          ),
      # drop-down 4: Only Estimated Reports
      dict(
          buttons=list([
                  dict(
                    label = "GBM",
                    method = "update",
                    args = [{"visible": [True, True, True, False, False, False, False, True, False]},{"title": "GBM (estimated)"}]
                ),
                dict(
                    label = "GLM",
                    method = "update",
                    args = [{"visible": [True, True, True, False, False, False, False, False, True]},{"title": "GLM (estimated)"}]
                ),
              ]),
              direction="down",
              pad={"r": 10, "t": 10},
              showactive=True,
              x=0.68,
              xanchor="left",
              y=1.01,
              yanchor="bottom"
          )
      ])
  
############################## 30% ############################################
if 30 in DN and 45 not in DN:
  updatemenus=list([
      dict(
          buttons=list([
                  dict(
                  args=['mapbox.style', 'light', {"visible": [True, True, True, True, True, False, False, False, False, False]}],
                  label='Light',
                  method='relayout'
              ),
              dict(
                  args=['mapbox.style', 'satellite-streets', {"visible": [True, True, True, True, True, False, False, False, False, False]}],
                  label='Satellite with Streets',
                  method='relayout'
              )
          ]),
          direction = 'up',
          x = 0.8,
          xanchor = 'left',
          y = 0.01,
          yanchor = 'bottom',
          # specify font size and colors
          bgcolor = 'white',
          bordercolor = '#FFFFFF',
          font = dict(size=11)
      ),
      # drop-down 2: All Storm Reports
      dict(
          buttons=list([
                  dict(
                    label = "GBM",
                    method = "update",
                    args = [{"visible": [True, True, True, True, True, False, False, False, False, False]},{"title": "GBM (All SR)"}]
                ),
                dict(
                    label = "GLM",
                    method = "update",
                    args = [{"visible": [True, True, True, True, False, True, False, False, False, False]},{"title": "GLM (All SR)"}]
                ),
              ]),
              direction="down",
              pad={"r": 10, "t": 10},
              showactive=True,
              x=0.27,
              xanchor="left",
              y=1.01,
              yanchor="bottom"
          ),
          # drop-down 3: Only Measured Reports
      dict(
          buttons=list([
                  dict(
                    label = "GBM",
                    method = "update",
                    args = [{"visible": [True, True, True, True, False, False, True, False, False, False]},{"title": "GBM (measured)"}]
                ),
                dict(
                    label = "GLM",
                    method = "update",
                    args = [{"visible": [True, True, True, True, False, False, False, True, False, False]},{"title": "GLM (measured)"}]
                ),
              ]),
              direction="down",
              pad={"r": 10, "t": 10},
              showactive=True,
              x=0.47,
              xanchor="left",
              y=1.01,
              yanchor="bottom"
          ),
      # drop-down 4: Only Estimated Reports
      dict(
          buttons=list([
                  dict(
                    label = "GBM",
                    method = "update",
                    args = [{"visible": [True, True, True, True, False, False, False, False, True, False]},{"title": "GBM (estimated)"}]
                ),
                dict(
                    label = "GLM",
                    method = "update",
                    args = [{"visible": [True, True, True, True, False, False, False, False, False, True]},{"title": "GLM (estimated)"}]
                ),
              ]),
              direction="down",
              pad={"r": 10, "t": 10},
              showactive=True,
              x=0.68,
              xanchor="left",
              y=1.01,
              yanchor="bottom"
          )
      ])
############################## 45% ############################################
if 45 in DN and 60 not in DN:
  updatemenus=list([
      dict(
          buttons=list([
                  dict(
                  args=['mapbox.style', 'light', {"visible": [True, True, True, True, True, True, False, False, False, False, False]}],
                  label='Light',
                  method='relayout'
              ),
              dict(
                  args=['mapbox.style', 'satellite-streets', {"visible": [True, True, True, True, True, True, False, False, False, False, False]}],
                  label='Satellite with Streets',
                  method='relayout'
              )
          ]),
          direction = 'up',
          x = 0.8,
          xanchor = 'left',
          y = 0.01,
          yanchor = 'bottom',
          # specify font size and colors
          bgcolor = 'white',
          bordercolor = '#FFFFFF',
          font = dict(size=11)
      ),
      # drop-down 2: All Storm Reports
      dict(
          buttons=list([
                  dict(
                    label = "GBM",
                    method = "update",
                    args = [{"visible": [True, True, True, True, True, True, False, False, False, False, False]},{"title": "GBM (All SR)"}]
                ),
                dict(
                    label = "GLM",
                    method = "update",
                    args = [{"visible": [True, True, True, True, True, False, True, False, False, False, False]},{"title": "GLM (All SR)"}]
                ),
              ]),
              direction="down",
              pad={"r": 10, "t": 10},
              showactive=True,
              x=0.27,
              xanchor="left",
              y=1.01,
              yanchor="bottom"
          ),
          # drop-down 3: Only Measured Reports
      dict(
          buttons=list([
                  dict(
                    label = "GBM",
                    method = "update",
                    args = [{"visible": [True, True, True, True, True, False, False, True, False, False, False]},{"title": "GBM (measured)"}]
                ),
                  dict(
                    label = "GLM",
                    method = "update",
                    args = [{"visible": [True, True, True, True, True, False, False, False, True, False, True]},{"title": "GLM (measured)"}]
                ),
              ]),
              direction="down",
              pad={"r": 10, "t": 10},
              showactive=True,
              x=0.47,
              xanchor="left",
              y=1.01,
              yanchor="bottom"
          ),
      # drop-down 4: Only Estimated Reports
      dict(
          buttons=list([
                  dict(
                    label = "GBM ",
                    method = "update",
                    args = [{"visible": [True, True, True, True, True, False, False, False, False, True, False]},{"title": "GBM (estimated)"}]
                ),
                  dict(
                    label = "GLM",
                    method = "update",
                    args = [{"visible": [True, True, True, True, True, False, False, False, False, False, True]},{"title": "GLM (estimated)"}]
                ),
              ]),
              direction="down",
              pad={"r": 10, "t": 10},
              showactive=True,
              x=0.68,
              xanchor="left",
              y=1.01,
              yanchor="bottom"
          )
      ])
############################## 60% ############################################
if 60 in DN:
  updatemenus=list([
      dict(
          buttons=list([
                  dict(
                  args=['mapbox.style', 'light', {"visible": [True, True, True, True, True, True, True, False, False, False, False, False]}],
                  label='Light',
                  method='relayout'
              ),
              dict(
                  args=['mapbox.style', 'satellite-streets', {"visible": [True, True, True, True, True, True, True, False, False, False, False, False]}],
            label='Satellite with Streets',
                  method='relayout'
              )
          ]),
          direction = 'up',
          x = 0.8,
          xanchor = 'left',
          y = 0.01,
          yanchor = 'bottom',
          # specify font size and colors
          bgcolor = 'white',
          bordercolor = '#FFFFFF',
          font = dict(size=11)
      ),
      # drop-down 2: All Storm Reports
      dict(
          buttons=list([
                  dict(
                    label = "GBM ",
                    method = "update",
                    args = [{"visible": [True, True, True, True, True, True, True, False, False, False, False, False]},{"title": "GBM (All SR)"}]
                ),
                  dict(
                    label = "GLM",
                    method = "update",
                    args = [{"visible": [True, True, True, True, True, True, False, True, False, False, False, False]},{"title": "GLM (All SR)"}]
                ),
              ]),
              direction="down",
              pad={"r": 10, "t": 10},
              showactive=True,
              x=0.27,
              xanchor="left",
              y=1.01,
              yanchor="bottom"
          ),
          # drop-down 3: Only Measured Reports
      dict(
          buttons=list([
                  dict(
                    label = "GBM",
                    method = "update",
                    args = [{"visible": [True, True, True, True, True, True, False, False, True, False, False, False]},{"title": "GBM (measured)"}]
                ),
                  dict(
                    label = "GLM",
                    method = "update",
                    args = [{"visible": [True, True, True, True, True, True, False, False, False, True, False, False]},{"title": "GLM (measured)"}]
                ),
              ]),
              direction="down",
              pad={"r": 10, "t": 10},
              showactive=True,
              x=0.47,
              xanchor="left",
              y=1.01,
              yanchor="bottom"
          ),
      # drop-down 4: Only Estimated Reports
      dict(
          buttons=list([
                  dict(
                    label = "GBM",
                    method = "update",
                    args = [{"visible": [True, True, True, True, True, True, False, False, False, False, True, False]},{"title": "GBM (estimated)"}]
                ),
                  dict(
                    label = "GLM",
                    method = "update",
                    args = [{"visible": [True, True, True, True, True, True, False, False, False, False, False, True]},{"title": "GLM (estimated)"}]
                ),
              ]),
              direction="down",
              pad={"r": 10, "t": 10},
              showactive=True,
              x=0.68,
              xanchor="left",
              y=1.01,
              yanchor="bottom"
          )
      ])

####### Updating buttons and legeds
layout['updatemenus'] = updatemenus 
fig = go.Figure(data=data, layout=layout) 
fig.update_mapboxes(center_lat=37.9) 
fig.update_mapboxes(center_lon=-95.77) 
fig.update_layout(
    annotations=[
        dict(text="All Storm Reports:", x=0.26, xref="paper", y=1.14, yref="paper",
                             align="left", showarrow=False, font_size=13),
        dict(text="<b>Machine Learning Model:</b>", x=-.02, xref="paper", y=1.2, yref="paper",
                             align="left", showarrow=False, font_size=14),
        dict(text="Measured Storm Reports:", x=0.54, xref="paper", y=1.14, yref="paper",
                             align="left", showarrow=False, font_size=13),
        dict(text="Estimated Storm Reports:", x=0.83, xref="paper", y=1.14, yref="paper",
                             align="left", showarrow=False, font_size=13),
        dict(text=" ASOS/AWOS Reports | 1630Z SPC Wind Probability Legend (%):", x=.08, y=.05, xref='paper', yref='paper', align='left', #.34
                            showarrow=False,bgcolor="white", font=dict(family='Times New Roman', size=15)),
                 ]) 

fig.update_layout(showlegend=True) 
fig.update_layout(legend=dict(
    yanchor="bottom",
    y=0,
    xanchor="right",
    x=0.5,
    orientation="h" ))

#plotly.offline.plot(fig, filename = 'interactive_archive.html', auto_open=False, image_width=400, image_height=400, include_plotlyjs='cdn')
plotly.offline.plot(fig, filename = '{t:%Y}_{t:%m}_{t:%d}_interactive_archive.html'.format(t=day_yesterday), auto_open=False, image_width=400, image_height=400, include_plotlyjs='cdn')


for day1otlk in glob.glob("day1otlk_*"):
      os.remove(day1otlk)



