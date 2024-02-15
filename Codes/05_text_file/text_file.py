# Make text file of the information to display on the website
# Will make a html table in the end
# Will also make a csv file to be used in plotting script


# combine files to get remarks and probabilities in one file

import pandas as pd
import numpy as np
from datetime import date, timedelta, datetime
import datetime
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

# import files
##If you need to set the date manually
#remarks=pd.read_csv('2020_08_10_SR_timefix.csv', header=0)

remarks = pd.read_csv('{t:%Y}_{t:%m}_{t:%d}_SR_timefix.csv'.format(t=specific_date), header=0)

### temp patch: drop last four since they were dropped in testing
# add something in that drops event_ids that are not in both files
#remarks = remarks.iloc[:-4 , :]

#### Read in probabilities
probs = pd.read_csv('final_probs_subsevere_2023.csv', header=0)

probs.to_csv('{t:%Y}_{t:%m}_{t:%d}_probs_sub.csv'.format(t=specific_date))

################## SAVE CSV TO PLOT FOR ARCHIVE
df_for_pp = probs.drop(columns=['svmRadial', 'mxnetAdam', 'stack_rf', 'avg_ens', 'indicator_text'])
df_for_pp['GLM'] = 100*(1 - df_for_pp['stack_glm'])
df_for_pp['GBM'] = 100*(1 - df_for_pp['gbm'])


dfnew =  pd.merge(df_for_pp, remarks, on="event_id")
dfnew['magnitude'] = dfnew['Speed(MPH)']
dfnew = dfnew.drop(columns=['lon', 'lat', 'year', 'day', 'month', 'hr', 'min',
       'stack_glm', 'Speed(MPH)', 'Location', 'County', 'State'])

new2 = dfnew[['event_id', 'Time', 'LAT', 'LON', 'magnitude',
                'Remarks','GBM','GLM']]

new2.to_csv('{t:%Y}_{t:%m}_{t:%d}_probs_labeled.csv'.format(t=specific_date))
################



event_id = remarks['event_id']


#Set models by day of the week
today = datetime.datetime.today()
today_day = datetime.datetime.today().weekday()
print(today_day)
tomorrow_test = tomorrow.weekday()
print(tomorrow_test)

probs['Model 1'] = np.nan
probs['Model 2'] = np.nan

for x in range(len(probs)):
    if (tomorrow_test % 2) == 0:
        probs['Model 1'][x] = (probs['gbm'][x])
        probs['Model 2'][x] = (probs['stack_glm'][x])
    else:
        probs['Model 1'][x] = (probs['stack_glm'][x])
        probs['Model 2'][x] = (probs['gbm'][x])

new = pd.merge(probs, remarks, on="event_id")
new['magnitude'] = new['Speed(MPH)']

new = new.drop(columns=['lon', 'lat', 'year', 'day', 'month', 'hr', 'min',
       'stack_glm', 'Speed(MPH)', 'Location', 'County', 'State'])

new['Model 1'] = 100*(1-new['Model 1'])
new['Model 2'] = 100*(1-new['Model 2'])
new['Difference'] = abs(new['Model 1'] - new['Model 2'])


test_new = new[['event_id', 'Time', 'LAT', 'LON', 'magnitude',
                'Remarks', 'Model 1',
                'Model 2', 'Difference']]

test_new.to_csv('{t:%Y}_{t:%m}_{t:%d}_text_file.csv'.format(t=specific_date))


### Try adding a column with radar names to be added in the html table ##
test_new['Radar'] = 0
for x in range(len(test_new)):
	test_new['Radar'][x] = "https://meteor.geol.iastate.edu/~etirone/radar/radar_{}.png".format(x) # border=3 height=200 width=200> </img>').format(x)
test_new['Radar']= r'''<div class="image-box"> <img src="''' + test_new['Radar'] + '''" height=300 width=300> </img> </div>'''

#Set options for html table
pd.set_option('colheader_justify', 'center')

html = "<html><head><link href='bootstrap/css/bootstrap.min.css' rel='stylesheet'></head><body>"
html += test_new.to_html(classes=['table', 'table-striped', 'table-hover'], 
                    header=True,
                    float_format='{:10.2f}'.format,
		    render_links=True,
		    escape=False
                    )
html += '</body></html>'

#Freeze the header
html += '<style>'
html += 'table.table > thead > tr:nth-child(1) > th{background: white;position: sticky;top:0;}'
html += '</style>'

#Change hover color
html += '<style>'
html += '.table-hover tbody tr:hover td, .table-hover tbody tr:hover th {background-color: #c7eae5;}'  
html += '</style>'

#Center text in table
html += '<style>'
html += 'td {text-align: center;}'
html += '</style>'

#Zoom radar on hover
html += '<style>'
#html += 'img {transition:transform 0.25s ease;}'
#html += 'img:hover {-webkit-transform:scale(2); /* transform:scale(2);}'

html += '* {-moz-box-sizing: border-box;-webkit-box-sizing: border-box;box-sizing: border-box;margin: 0;padding: 0;}'
html += '.image-box {position: relative;margin: auto;overflow: hidden;width: 300px;}'
html += '.image-box img {max-width: 100%; transition: all 0.3s;display: block;width: 100%;height: auto;transform: scale(1);}'
html += '.image-box:hover img {transform: scale(2);}'
html += '</style>'

text_file = open("SR_table.html", "w")
text_file.write(html)
text_file.close()
