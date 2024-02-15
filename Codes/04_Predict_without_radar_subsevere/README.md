# Running Predict_without_radar_subsevere

This program is run in R.  I made some attempts to convert it to python and realized that I did not have a sufficient understanding of the machine learning model used in the R script to accurately convert it to python.  My attempt is located in the the [PythonAttempt folder](PythonAttempt).  

The R script that is run is 

* Predict_without_adar_subsevere.R 

This script requires the following libraries

* library(mxnet)
* library(caret);library(caretEnsemble)
* library(pROC);library(plotROC)
* library("tm"); 
* library("SnowballC"); 
* library("wordcloud"); 
* library("RColorBrewer");
* library("Matrix")

Unfortunately, this script calls another script. 

* new_all_fn.R  

This script requires the following libraries:

list.of.packages <- c("MASS","lattice","nlme","Matrix","class","codetools","rpart","survival","ROCR",
                      "tidyverse","ggplot2", "dplyr", "tidyr",
                      "topicmodels", "tm", "SnowballC", "wordcloud", "tidytext", "stringr",
                      "RColorBrewer", "maps", "caret", "caretEnsemble")


## Creating a container

I did not have time to create a container for this script. But I have a place to start. 


First build mxnet-base

```
Bootstrap: docker
From: nvidia/cuda:11.7.0-cudnn8-devel-ubuntu18.04 

%post


export DEBIAN_FRONTEND=noninteractive
export TZ=US/Chicago
apt-get update && apt-get install -y \
    build-essential git libatlas-base-dev libopencv-dev python-opencv \
    libcurl4-openssl-dev libgtest-dev cmake wget unzip python3-pip \
    ninja-build ccache libopenblas-dev

cd /usr/src/gtest && cmake CMakeLists.txt && make && cp *.a /usr/lib

cd /opt

wget https://github.com/Kitware/CMake/releases/download/v3.26.3/cmake-3.26.3-linux-x86_64.tar.gz

tar xvf cmake-3.26.3-linux-x86_64.tar.gz


export BUILD_OPTS="USE_CUDA=1 USE_CUDA_PATH=/usr/local/cuda USE_CUDNN=1"
cd /opt

git clone --recursive https://github.com/apache/mxnet 
cd mxnet
git checkout 1.9.1
git submodule init
git submodule update --recursive
cp config/linux_gpu.cmake config.cmake
cd cmake/upstream 
wget https://raw.githubusercontent.com/apache/mxnet/master/cmake/upstream/select_compute_arch.cmake -O select_compute_arch.cmake
cd ../../
mkdir build 
cd build
/opt/cmake-3.26.3-linux-x86_64/bin/cmake ..
/opt/cmake-3.26.3-linux-x86_64/bin/cmake --build . --parallel 8```

```

Then add R to the container,  I haven't tested this so I am sure there are several libraries that I mentioned above that still needed to be added to this. 


```
Bootstrap: localimage
From: mxnet-1.9.1.sif 

%post


# update indices
apt update -qq
# install two helper packages we need
apt install --no-install-recommends software-properties-common dirmngr -y
# add the signing key (by Michael Rutter) for these repos
# To verify key, run gpg --show-keys /etc/apt/trusted.gpg.d/cran_ubuntu_key.asc 
# Fingerprint: E298A3A825C0D65DFD57CBB651716619E084DAB9
wget -qO- https://cloud.r-project.org/bin/linux/ubuntu/marutter_pubkey.asc | tee -a /etc/apt/trusted.gpg.d/cran_ubuntu_key.asc
# add the R 4.0 repo from CRAN -- adjust 'focal' to 'groovy' or 'bionic' as needed
add-apt-repository "deb https://cloud.r-project.org/bin/linux/ubuntu bionic-cran40/"
add-apt-repository ppa:c2d4u.team/c2d4u4.0+
add-apt-repository ppa:cran/libgit2



apt-get update
apt-get install -y r-base-core r-cran-rlang r-cran-roxygen2 libcairo2-dev libxml2-dev
apt-get install -y r-cran-gert
apt-get install -y r-cran-usethis
apt-get install -y r-cran-devtools
export LD_LIBRARY_PATH=/opt/mxnet/build:$LD_LIBRARY_PATH


cd /opt/mxnet

make -f R-package/Makefile rpkg
```

This should work on both GPU and CPU


I am leaving the rest of this documentation outline for consistency for future use once someone figures out the R installation or R container creation.


## Input file 

## Google Drive 

## required files 
* table_with_elevation_2023_05_25.csv
* new_all_fn.py

## Required script modifications

## Command Execution 



## OUTPUT Files


