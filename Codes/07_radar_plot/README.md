# Running the Radar Script 

Due to time constraints, I was not able to successfully get this program to run. I have updated the script to use the specific day inputs. 


## Input file 

* 2023_05_25_probs_sub.csv
* 2023_05_25_text_file.csv

## Google Drive 

## required files 

* 2023_05_25_probs_sub.csv
* 2023_05_25_text_file.csv
* radar_locs_updated.csv
* radar_plot.py

## Required script modifications

If the radar_locs_updated.csv file changes then you will need to update the csv file.

```
radar_locs = pd.read_csv('radar_locs_updated.csv')
```

## Command Execution 

```
python3 radar_plot.py  230525
```


## OUTPUT Files



## OUTPUT Text 