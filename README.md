# Warning! This project has been migrated to GitLab with the same name
# svcstats.py

<a href="https://www.buymeacoffee.com/mezantrop" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>

## svcstats.py - Report IBM SVC/Storwize storage system performance statistics for nodes, vdisks, mdisks or drives in CLI using SMI-S interface

## Installation

Download all files, then run:
```python3 setup.py install```

### Virtual environment installation
In order not to modify system python3 environment, you may consider virtual environment.
```
mkdir svcstats
cd svcstats
# Copy all svcstats.py files into svcstats directory
python3 -m venv venv
source venv/bin/activate
(venv) python3 setup.py install
```

If you have installed **svcstats.py** into a virtual environment, do not forget to activate it with "source /path/to/venv/bin/activate" command, for each session you are running **svcstats.py**.


* Requires Python 3 with 'pywbem' module
* Before running **svcstats.py**, enable statistic on SVC/Storwize system: ```svctask startstats -interval <1-60 minutes>```


```
Usage:
    svcstats.py -n|-v|-m|-d -a address -u user -p password [-f minutes] [-ht]

Options:
    -n, -v, -m or -d
option -q not recognized 
Show nodes, vdisks, mdisks or drives performance statistics.

    -a address -u user -p password
Valid IP/DNS address, username and passwors to connect with IBM SVC/Storwize storage system
    [-f minutes]
Optional report frequency interval. Must not be less then default "StatisticsFrequency" value.
    [-h]
Disable column headers.
    [-t]
Show report date/time creation timestamp on the storage system
```

[IBM SVC/Storwize CIM agent documentation](https://www.ibm.com/support/knowledgecenter/STPVGU/com.ibm.storage.svc.console.720.doc/svc_sdkintro_215ebp.html)

## scstat_ssh.py - Report IBM SVC/Storwize Cluster-level performance statistics using SSH

Requires:
* Python 3 
* paramiko module

```
Usage:
	scstat_ssh.py -a address -u user -p password [-f seconds][-s count][-o stat|csv][-z]

Options:
	-a address -u user -p password
Valid IP/DNS address, username and password to connect with IBM SVC/Storwize storage system
	[-f seconds]
Report frequency interval: 1 to 60 seconds. Default is 5
	[-s count]
Stop statistic collection after "count" times and exit
	[-o stat|csv]
Output format style. Default is "stat"
	[-z]
Show lines with zero values
```

## scstat.sh - Report IBM SVC/Storwize Cluster-level performance statistics using SSH (light version)
* Requires keys for SSH authorisation or use SSH wrapper
```
Usage:
 scstat.sh <user> <target>
```

## 2rrd/2rrd_scstat-controller.sh
An example script to feed RRD database with IBM SVC/Storwize Controller level statistics and create a simple HTML report
