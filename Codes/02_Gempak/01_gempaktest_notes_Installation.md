# gempaktest.py (jobscript.sh) - processes mesoanalysis data


* Sept 8th 2023
* Vagrant singularity folder on laptop 

## set up vagrant VM

```
vagrant plugin install vagrant-disksize
vagrant init sylabs/singularity-3.5-ubuntu-bionic64
vagrant up
vagrant ssh
```

## Create singularity container from the def file.

```
sudo singularity build gempak_alma8.sif gempak_alma8.def 

```

## Verify that it installed the gd files 

```
singularity exec gempak_alma8.sif ls /GEMPAK7/os/linux64_gfortran/bin
singularity exec gempak_alma8.sif /GEMPAK7/os/linux64_gfortran/bin/gdlist
 [IP -2]
 [IP -10] GDLIST
 [GEMPLT -101]
Error in message send = 22
itype, ichan, nwords,0,0,3
```

Everything looks good.


## Let's create a sandbox and start installing everything.


```
sudo singularity build --sandbox gempakSandbox gempak_alma8.sif
 sudo singularity build --fix-perms --sandbox gempakSandbox gempak_alma8.sif 
```

## Now enter the writeable shell of this sandbox

```
singularity shell --writable gempaksandbox/
```


## Install some needed programs 

```
dnf install vim 
```

## Writable overlay 

* Sept 12, 2023


* https://docs.sylabs.io/guides/3.5/user-guide/persistent_overlays.html

I can't seem to get the sandbox to work properly. So instead I am going to make an overlay and record all the commands I need to get a functioning container and periodically update the container with the new installs until the definition file has everything it needs to create a container in one go. 

```
brew install e2fsprogs
export PATH="/usr/local/opt/e2fsprogs/bin:$PATH 
export PATH="/usr/local/opt/e2fsprogs/sbin:$PATH"

# this is 30G overlay
dd if=/dev/zero of=overlay.img bs=1G count=30 && \
    mkfs.ext3 overlay.img

vagrant up
vagrant ssh
sudo singularity shell --overlay overlay.img gempak_alma8.sif

```


The overlay worked!!! That means I can now start adding the required programs and start testing.


## testing 

without overlay

```
sudo singularity shell  gempak_alma8.sif
/GEMPAK7/os/linux64/bin/gdlist
```
this worked

```
[IP -2]
 [IP -10] GDLIST
 [GEMPLT -101]
Error in message send = 22
itype, ichan, nwords,0,0,3
 [IP -1]
```

With an Overlay 

```
sudo singularity shell --overlay overlay.img gempak_alma8.sif
/GEMPAK7/os/linux64/bin/gdlist
```

This is working.  I had to fix the overlay file after installing the right tools (see above).


## Grab files for testing

* Sept 14th, 2023
* /Users/lab/singularity-vm2

These files were about 15G and I transferred them to my laptop. This folder `/Users/lab/singularity-vm2` is where I start the vagrant virtual machine on my mac to work on singularity containers.

```
rsync -avz -e ssh severin@novadtn.its.iastate.edu:/work/gif4/severin/2023_Gallus_SevereWind/temp/01_rewrite/hwt_2023 .

rsync -avz -e ssh severin@novadtn.its.iastate.edu:/work/gif4/severin/2023_Gallus_SevereWind/temp/01_rewrite/scripts .

```


## Restart the vagrant and enter the container 

```
vagrant up
vagrant ssh
sudo singularity shell --overlay overlay.img gempak_alma8.sif
```


## installing conda for radar

I exported the conda environment from nova into a yml file that I am using to add the conda environment to the container.

```
conda env create -f radar.yml

#add the following to enviromental file
conda activate radar

```


## Other installations 

```
#create a directory for downloads
mkdir ~/Downloads 

#need python3 for conda installation
dnf install python3 -y
#dnf install procsps-ng -y

#download conda install
wget -P ~/Downloads https://repo.anaconda.com/archive/Anaconda3-2021.11-Linux-x86_64.sh
cd ~/Downloads

# run the install, agree to license and place in usr/local
bash Anaconda3-2021.11-Linux-x86_64.sh -u -b -p /usr/local/

```

* Sept 14th, 2023

