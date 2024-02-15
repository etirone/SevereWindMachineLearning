from tqdm import tqdm

import geopandas as gpd
import pandas as pd

import numpy as np
import xarray as xr

import matplotlib.pyplot as plt
import metpy

import warnings
from datetime import date, timedelta, datetime

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


# Setting Days
# day_yesterday = pd.to_datetime(date.today() - timedelta(days=1))


# Use csv file from Jon
stations = pd.read_csv('metpy_us_stations.csv')

conus_stations = gpd.GeoDataFrame(
    stations,
    geometry=gpd.points_from_xy(stations.lon, stations.lat)
)


#Use timefix for lsrs
####################### Will have to change to fluid dates
lsrs = pd.read_csv('{t:%Y}_{t:%m}_{t:%d}_SR_timefix.csv'.format(t=specific_date))

#lsrs = lsrs.iloc[:-4 , :]
#print(lsrs)

lsrs = lsrs.drop(columns='Unnamed: 0')
lsrs['timestamp'] = pd.to_datetime(lsrs['Time'])

lsrs = gpd.GeoDataFrame(
    lsrs,
    geometry=gpd.points_from_xy(lsrs.LON, lsrs.LAT)
)

# Initial filtering: subset to all stations within a distance of a wind LSR
buffer = 0.288  # this is degrees, buffer in lat lon space
lsrs['buffer'] = lsrs.geometry.buffer(buffer)


# Pulling data from stations near SRs in time
station_gusts_near_lsrs = []
for _, row in lsrs.iterrows():
    t1 = row['timestamp'] - pd.Timedelta(10, 'min')
    t2 = (row['timestamp'] + pd.Timedelta(10, 'min')).ceil(freq='60min')
    this_stations = conus_stations[
        conus_stations.geometry.within(row['buffer'])
    ]
    if len(this_stations):
        # Only search if we have stations!
        for _, station_row in this_stations.iterrows():
            url = (
                "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?"
                f"data=gust&data=sknt&year1={t1:%Y}&month1={t1:%m}&"
                f"day1={t1:%d}&hour1={t1:%H}&minute1={t1:%M}&year2={t2:%Y}&"
                f"month2={t2:%m}&day2={t2:%d}&hour2={t2:%H}&minute2={t2:%M}&"
                "tz=Etc%2FUTC&format=onlycomma&latlon=yes&elev=yes&missing=M&"
                "trace=T&%20direct=no&report_type=1&report_type=2&"
                f"station={station_row['ID']}"
            )
            station_data = pd.read_csv(url)
            if len(station_data):
 # Only report if we have data!
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    max_gust = np.nanmax(
                        station_data['gust'].replace('M', np.nan).to_numpy(dtype='float')
                    )
                    if np.isnan(max_gust):
                        # No gust data! use max of regular wind
                        max_gust = np.nanmax(
                            station_data['sknt'].replace('M', np.nan).to_numpy(dtype='float')
                        )
                station_gusts_near_lsrs.append(
                    row.to_list() + [station_row['ID'], max_gust]
                )


#Add column to LSR with nearest measurement and gust information
station_gust_table = pd.DataFrame.from_records(
    station_gusts_near_lsrs,
    columns=list(lsrs.columns) + ['station_id', 'max_gust']
)

print('number of reports', len(station_gust_table))

conus_stations.set_index("ID")[['lon', 'lat']]

#Make file of subsevere reports that is better cleaned up with lat/lon
station_gusts_at_station = station_gust_table[['timestamp', 'station_id', 'max_gust']].join(
    other=conus_stations.set_index("ID")[['lon', 'lat']],
    on='station_id',
    how='left'
)

#station_gusts_at_station.to_csv('backup_file_if_radar_is_broken.csv')
station_gusts_at_station.to_csv('{t:%Y}_{t:%m}_{t:%d}_sub_severe_reports.csv'.format(t=specific_date))

