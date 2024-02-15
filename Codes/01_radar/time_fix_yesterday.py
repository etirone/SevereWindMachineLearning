#Script will download yesterday's SR and then fix the time and add an event_id
# Nov 17, 2023 Script will download the specified date's SR and then fix the time and add an event_id
# # singularity exec radar.sif python time_fix_yesterday.py 230609
# year is in the 2 digit form here because the url uses 2 digits rather than 4. 

import csv
import pandas as pd
from datetime import date, timedelta, datetime
import argparse  # Import the argparse module

# Set location of time table conversion file

timeTableConversionFile = './TimeLookup.csv'

# Create the argument parser

parser = argparse.ArgumentParser(description='Download NOAA wind reports for a specific date.')
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


# Format the URL with the provided date
url = f'https://www.spc.noaa.gov/climo/reports/{args.date_input}_rpts_raw_wind.csv'
print(url)

# added a parser to the url above to input the date
data = pd.read_csv(url)
#data = pd.read_csv('https://www.spc.noaa.gov/climo/reports/today_raw_wind.csv') #If they're late to updating "yesterday's storm reports" use this
#data = pd.read_csv('https://www.spc.noaa.gov/climo/reports/yesterday_raw_wind.csv', header=0)

#day_yesterday = pd.to_datetime(date.today() - timedelta(days=1))
#day_yesterday = pd.datetime(2023,5,25)


#today = specific_date
#today_test = specific_date.strftime('%Y-%m-%d')
#yesterday = specific_date - timedelta(days=1)
#yesterday_test = yesterday.strftime('%Y-%m-%d')

#Downloads yesterday's storm reports and names the file year_month_day_SR.csv

# Convert args.date_input to a datetime object
date_obj = datetime.strptime(args.date_input, '%y%m%d')
# Now use this date_obj to format your filename
filename = date_obj.strftime('%Y_%m_%d_SR.csv')
# Use the formatted filename in to_csv, write to file.
d = data.to_csv(filename, header=True)

print(data)

# read from file to ensure the original data has been saved.
df = pd.read_csv(filename, delimiter=',', header=1)

####Try skiprows=1 instead of header=1
# Changed the file lookup (line above) into an object I generate below 

# Generate the content programmatically instead of reading it in from file Nov 14, 2023
#original = list(range(0, 2400, 1))
#new = [f'{i // 100:02d}:{i % 100:02d}' for i in original]

# Create a DataFrame
#time_lookup = pd.DataFrame({'original': original, 'new': new})
#time_lookup_matrix = time_lookup.to_numpy()

# Jan 4, 2024 looks like my attempt above to replace this file didn't work.  The issue may in part be that I am using all the values between 0 and 2400 but minutes are out of 60 not 100
time_lookup = pd.read_csv(timeTableConversionFile, delimiter=',', header=0)
#print(time_lookup)

today = specific_date
today_test = specific_date.strftime('%Y-%m-%d')
yesterday = specific_date - timedelta(days=1)
yesterday_test = yesterday.strftime('%Y-%m-%d')
day_yesterday_test = yesterday.strftime('%Y-%m-%d')

# Jan 4, 2024 I had to add the tomorrow variable because the variables were not making senses once I started giving it specific dates.
# When you decide to reimplement running just the last day of data, you will want to make sure the loop below is still functioning properly
# in addition, you will want to check the location of the data download as that is different than older date data. 
#
tomorrow = specific_date + timedelta(days=1)
tomorrow_test = tomorrow.strftime('%Y-%m-%d')

# print('today', today)
# print('today_test', today_test)
# print(yesterday)
# print('yesterday_test', yesterday_test)


time_out = pd.DataFrame(df['Time'])
print(time_out)
count = 0


for i in df['Time']:
     x = 0
     while x < 1440:
        if i == time_lookup['original'][x]:
            print(i)
            if i <= 1159:
                #time_out['Time'][count] = today[0:11]+str(time_lookup['new'][x])
                #time_out['Time'][count] = today_test[0:11]+ ' ' +str(time_lookup['new'][x])
                time_out['Time'][count] = tomorrow_test + ' ' + str(time_lookup['new'][x])
                count =  count+1
            elif i >= 1159 and i <= 2359:
                #time_out['Time'][count] = yesterday_test[0:11]+ ' ' + str(time_lookup['new'][x])
                time_out['Time'][count] = today_test + ' ' + str(time_lookup['new'][x])
                count =  count+1
            else:
                print('this event is out of date')
        x = x+1

df['Time'] = time_out


#Get rid of reports before 1630Z yesterday (before SPC period)
df['Time'] = pd.to_datetime(df['Time'], format='%Y-%m-%d %H:%M')
#yest = '{t:%Y}-{t:%m}-{t:%d} 16:30'.format(t=day_yesterday)
#yest = '{t:%Y}-{t:%m}-{t:%d} 16:30'.format(t=day_yesterday_test)
yest_str = yesterday_test + ' 16:30'
yest = pd.to_datetime(yest_str)

index_names = df[ df['Time'] < yest ].index
df.drop(index_names, inplace = True)
#print('yest_str ',yest_str)

df['Time'] = df['Time'].dt.strftime('%Y-%m-%d %H:%M')

df.insert(0, 'event_id', range(1, 1+len(df)))

df.to_csv('{year}_{month:02d}_{day:02d}_SR_timefix.csv'.format(year=year, month=month, day=day))

print(df)

