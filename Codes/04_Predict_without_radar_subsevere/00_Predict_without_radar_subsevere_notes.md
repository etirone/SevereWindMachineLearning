# The Predict_without_radar_subsevere R script 

* Nov 17, 2023

This is the script I was asked to convert to python.  But first I want to make sure I understand what it is doing and that I can get it to run with output that I can then try to reproduce when I rewrite it with python

## create the definition file

```
Bootstrap: docker
From: r-base:latest

%post
    # Update and install system dependencies (if any)
    apt-get update && apt-get install -y libcurl4-openssl-dev libssl-dev libxml2-dev

    # Install R packages
    R -e "install.packages(c('topicmodels', 'tidytext', 'tidyverse', 'mxnet', 'caret', 'caretEnsemble', 'pROC', 'plotROC'), repos='https://cloud.r-project.org/')"

    # You might need to adjust the library path or installation method depending on your specific requirements

%environment
    export PATH="/usr/local/lib/R/bin:$PATH"

%runscript
    exec R "$@"
```

## Build the container that supports R and libraries 

```
sudo singularity build Rcont.sif Rcontainer.def
```

* Nov 20, 2023

I am getting stuck with the installation of mxnet as an R package.  


I found this R function that may be useful.

/work/wgallus/etirone2//hwt_2021/Install_mxnet.R

Here is an example of the output 

/work/wgallus/etirone2//hwt_2021/Install_mxnet.R 

```
"","event_id","lon","lat","year","day","month","hr","min","gbm","svmRadial","mxnetAdam","stack_glm","stack_rf","avg_ens","indicator_text","magnitude"
"1",1,29.71,-95.12,2021,3,6,17,54,0.563525991952772,0.457693767391535,0.544641077518463,0.521096178761409,0.636,0.52195361228759,0,NA
"2",2,43.29,-75.55,2021,3,6,19,32,0.888179436635093,0.457693767391533,0.632675409317017,0.675679008671722,0.616,0.659516204447881,0,NA
"3",3,43.29,-75.55,2021,3,6,19,43,0.814426108078715,0.457693767391533,0.63165682554245,0.655569472256434,0.628,0.634592233670899,0,NA
"4",4,36.81,-84.46,2021,3,6,20,0,0.980007484881323,0.90715751266419,0.550599217414856,0.791688204830374,0.896,0.812588071653456,0,NA
"5",5,39.37,-77.06,2021,3,6,20,12,0.0440592034967092,0.457693767391531,0.60288143157959,0.412172883957917,0.286,0.368211467489277,0,NA
"6",6,39.32,-77.74,2021,3,6,20,15,0.337287318639379,0.457693767391535,0.599424660205841,0.495423986526557,0.6,0.464801915412252,0,NA
"7",7,39.35,-76.95,2021,3,6,20,24,0.0434424709500362,0.457693767391531,0.601368248462677,0.410891955824544,0.308,0.367501495601415,0,NA
```