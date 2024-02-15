#!/usr/bin/env python
from __future__ import print_function
import glob
import os
import sys
import datetime

import gempak
import numpy as np
import pandas as pd

# Run for a given year
year = int(sys.argv[1])
month = int(sys.argv[2])
day = int(sys.argv[3])

# set directory 
#directory_path = "/vagrant/scripts/ghwt_2023/"
directory_path = "/work/gif4/severin/2023_Gallus_SevereWind/temp/02_gempak/GOOD2GO"

# run from a temp dir to keep GEMPAK .nts files happy
tmpdir = "run%s%02i%02i" % (year, month, day)
if not os.path.isdir(tmpdir):
    os.mkdir(tmpdir)
os.chdir(tmpdir)

# Load up GEMPAK parameters

paramsFile = "gempakparameters.csv"
#params = os.path.join(directory_path, paramsFile)
params = pd.read_csv(os.path.join(directory_path, paramsFile))

# Change from original to just pull the csv with specific day's SR
# Fix to either add event_id or change event_id


#df = pd.read_csv('/work/gif4/severin/2023_Gallus_SevereWind/temp/02_gempak/GOOD2GO/%s_%02i_%02i_SR_timefix.csv' % (year, month, day ), index_col='event_id')
df = pd.read_csv(f'{directory_path}/{year}_{month:02d}_{day:02d}_SR_timefix.csv', index_col='event_id')

#df = pd.read_csv('hwt_2023/%s_%02i_%02i_SR_timefix.csv' % (year, month, day ), index_col='event_id')
for name in params['NAME']:
    for i in range(1, 26):
        df["%s_%s" % (name, i)] = np.nan

#gl = gempak.app('gdlist')
#gl = gempak.app('/home/gempak/GEMPAK7/gempak/source/programs/gd/gdlist')
gl = gempak.app('gdlist')
# For each storm report
for event_id, srrow in df.iterrows():
    #if eventid != 236713:
    #    continue
    valid = datetime.datetime.strptime(srrow["Time"], "%Y-%m-%d  %H:%M") #%m-%d-%Y  %H:%M
#    oafile = valid.strftime("/work/gif4/severin/2023_Gallus_SevereWind/temp/02_gempak/GOOD2GO/mesoanalysis/sfcoaruc_%y%m%d%H")
    oafile = valid.strftime(f"{directory_path}/mesoanalysis/sfcoaruc_%y%m%d%H")

    if not os.path.isfile(oafile):
        print("Uh oh, missing %s, skipping" % (oafile, ))
        continue

    for _, paramrow in params.iterrows():
        unique_filename = "%s_%s_%s.dat" % (event_id, valid.strftime("%Y%m%d%H%M"), paramrow['NAME'])
        config = {
        	'GDFILE': '/vagrant/scripts/hwt_2023/mesoanalysis/%s' % (oafile.split("/")[-1],),
        	'GDATTIM': 'LAST',
        	'GFUNC': paramrow['NAME'],
        	'GAREA': '#%.2f;%.2f;0.7;0.7' % (srrow['LAT'], srrow['LON']),
        	'GLEVEL': paramrow['GLEVL1'],
        	'GVCORD': paramrow['GVCORD'],
        	'PROJ': 'MER',
        	'SCALE': 999,
                'OUTPUT': 'f /%s' % (unique_filename,),
   #     	'OUTPUT': 'f /vagrant/02_gempak/run230609/%s' % (unique_filename,),
        }
        for key, value in config.items():
            print('Setting {} to {}'.format(key, value))
            gl.set(key, value)
        #print("Current directory: ", os.getcwd())
        #print("Unique filename: ", unique_filename)
        #open(os.path.join(os.getcwd(), 'testfile.txt'), 'w').close()
        #gl.run()
        try:
            gl.run()
        except Exception as e:
            print("Failed to run gl.run(). Error: {}".format(str(e)))

        if not os.path.isfile(unique_filename):
            print("uh oh, failed to generate %s" % (unique_filename,))
            continue
        data_values = []
        for line in open(unique_filename):
            if line.find('Scale factor') > -1:
                tokens = line.strip().split(":")[1].split("**")
                scale_factor = float(tokens[0]) ** float(tokens[1])
            if not line.strip().startswith('ROW '):
                continue
            if len(line) < 12:
                break
            data_values.append([])
            for pos in range(8, len(line)+1, 9):
                # TODO is dividing by scale_factor right
                text = line[pos:pos+9].strip()
                if text == '':
                    continue
                data_values[-1].append(float(text) / scale_factor)
        if len(data_values) <= 1:
            print("uh oh, %s had no data, data_values %s" % (unique_filename, data_values))
            continue
        data_values = np.array(data_values)
        dims = data_values.shape
        if len(dims) == 1:
            print("uh oh, %s data_values is screwy %s" % (unique_filename, data_values))
            continue
        if dims[0] == 6:
            data_values = data_values[:5, :]
        elif dims[0] == 7:
            data_values = data_values[1:6, :]
        if dims[1] == 6:
            data_values = data_values[:, :5]
        elif dims[1] == 7:
            data_values = data_values[:, 1:6]
        newdims = data_values.shape
        if newdims != (5, 5):
            print("ERROR, we found a data_values of shape %s, old %s" % (newdims, dims))
            continue
        for i, val in enumerate(np.ravel(data_values)):
            df.at[event_id, "%s_%s" % (paramrow['NAME'], i + 1)] = val
#        os.unlink(unique_filename)

df.to_csv('%s_%02i_%02i_results.csv' % (year, month, day))
