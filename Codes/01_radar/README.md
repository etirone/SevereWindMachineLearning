# Running the Radar Script 

## Input file 

Input is data downloaded from the NOAA Storm Prediction Center (SPC) website.  The data is in a csv format.  

* https://www.spc.noaa.gov/climo/reports/{args.date_input}_rpts_raw_wind.csv


## Google Drive 

* https://drive.google.com/drive/folders/1WmZUSXn16tczsbVjdmwu7Pryt8xoPJQX?usp=share_link
    * 01_radar

## Required files 

* time_fix_yesterday.py
* radar.sif
* url = f'https://www.spc.noaa.gov/climo/reports/{args.date_input}_rpts_raw_wind.csv'
* TimeLookup.csv

## Required script modifications

There is one line in the 'time_fix_yesterday.py' script that can be updated if you place the TimeLookup.csv file in a different folder than the script. 

```
timeTableConversionFile = './TimeLookup.csv'
```

## Command Execution 

```
# This script curently works for a specific date.
# the year being 23 instead of 2023 is due to the fact that the url only uses 2 digits for the year.

module load singularity
singularity exec radar.sif python time_fix_yesterday.py 230609


# I had intentions to have this script work with data from "yesterday" but ran out of time.
# it just needs a modified if statement to change the url to the url for yesterday's data which is different than specific dates.

singularity exec radar.sif python time_fix_yesterday.py $(date --date="yesterday" +%y%m%d)
```

## OUTPUT 

There are two output files.  The one in bold (2023_06_09_SR_timefix.csv) is the output that is used in step 02.


* 2023_06_09_SR.csv
* **2023_06_09_SR_timefix.csv**

Examples of the output can be found in the google drive folder.

## OUTPUT Text 


```
singularity exec radar.sif python time_fix_yesterday.new 230525
https://www.spc.noaa.gov/climo/reports/230525_rpts_raw_wind.csv
                                                                 Raw Wind/Gust LSR for 230525 12Z to 11:59Z the next day
Time Speed(MPH) Location          County     State LAT   LON                                                Remarks
1410 UNK        3 N SAN ANGELO    TOM GREEN  TX    31.49 -100.44  POWER POLES DOWN ON BOWIE ST... BETWEEN E 26TH...
2121 73         4 NW RYAN         PRESIDIO   TX    30.47 -104.35     MESONET STATION UP400 4.0 NW RYAN (UPR). (MAF)
2240 58         26 ENE CALLAO     TOOELE     UT    40.11 -113.31  MEASURED FROM DUGWAY PROVING GROUND DPG31 WEST...
2310 60         5 ENE FORESTGROVE FERGUS     MT    47.02 -108.98  ESTIMATED WIND GUSTS OF 50 TO 60 MPH. PEA SIZE...
0039 60         3 SSW HOLLISTER   TWIN FALLS ID    42.32 -114.59                                              (BOI)
0242 61         7 E TUCUMCARI     QUAY       NM    35.18 -103.6     ASOS STATION KTCC TUCUMCARI MUNI AIRPORT. (ABQ)
0256 82         9 SE TUCUMCARI    QUAY       NM    35.08 -103.61  WIND GUST TO 81.5 MPH MEASURED ON CAR ROOF ANE...
0300 75         7 E TUCUMCARI     QUAY       NM    35.18 -103.6     ASOS STATION KTCC TUCUMCARI MUNI AIRPORT. (ABQ)
                                                         -103.6   CORRECTS PREVIOUS TSTM WND GST REPORT FROM 7 E...
0317 UNK        8 SE TUCUMCARI    QUAY       NM    35.1  -103.61  REPORT FROM MPING: 1-INCH TREE LIMBS BROKEN; S...
0701 59         5 S BROADVIEW     CURRY      NM    34.75 -103.21                                              (ABQ)
0915 65         2 WNW TEXICO      CURRY      NM    34.4  -103.09                                              (ABQ)
     UNK        3 ENE CLOVIS      CURRY      NM    34.42 -103.16               MESONET STATION GW0819 CLOVIS. (ABQ)
0950 UNK        3 WNW LAYTON      GMZ032     FL    24.84 -80.86   A 57 KNOT... OR 65 MPH... WIND GUST FROM A DOW...
    Time
0   1410
1   2121
2   2240
3   2310
4     39
5    242
6    256
7    300
8    300
9    317
10   701
11   915
12   915
13   950
1410
2121
2240
2310
39
242
256
300
300
317
701
915
915
950
    event_id              Time Speed(MPH)           Location      County State    LAT     LON                                            Remarks
0          1  2023-05-25 14:10        UNK     3 N SAN ANGELO   TOM GREEN    TX  31.49 -100.44  POWER POLES DOWN ON BOWIE ST... BETWEEN E 26TH...
1          2  2023-05-25 21:21         73          4 NW RYAN    PRESIDIO    TX  30.47 -104.35     MESONET STATION UP400 4.0 NW RYAN (UPR). (MAF)
2          3  2023-05-25 22:40         58      26 ENE CALLAO      TOOELE    UT  40.11 -113.31  MEASURED FROM DUGWAY PROVING GROUND DPG31 WEST...
3          4  2023-05-25 23:10         60  5 ENE FORESTGROVE      FERGUS    MT  47.02 -108.98  ESTIMATED WIND GUSTS OF 50 TO 60 MPH. PEA SIZE...
4          5  2023-05-26 00:39         60    3 SSW HOLLISTER  TWIN FALLS    ID  42.32 -114.59                                              (BOI)
5          6  2023-05-26 02:42         61      7 E TUCUMCARI        QUAY    NM  35.18 -103.60    ASOS STATION KTCC TUCUMCARI MUNI AIRPORT. (ABQ)
6          7  2023-05-26 02:56         82     9 SE TUCUMCARI        QUAY    NM  35.08 -103.61  WIND GUST TO 81.5 MPH MEASURED ON CAR ROOF ANE...
7          8  2023-05-26 03:00         75      7 E TUCUMCARI        QUAY    NM  35.18 -103.60    ASOS STATION KTCC TUCUMCARI MUNI AIRPORT. (ABQ)
8          9  2023-05-26 03:00         75      7 E TUCUMCARI        QUAY    NM  35.18 -103.60  CORRECTS PREVIOUS TSTM WND GST REPORT FROM 7 E...
9         10  2023-05-26 03:17        UNK     8 SE TUCUMCARI        QUAY    NM  35.10 -103.61  REPORT FROM MPING: 1-INCH TREE LIMBS BROKEN; S...
10        11  2023-05-26 07:01         59      5 S BROADVIEW       CURRY    NM  34.75 -103.21                                              (ABQ)
11        12  2023-05-26 09:15         65       2 WNW TEXICO       CURRY    NM  34.40 -103.09                                              (ABQ)
12        13  2023-05-26 09:15        UNK       3 ENE CLOVIS       CURRY    NM  34.42 -103.16               MESONET STATION GW0819 CLOVIS. (ABQ)
13        14  2023-05-26 09:50        UNK       3 WNW LAYTON      GMZ032    FL  24.84  -80.86  A 57 KNOT... OR 65 MPH... WIND GUST FROM A DOW...
```

