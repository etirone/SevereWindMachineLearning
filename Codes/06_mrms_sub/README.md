# Running the Radar Script 

## Input file 

* metpy_us_stations.csv
* mrms_sub.py
* 2023_05_25_SR_timefix.csv

## Google Drive 

## required files 

* metpy_us_stations.csv

## Required script modifications
This line may need changes as it is hard-coded in.

# Use csv file from Jon
stations = pd.read_csv('metpy_us_stations.csv')


## Command Execution 

```
singularity exec ../01_radar/GOOD2GO/radar.sif python mrms_sub.py  230525
```

## OUTPUT Files

* 2023_05_25_sub_severe_reports.csv

## OUTPUT Text 

number of reports 12