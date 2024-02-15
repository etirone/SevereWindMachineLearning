# running the ele_pop_new script 

I modified the script to accept specific dates 
## Input file 

Output file from gempaktest.py

* 2023_05_25_results.csv 

## Google Drive 

* https://drive.google.com/drive/folders/1WmZUSXn16tczsbVjdmwu7Pryt8xoPJQX?usp=share_link
    * 03_ele_pop_new
    
## required files 

* landscan2017.nc
* radar.sif

## Required Script modifications 

pop_dataInputFile = './landscan2017.nc'



## Command Execution 

* the 3 arguments are Year, Month, Day

```
singularity exec --bind $PWD ../01_radar/radar.sif python ele_pop_new.py 2023 05 25
```

## OUTPUT 

* table_with_elevation_2023_05_25.csv  
* table_with_elevation_and_pop_2023_05_25.csv


## OUTPUT Text 

```
{'results': [{'dataset': 'mapzen', 'elevation': 379.0, 'location': {'lat': 35.34, 'lng': -97.51}}], 'status': 'OK'}
379.0
ERROR 1: PROJ: proj_create_from_database: Open of /opt/conda/envs/radar-env/share/proj failed
Took --- 14.996439933776855 seconds ---
pop_frame:                  lat         lon  Band1  crs
0          0.004167 -124.995833    NaN  b''
1          0.004167 -124.987500    NaN  b''
2          0.004167 -124.979167    NaN  b''
3          0.004167 -124.970833    NaN  b''
4          0.004167 -124.962500    NaN  b''
...             ...         ...    ...  ...
43559995  54.995833  -70.037500    0.0  b''
43559996  54.995833  -70.029167    0.0  b''
43559997  54.995833  -70.020833    0.0  b''
43559998  54.995833  -70.012500    0.0  b''
43559999  54.995833  -70.004167    0.0  b''

[43560000 rows x 4 columns]
45
45
Program complete!
Took --- 17.244986057281494 seconds ---

```