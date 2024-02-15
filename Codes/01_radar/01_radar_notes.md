# Singularity container for radar

The first step in this pipeline involves a conda package called radar. I am going to make a separate singularity container for it because alma linux and the version of gcc required for gempak does not mix well with the required version required for the radar dependencies.  


In the definition file I used ubuntu:latest which is the following:


I had to remove libxp6

I had to add this to `vagrant@vagrant:/vagrant$ sudo vim /etc/apt/sources.list`

```
deb http://old-releases.ubuntu.com/ubuntu impish-security main restricted
```

I believe that glibc 2.34 is what I need for the radar.yml file to be loaded properly via conda. and using ubuntu:20.10 or 20.04 should work but I can't get the image to download properly.  Something to do with the source.list perhaps



* Nov 9, 2023

I created files for radar.def and radar.yml based on what worked for Yash.

Installed Docker 

```
sudo apt-get install docker.io
sudo usermod -aG docker vagrant
newgrp docker
docker login -u andrewseverin
```

## Testing the container

* Nov 13, 2023

* /home/lab/singluarity_vm3 
* /vagrant/radar

```
vagrant ssh
singularity exec --bind /vagrant radar.sif python /vagrant/scripts/time_fix_yesterday.py
```

**Error:** FileNotFoundError: [Errno 2] No such file or directory: '/work/wgallus/etirone2/spc_raw_SR_2018/HWT_test/TimeLookup.csv'

I went ahead and grabbed those files for now.

* /Users/lab/singularity-vm3/files

```
rsync -avz -e ssh severin@nova.its.iastate.edu:/work/wgallus/etirone2/spc_raw_SR_2018/HWT_test .


receiving file list ... done
HWT_test/
HWT_test/2020_03_04_SR.csv
HWT_test/2020_03_04_SR_timefix.csv
HWT_test/2020_04_12_SR.csv
HWT_test/2020_04_12_SR_timefix.csv
HWT_test/2020_04_14_SR.csv
HWT_test/2020_04_14_SR_timefix.csv
HWT_test/README.txt
HWT_test/SR_plot.py
HWT_test/SR_plot_backup.py
HWT_test/TimeLookup.csv
HWT_test/fix_SR_yesterday.py
HWT_test/fix_SR_yesterday_backup.py
HWT_test/good_scripts/
HWT_test/good_scripts/SR_plot.py
HWT_test/good_scripts/fix_SR_yesterday.py
```

I updated the hard coded link and the script appears to finish without error 

```
singularity exec --bind /vagrant radar.sif python /vagrant/scripts/time_fix_yesterday.py

```

* Nov 14, 2023

I modified the hard coded line for the time data and added a parsed argument 

```
singularity exec --bind /vagrant radar.sif python /vagrant/scripts/time_fix_yesterday.py /vagrant/files/HWT_test/TimeLookup.csv
```

This completes as expected. 

Q: Does the TimeLookup.csv ever change? if not we can hard code it into the python script. Add to issues in github.
It looks like the file is used to just convert time to include a colon and make sure it is 4 digits 1 to 00:01, 2 to 00:02, etc.  I think we can hard code this into the script.  I will add this to the issues in github. 

I just went ahead and programmatically generated the files content for 2023_06_09_SR_timefix.csv

I started by taking the hard coded line and converting it into an input argument, then I commented out the line and added the following code to generate the content.

```
#time_lookup = pd.read_csv('/vagrant/files/HWT_test/TimeLookup.csv', delimiter=',', header=0)
#time_lookup = pd.read_csv(args.css_file_path, delimiter=',', header=0)  # Use the argument here

# Generate the content programmatically instead of reading it in from file Nov 14, 2023
original = list(range(0, 2400, 1))
new = [f'{i // 100:02d}:{i % 100:02d}' for i in original]

# Create a DataFrame
time_lookup = pd.DataFrame({'original': original, 'new': new})
```

This is what the output looks like 

```
      original    new
0            0  00:00
1            1  00:01
2            2  00:02
3            3  00:03
4            4  00:04
...        ...    ...
2395      2395  23:95
2396      2396  23:96
2397      2397  23:97
2398      2398  23:98
2399      2399  23:99
```

I commented out some of the print commands that Lizzie used to debug the script.  The script appears to be working properly.  However, It appears, that it gets the data from yesterday if available, so additional modifications may be required.  Fortunately, we can do that on the fly, and not have to recreate the container.