I am working on installing anaconda still, once that is installed, install radar with conda so that the first script will run properly. and then continue with the second script.  I am hoping they use the same python.

I think this is the command we need to test once pythom is installed. 

`python gempaktest.py 6 9 2023`


START HERE
so things aren't proceeeding. start by rebooting and remaking the overlay ie starting over

```
# be sure to make the overlay.img in the bound folder rather than the vagrant image or you run into disk space issues.

cd /vagrant
dd if=/dev/zero of=overlay.img bs=1G count=30 &&  mkfs.ext3 overlay.img
```

```
singularity shell --overlay overlay.img gempak_alma8.sif
```

* Sept 22, 2023

Generating the image in the vagrant file took quiet a while and I had to be in front of the computer so it wouldn't shutdown midway through. 

```
#create a directory for downloads
mkdir /vagrant/Downloads 

#need python3 for conda installation
dnf install python3 -y
dnf install procsps-ng -y

#download conda install
wget -P /vagrant/Downloads https://repo.anaconda.com/archive/Anaconda3-2021.11-Linux-x86_64.sh
cd /vagrant/Downloads

# run the install, agree to license and place in usr/local
bash Anaconda3-2021.11-Linux-x86_64.sh -u -b -p /usr/local/

```

* Sep 29, 2023

I have figured out a way forward with the containers, while not elegant it will work. I am building the containers from scratch but only piece meal.  once I get all the pieces working then I will create a final container. 

I was able to get conda installed and am working on installing the radar from the yml file. 

#### Memory issues 

I ran into some issues with memory so set up a swap file on the /vagrant partition 

```
sudo dd if=/dev/zero of=/vagrant/swapfile bs=1M count=12288
sudo chmod 600 /vagrant/swapfile
sudo mkswap /vagrant/swapfile
sudo swapon /vagrant/swapfile
```

I also upped the vagrant virtual memory from 1 to 8G in the vagrant file.


* Oct 3, 2023

I figured out that the hard drive space was still expanded despite allocating more. Here is how I fixed it. 

The details you provided show that the root filesystem is not directly on `/dev/sda1`. Instead, it's on a logical volume (`/dev/mapper/vagrant--vg-root`). This means you are using LVM (Logical Volume Management) on your VM. 

Given this setup, here's how you can resize your logical volume and filesystem:

1. **Expand the Physical Volume**:

   First, you need to tell LVM to use the new space on `/dev/sda1`:

   ```bash
   sudo pvresize /dev/sda1
   ```

2. **Check Available Space for the Logical Volume**:

   See how much free space you have in the volume group:

   ```bash
   sudo vgs
   ```

   Note the 'VFree' column for the amount of free space.

3. **Expand the Logical Volume**:

   Resize the logical volume to fill the available space (or specify a size):

   ```bash
   sudo lvextend -l +100%FREE /dev/mapper/vagrant--vg-root
   ```

4. **Resize the Filesystem**:

   Now, resize the ext4 filesystem on the logical volume:

   ```bash
   sudo resize2fs /dev/mapper/vagrant--vg-root
   ```

5. **Verify**:

   Finally, verify that the root filesystem now uses the entire available space:

   ```bash
   df -h
   ```





Once I get the radar installed via conda, I will want to give it a try with the script, going back to the first step and then trying this gempak second step after I do a full install.  I may need to up the swap space again.

Radar using conda is taking a really long time, It may make more since to install mamba and try installing it using mamba instead. 
Start with mamba if it hasn't finished by the next time I look at this. 


* Oct 10, 2023

```
/usr/local/miniconda/bin/mamba env create -f /vagrant/radar.yml


conda update --prefix /usr/local/miniconda anaconda -y
```

I think I should start by making containers for each script and combine where I can, I think Gempak is making this more difficult!

* Oct 17, 2023

I will need to figure out if I need to:

* alma_gempak.sif
   * put the scripts inside the container or if the script can be run outside the container
   * looks like it is going to need python3 or some version of python and pandas



TODO 

* figure out how to run script inside singularity container 
    * what files do I need to run it
    * how do I set the folder location rather than having it as a fixed location inside the script
    * rename the script?
    * rsync the needed files from Nova

* done: test gdlist 
* add export NAWIPS=/GEMPAK7 to environmental file