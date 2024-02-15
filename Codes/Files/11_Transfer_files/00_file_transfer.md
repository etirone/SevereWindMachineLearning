# File transfer

* Feb 9, 2024
* /work/wgallus/etirone2/

I am going to transfer the bulk of or Lizzie's folder on Nova to google drive.

```
/work/wgallus/etirone2/hwt_2023$ du -hs ../*

## These files will not be transferred to google drive
1.7T    ../analyses_40
15G     ../continuous_spc
106G    ../data_2019
253G    ../data_2020_2021

## These folders will be transferred to google drive
12G     ../gempaktest
449M    ../hwt_2020
21G     ../hwt_2021
2.6G    ../hwt_2022
15G     ../hwt_2023
1.5G    ../ml_training
1.1G    ../model_files
536G    ../new_data
16M     ../plot_SR
3.3G    ../population_data
17M     ../radar_curvature
616K    ../real_time
512     ../script_testing
5.5G    ../spc_raw_SR_2018
102M    ../storm_report_files
2.3M    ../subsevere_radar
39M     ../verification_data
```


```
singularity exec --bind $PWD /work/gif4/containers/rclone_latest.sif rclone sync --stats-one-line -P --stats 2s /work/wgallus/etirone2/gempaktest gdriveISUGIF:2023_Gallus_SevereWind/etirone2/gempaktest

singularity exec --bind $PWD /work/gif4/containers/rclone_latest.sif rclone sync --stats-one-line -P --stats 2s /work/wgallus/etirone2/hwt_2020 gdriveISUGIF:2023_Gallus_SevereWind/etirone2/hwt_2020

singularity exec --bind $PWD /work/gif4/containers/rclone_latest.sif rclone sync --stats-one-line -P --stats 2s /work/wgallus/etirone2/hwt_2021 gdriveISUGIF:2023_Gallus_SevereWind/etirone2/hwt_2021

singularity exec --bind $PWD /work/gif4/containers/rclone_latest.sif rclone sync --stats-one-line -P --stats 2s /work/wgallus/etirone2/hwt_2022 gdriveISUGIF:2023_Gallus_SevereWind/etirone2/hwt_2022

singularity exec --bind $PWD /work/gif4/containers/rclone_latest.sif rclone sync --stats-one-line -P --stats 2s /work/wgallus/etirone2/hwt_2023 gdriveISUGIF:2023_Gallus_SevereWind/etirone2/hwt_2023

singularity exec --bind $PWD /work/gif4/containers/rclone_latest.sif rclone sync --stats-one-line -P --stats 2s /work/wgallus/etirone2/ml_training gdriveISUGIF:2023_Gallus_SevereWind/etirone2/ml_training

singularity exec --bind $PWD /work/gif4/containers/rclone_latest.sif rclone sync --stats-one-line -P --stats 2s /work/wgallus/etirone2/model_files gdriveISUGIF:2023_Gallus_SevereWind/etirone2/model_files

singularity exec --bind $PWD /work/gif4/containers/rclone_latest.sif rclone sync --stats-one-line -P --stats 2s /work/wgallus/etirone2/new_data gdriveISUGIF:2023_Gallus_SevereWind/etirone2/new_data

singularity exec --bind $PWD /work/gif4/containers/rclone_latest.sif rclone sync --stats-one-line -P --stats 2s /work/wgallus/etirone2/plot_SR gdriveISUGIF:2023_Gallus_SevereWind/etirone2/plot_SR

singularity exec --bind $PWD /work/gif4/containers/rclone_latest.sif rclone sync --stats-one-line -P --stats 2s /work/wgallus/etirone2/population_data gdriveISUGIF:2023_Gallus_SevereWind/etirone2/population_data

singularity exec --bind $PWD /work/gif4/containers/rclone_latest.sif rclone sync --stats-one-line -P --stats 2s /work/wgallus/etirone2/radar_curvature gdriveISUGIF:2023_Gallus_SevereWind/etirone2/radar_curvature

singularity exec --bind $PWD /work/gif4/containers/rclone_latest.sif rclone sync --stats-one-line -P --stats 2s /work/wgallus/etirone2/real_time gdriveISUGIF:2023_Gallus_SevereWind/etirone2/real_time

singularity exec --bind $PWD /work/gif4/containers/rclone_latest.sif rclone sync --stats-one-line -P --stats 2s /work/wgallus/etirone2/script_testing gdriveISUGIF:2023_Gallus_SevereWind/etirone2/script_testing

singularity exec --bind $PWD /work/gif4/containers/rclone_latest.sif rclone sync --stats-one-line -P --stats 2s /work/wgallus/etirone2/spc_raw_SR_2018 gdriveISUGIF:2023_Gallus_SevereWind/etirone2/spc_raw_SR_2018

singularity exec --bind $PWD /work/gif4/containers/rclone_latest.sif rclone sync --stats-one-line -P --stats 2s /work/wgallus/etirone2/storm_report_files gdriveISUGIF:2023_Gallus_SevereWind/etirone2/storm_report_files

singularity exec --bind $PWD /work/gif4/containers/rclone_latest.sif rclone sync --stats-one-line -P --stats 2s /work/wgallus/etirone2/subsevere_radar gdriveISUGIF:2023_Gallus_SevereWind/etirone2/subsevere_radar

singularity exec --bind $PWD /work/gif4/containers/rclone_latest.sif rclone sync --stats-one-line -P --stats 2s /work/wgallus/etirone2/verification_data gdriveISUGIF:2023_Gallus_SevereWind/etirone2/verification_data

```

Transfer complete 