## Current status 

* Nov 14, 2023 
* /Users/lab/singularity-vm3/01_radar
* /vagrant/radar


Execution of the first step, radar 

```
singularity exec --bind /vagrant radar.sif python /vagrant/scripts/time_fix_yesterday.py 230609
```


Container files

* environment.yml   # needed for the conda environment
* radar.def         # needed to create the container
* radar.sif         # the actual container file.


**TODO:** We need to check on the urls and output files 

Looks like we can use the following commands for today and yesterday 

```
$(date +%y%m%d)
$(date --date="yesterday" +%y%m%d)
```

So we can run the script like this 

```
singularity exec --bind /vagrant radar.sif python /vagrant/scripts/time_fix_yesterday.py $(date --date="yesterday" +%y%m%d)
```


May need to create an if than statement if yesterday is used or if the the date is 1 less than the current date.

Email from Lizzie

```
I just checked and it seems that one in particular doesn't exist is because it is yesterday's date, and therefore the link for the day prior would be https://www.spc.noaa.gov/climo/reports/yesterday_raw_wind.csv.

If you do the day before yesterday, the link would be https://www.spc.noaa.gov/climo/reports/231112_rpts_raw_wind.csv. 
I am pretty confident that is a consistent naming convention for the files, so that the day before today (yesterday) will always have the link with yesterday_raw_wind (not the date of yesterday) and all other dates besides today will have the link with the date.
```


# Other notes 


I need to verify that the output should have the same date as the specified day.

```
more 2023_06_09_SR_timefix.csv
,event_id,Time,Speed(MPH),Location,County,State,LAT,LON,Remarks
0,1,2023-06-09 00:00,UNK,1 NE Orange Springs,Putnam,FL,29.52,-81.93,Tree downed along S County Rd 315. Time of event estimated via radar. (JAX)
1,2,2023-06-09 00:00,63,5 NE West Bay,Bay,FL,30.35,-85.8,ASOS station KECP Panama City measured 63mph gust. (TAE)
2,3,2023-06-09 00:56,UNK,3 W Saint Teresa,Franklin,FL,29.93,-84.5,Fallen trees and limbs resulted in a power outage via Duke Energy outage map. (TAE)
3,4,2023-06-09 01:47,UNK,4 W Vicksburg,Bay,FL,30.33,-85.72,High winds along Highway 388 blew heavy objects into a yard. Nearby KECP gusted to 63 mph. (TAE)
4,5,2023-06-09 02:00,UNK,1 ESE Flagler Beach,Flagler,FL,29.47,-81.12,Corrects previous tstm wnd dmg report from 1 ESE Flagler Beach. Power Line Down along A1A be
```

I am also not sure if I am seeing two days.  

Lizzie mentions 

```
Times between 1200UTC-2359UTC have yesterday's date. Times between 0000UTC and 1159UTC have today's date.
```

* Nov 20, 2023

I believe I have fixed the date issue, just needed to verify the for loop is working properly.



* Jan 4, 2024

Reworking the 01_radar script.  It is not giving the dates properly and I now believe I have a better understanding of the dates for the data.

Include the following csv in the radar google drive folder.  I have code generate this table but include it for reference.
* /work/wgallus/etirone2/spc_raw_SR_2018/HWT_test/TimeLookup.csv

I got it all working and cleaned up.

* Jan 5, 2024
* /work/gif4/severin/2023_Gallus_SevereWind/temp/01_radar/GOOD2GO

uploaded the files to google drive 

```
singularity exec --bind $PWD /work/gif4/containers/rclone_latest.sif rclone sync --stats-one-line -P --stats 2s ./ gdriveISUGIF:2023_Gallus_SevereWind/01_radar/
```

* Jan 25, 2024

To be clear about the dates. 

```

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
```


In the original code, a variable labeled yesterday was generated. But the data collected included data from yesterday and today. Since I have been giving specific dates, it made it difficult to determine what that meant in the code that worked on yesterday and today. So for a given date, I determined that the input data has values <=1159 that would normally have today's date will now have a variable I have labeled as tomorrow's date because yesterday is now the date specified (specific_date variable). 

      Old code 
      Yesterday's date and Today's date (<=1159)

      New code 
      Specific date and Tomorrow's date (<=1159)