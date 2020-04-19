# vmbkup.py #

 https://github.com/jpickell/vmbkup

 A simple python script to run as root on an ESXI host to produce backups (clones) of the running virtual machines.

Still a work in progress, but it is mostly functional.

'vmbkup' uses snapshots to enable cloning of running virtual machines.

Backups are stored in a primary/secondary fashion.  When the tool is run, the secondary location is purged and the primary is then moved to the secondary folder and new backups are placed into the primary folder ensuring that there are two backups available when the process completes.

## TODO 
- Add better error checking around the os level functions
- Add logging

