# Running the Radar Script 

## Input file 

This is the file that is outputted from 01_radar script 

* 2023_05_25_SR_timefix.csv
* gempak_alma8.sif
* gempaktest.py
* gempak.py


## Google Drive 

* https://drive.google.com/drive/folders/1WmZUSXn16tczsbVjdmwu7Pryt8xoPJQX?usp=share_link
    * 02_gempak

## required files 

* oafile storm reports mesoanalysis/sfcoaruc_*
* paramsFile = "gempakparameters.csv"

## Required script modifications 

You can specify the location of the directory you are planning on running your script. 

directory_path = "/work/gif4/severin/2023_Gallus_SevereWind/temp/02_gempak/GOOD2GO"
The full directory path of your current working directory is required. 

This directory contains the input and required files. 

## Command Execution 

On an HPC system 

```
singularity exec --bind $PWD gempak_alma8.sif python3 ./gempaktest.py 2023 05 25
```


## OUTPUT Files

* run20230525
    * run20230525/2023_05_25_results.csv
    * *.dat files
        1_202305251410_SBCP.dat (here is an example of the file name)
    * gemglb.nts
    * last.nts
    
## OUTPUT Text 

```
GDLIST PARAMETERS:

Grid file: /vagrant/scripts/hwt_2023/mesoanalysis/sfcoaruc_23052609

GRID IDENTIFIER:
    TIME1             TIME2         LEVL1 LEVL2   VCORD PARM
230526/0900                             0          NONE EDCP

GAREA:    #34.75;-103.21;0.7;0.7
SCALE FACTOR : 10** 1
OUTPUT:    FILE/


MINIMUM AND MAXIMUM VALUES     0.03    15.53
Enter <cr> to accept parameters or type EXIT: Parameters requested: GDATTIM,GLEVEL,GVCORD,GFUNC,GDFILE,GAREA,PROJ,SCALE,
OUTPUT.
GEMPAK-GDLIST>Setting GDFILE to /vagrant/scripts/hwt_2023/mesoanalysis/sfcoaruc_23052609
Setting GDATTIM to LAST
Setting GFUNC to U8SV
Setting GAREA to #34.75;-103.21;0.7;0.7
Setting GLEVEL to 0
Setting GVCORD to NONE
Setting PROJ to MER
Setting SCALE to 999
Setting OUTPUT to f /11_202305260950_U8SV.dat
Current directory:  /vagrant/02_gempak/run20230525
Unique filename:  11_202305260950_U8SV.dat
GDATTIM   Grid date/time                    LAST
GLEVEL    Grid level                        0
GVCORD    Grid vertical coordinate          NONE
GFUNC     Scalar grid                       EDCP
GDFILE    Grid file                         /vagrant/scripts/hwt_2023/mesoanalysis/sfcoaruc_23052609
GAREA     Graphics area                     #34.75;-103.21;0.7;0.7
PROJ      Map projection/angles/margins|dr  MER
SCALE     Scalar scale / vector scale       999
OUTPUT    Output device/filename            f /11_202305260950_EDCP.dat
Parameters requested: GDATTIM,GLEVEL,GVCORD,GFUNC,GDFILE,GAREA,PROJ,SCALE,
OUTPUT.
GEMPAK-GDLIST> GEMPAK-GDLIST> GEMPAK-GDLIST> GEMPAK-GDLIST> GEMPAK-GDLIST> GEMPAK-GDLIST> GEMPAK-GDLIST> GEMPAK-GDLIST> GEMPAK-GDLIST> GEMPAK-GDLIST> GEMPAK-GDLIST>Creating process: gplt for queue 357629954
Creating process: gn for queue 357662723
```
    
This is repeated over and over for each data point.