# Running the Radar Script 

## Input files 

* 2023_05_25_SR_timefix.csv  
* final_probs_subsevere_2023.csv 
* text_file.py

## Google Drive 

## required files 

* final_probs_subsevere_2023.csv

## Required script modifications

This line will need to be modified if you change the final probabilities file.

```
#### Read in probabilities
probs = pd.read_csv('final_probs_subsevere_2023.csv', header=0)
```
## Command Execution 

singularity exec ../01_radar/GOOD2GO/radar.sif python text_file.py 230525

## OUTPUT Files

* 2023_05_25_probs_labeled.csv  
* 2023_05_25_probs_sub.csv  
* 2023_05_25_text_file.csv  
* SR_table.html  

