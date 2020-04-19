#!/bin/python
#--------------------------------------#
# vmbkup.py
# 
# https://github.com/jpickell/vmbkup
#
# A simple python script to run as root
# on an ESXI host to create backups of 
# the running virtual machines
#--------------------------------------#

### TODOS ###
# - Need to add logging and error checking

import sys
import os
import shutil
#import time
import urllib.request
from subprocess import call
from subprocess import check_output

# Required! Set this to the backup location 
# (currently local datastores only
bkpath = "/vmfs/volumes/USB-Datastore/backups/"

hostname = os.uname()[1]
vmlist = os.popen('vim-cmd vmsvc/getallvms')
vms = list(vmlist)

# Archive existing backups
bkpathA = bkpath+"/a"
bkpathB = bkpath+"/b"

print("Removing secondary backups from {:s}".format(bkpathB))
shutil.rmtree(bkpathB)
print("Archiving primary backups to secondary location...")
shutil.move(bkpathA,bkpathB)
print("Creating new primary backup location at {:s}\n".format(bkpathA))
os.mkdir(bkpathA)
bkpath = bkpathA+"/"

# Backup the Host configuration
bkloc = "{:s}configBundle-{:s}.tgz".format(bkpath,hostname)
if not os.path.isfile(bkloc):
  hostsync = "/bin/vim-cmd hostsvc/firmware/sync_config"
  hostbkup = "/bin/vim-cmd hostsvc/firmware/backup_config"

  print("Syncing host config: {:s}".format(hostsync))
  hs = os.popen(hostsync)
  print("Creating host config backup: {:s}".format(hostbkup))
  hb = check_output(["/bin/vim-cmd", "hostsvc/firmware/backup_config"])

  urlinfo = hb.decode(encoding='utf-8', errors='strict').split('/')
  url = "http://localhost/downloads/{:s}/configBundle-{:s}.tgz".format(urlinfo[4],hostname)

  wout = urllib.request.urlretrieve(url, bkloc)
  print("Config bundle downloaded to {:s}".format(bkpath))
else:
  print("Current config bundle already exists at {:s}".format(bkloc))
  
# Start the snapshot/clone process
print("\nCreating backups..")
# Process each VM individually
for v in vms: 
  vm=v.split()
  vmid = vm[0]
  vmname = vm[1]
  vmloc = vm[2].replace('[','').replace(']','')
  vmfile = vm[3].replace('vmx','vmdk')
  vmpath = "/vmfs/volumes/{:s}/{:s}".format(vmloc,vmfile)

  if vmid.isnumeric(): 
    print("{:s} {:s} {:s}".format(vmid, vmname, vmloc))
    snapstat = "vim-cmd vmsvc/snapshot.get {:s}".format(vmid)
    snapadd  = "vim-cmd vmsvc/snapshot.create {:s} vmbkup_snap".format(vmid)
    snaprem  = "vim-cmd vmsvc/snapshot.removeall {:s}".format(vmid)
    statecmd = "vim-cmd vmsvc/power.getstate {:s}".format(vmid)
    startcmd = "" 
    stopcmd  = "vim-cmd vmsvc/power.shutdown {:s}".format(vmid)
    bkupcmd  = "vmkfstools -i {:s} {:s}{:s}.vmdk -d thin".format(vmpath,bkpath,vmname)
  
    state = list(os.popen(statecmd))

    if "off" in state[1]:
      vmstate = "OFF"
      print("VM {:s} is {:s}; No backup executed".format(vmname,vmstate))
      #uncommment the following two lines if you want to back up vms that are off
      #print(bkupcmd)
      #bresults = os.system(bkupcmd)
    else:
      vmstate = "ON"
      print(vmstate)

      print(snapadd)
      sa_results = os.system(snapadd)
      print(bkupcmd)
      bresults = os.system(bkupcmd)
      print(snaprem)
      sr_results = os.system(snaprem)

    print("---\n")
 

