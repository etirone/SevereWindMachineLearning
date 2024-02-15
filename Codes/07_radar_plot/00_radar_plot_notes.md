# Notes about how I updated the radar_plot script 

* Feb 13, 2024

I tried to modify the radar.def file to create a radar.sif container that will work for this but am having a lot of trouble.  I suspect a different container or someone more familiar with what radar_plot.py is doing will be able to trouble shoot this more efficiently.


* Feb 1, 2024
 

I am working on getting it to work with a specific date. The today and yesterday variables are so strongly incorporated that i just renamed my regular convention of specific_date and tomorrow_test with yesterday and today.

```
day_yesterday = specific_date
today = tomorrow
```



Unfortunately, I am getting the following error due to a missing library. I will see if I can include that in the radar.sif container.  Hopefully that won't break the pipeline by introducing some kind of dependency conflict.

```
singularity exec ../01_radar/GOOD2GO/radar.sif python radar_plot.py  230525
ERROR 1: PROJ: proj_create_from_database: Open of /opt/conda/envs/radar-env/share/proj failed

## You are using the Python ARM Radar Toolkit (Py-ART), an open source
## library for working with weather radar data. Py-ART is partly
## supported by the U.S. Department of Energy as part of the Atmospheric
## Radiation Measurement (ARM) Climate Research Facility, an Office of
## Science user facility.
##
## If you use this software to prepare a publication, please cite:
##
##     JJ Helmus and SM Collis, JORS 2016, doi: 10.5334/jors.119

Traceback (most recent call last):
  File "radar_plot.py", line 48, in <module>
    import cv2
ImportError: libGL.so.1: cannot open shared object file: No such file or directory
```


Looks like I have pyproj in the environmental.yml file used in the definition file.  So perhaps the PROJ_LiB environmental variable may not be set properly and not sure about the libGL.so.1. I will need to shell in and see if I can find it.

* Feb 9, 2024 
* nova: /work/gif4/severin/2023_Gallus_SevereWind/temp/07_radar_plot

Added these two lines to environmental.yml file and built a radarU.sif container (not included in the repo or box folder as it didn't solve the problem) 

```
  - mesa-libgl-cos6-x86_64
  - opencv
```

```
singularity exec --bind ./proj:/opt/conda/envs/radar-env/share/proj/ --env LD_LIBRARY_PATH=/opt/conda/pkgs/mesa-libgl-cos6-x86_64-11.0.7-h9b0a68f_1105/x86_64-conda-linux-gnu/sysroot/usr/lib64:/opt/conda/pkgs/mesa-dri-drivers-cos6-x86_64-11.0.7-h9b0a68f_1105/x86_64-conda-linux-gnu/sysroot/usr/lib64:$LD_LIBRARY_PATH ./radarU.sif /opt/conda/envs/radar-env/bin/python3 radar_plot.py 230525
```



