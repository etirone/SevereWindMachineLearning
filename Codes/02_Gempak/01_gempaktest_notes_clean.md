# Gempak clean version

* Oct 17, 2023
* 

I am working on a cleaned up version of how I made the containers to function with the scripts as 02a_gempaktest.md was a lot more about getting singularity and vagrant running properly on a macbook.

## TODO 

I will need to figure out if I need to:

* alma_gempak.sif
   * put the scripts inside the container or if the script can be run outside the container
   * looks like it is going to need python3 or some version of python and pandas

I had chatGPT look over the gempaktest.py and gempak.py scripts and make recommendations for what I needed to include in the definition file that Yash and I got gempak working in. It suggested python and the required pip libraries. 

Here is the alma8_gempak.def file


```
Bootstrap: docker
From: almalinux/8-base

%environment
    export NAWIPS=/GEMPAK7
    export NA_OS=linux64_gfortran
    export PATH=$PATH:/GEMPAK7/os/linux64/bin/

%files

%post
    # Create necessary directories
    if [ ! -d /home/vagrant ]; then
        mkdir -p /home/vagrant
    fi
    if [ ! -d /vagrant ]; then
        mkdir -p /vagrant
    fi

    # Install required system packages
    dnf --rpmverbosity=debug install gcc gcc-c++ gcc-gfortran libX11 libX11-devel libXt-devel libXext libXp libXp-devel libXft-devel libXtst-devel xorg-x11-xbitmaps flex byacc *fonts-ISO8859-* wget make automake kernel-devel diffutils motif-devel libtool vim nano -y

    # Install Python, pip and required Python libraries
    dnf install python3 python3-pip -y
    pip3 install numpy pandas

    # Download and set up GEMPAK
    cd /
    wget -O gempak.tar.gz https://github.com/Unidata/gempak/archive/refs/tags/7.16.1.tar.gz
    tar -xvzf gempak.tar.gz
    mv gempak-7.16.1 GEMPAK7
    echo "export NAWIPS=/GEMPAK7" >> GEMPAK7/Gemenviron.profile
    ln -s GEMPAK7/ NAWIPS
    cd GEMPAK7
    . /GEMPAK7/Gemenviron.profile
    make everything
    
```

## Testing alma_gempak.sif 

#### test gempak install 

```
singularity exec alma8_gempak.sif gdlist
 [IP -10] GDLIST
 [GEMPLT -101]
Error in message send = 22
itype, ichan, nwords,0,32769,3
```

#### test python install 

```
singularity exec alma8_gempak.sif gdlist
 [IP -10] GDLIST
 [GEMPLT -101]
Error in message send = 22
itype, ichan, nwords,0,32769,3
vagrant@vagrant:/vagrant$ singularity exec alma8_gempak.sif python3
Python 3.6.8 (default, Jun 22 2023, 07:44:04)
[GCC 8.5.0 20210514 (Red Hat 8.5.0-18)] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import pandas as pd
>>> import numpy as np
```

Both check out. I need to test the script with real data.




## Separate Container Gempak only

* Nov 14, 2023

I was able to get the radar script working in a separate container.  I am now moving on to make sure this step in the pipeline is working properly.

* /Users/lab/singularity-vm3/02_gempak
* laptop: /vagrant/02_gempak 


Test that gdlist is working properly. 

```
singularity exec gempak_alma8.sif /GEMPAK7/os/linux64/bin/gdlist
 [IP -2]
 [IP -10] GDLIST
 [GEMPLT -101]
Error in message send = 22
itype, ichan, nwords,0,65538,3
```

* Check 

Copy over the scripts I need to test this step. 

```
cp ../scripts/gempak* .
```


* Nov 15, 2023
* Nova: /work/gif4/severin/containers/02_gempak
I noticed I never sourced the gempak environment file. I will try that now 

```
cp /work/wgallus/gempak/Gemenviron.profile .

```

I created a new folder and ran the singularity container again using the original gempak.py and gempaktest.py files as far as I could tell which I copied from here: `/work/wgallus/etirone2/hwt_2023/`


```
singularity exec --bind $PWD ../gempak_alma8.sif python3 /work/gif4/severin/containers/02_gempak/test/gempaktest.py 2023 06 09
 GDATTIM   Grid date/time                    LAST
 GLEVEL    Grid level                        500
 GVCORD    Grid vertical coordinate          PRES
 GFUNC     Scalar grid                       TMPC
 GDFILE    Grid file                         $GEMPAK/data/hrcbob.grd
 GAREA     Graphics area                     WV
 PROJ      Map projection/angles/margins|dr  MER
 SCALE     Scalar scale / vector scale       999
 OUTPUT    Output device/filename            T
 Parameters requested: GDATTIM,GLEVEL,GVCORD,GFUNC,GDFILE,GAREA,PROJ,SCALE,
 OUTPUT.
 GEMPAK-GDLIST> GEMPAK-GDLIST> GEMPAK-GDLIST> GEMPAK-GDLIST> GEMPAK-GDLIST> GEMPAK-GDLIST> GEMPAK-GDLIST> GEMPAK-GDLIST> GEMPAK-GDLIST> GEMPAK-GDLIST> GEMPAK-GDLIST>Traceback (most recent call last):
  File "/work/gif4/severin/containers/02_gempak/test/gempaktest.py", line 59, in <module>
    gl.run()
  File "/work/gif4/severin/containers/02_gempak/test/gempak.py", line 137, in run
    self._run()
  File "/work/gif4/severin/containers/02_gempak/test/gempak.py", line 241, in _run
    (_stdout, _stderr) = app.communicate(input=inString.encode('ascii'), timeout=15)
  File "/usr/lib64/python3.6/subprocess.py", line 863, in communicate
    stdout, stderr = self._communicate(input, endtime, timeout)
  File "/usr/lib64/python3.6/subprocess.py", line 1560, in _communicate
    self.wait(timeout=self._remaining_time(endtime))
  File "/usr/lib64/python3.6/subprocess.py", line 1469, in wait
    raise TimeoutExpired(self.args, timeout)
subprocess.TimeoutExpired: Command '/GEMPAK7/os/linux64/bin/gdlist' timed out after 14.999811654910445 seconds
```

I am wondering if I need to modify the Gemenvironment file inside the container or create one and the have it replace the one inside the folder using files. then I can just source it from within the /environment file that inside the container.  

is it possible that the gempakenvironment.profile isn't being properly sourced inside the container? 

I fixed a few things and am trying to build one more time
* linux64 instead of linux65_fortran
* I also am letting the Gempackenviron.profile be sourced from the container. I made changes and am including the file in the appropriate place then calling from the /environment


* /vagrant/02_gempak

```
sudo singularity build gempak_alma8_new.sif gempak_alma8.def
```


* Nov 16, 2023

It turns out that the scripts they are using are sensitive to the version of Gempak we install.  With version 7.15.1 the script runs successfully. 

Success!  I was able to successfully build the Gempak container and have it output the .dat files!

```
singularity exec --bind /vagrant gempak_alma8.sif python3  /vagrant/02_gempak/gempaktest.py 2023 06 09
```

The gempak_alma8.def file requires the Gemenviron.profile.  Both files are included in this repo.


## Uploaded the files to google drive 

* Jan 5, 2024
* Nova: work/gif4/severin/2023_Gallus_SevereWind/temp/02_gempak/GOOD2GO

```
singularity exec --bind $PWD /work/gif4/containers/rclone_latest.sif rclone sync --stats-one-line -P --stats 2s ./ gdriveISUGIF:2023_Gallus_SevereWind/02_gempak/
```

