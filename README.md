# svcstats.py / scstat.sh
## svcstats.py - Report IBM SVC/Storwize storage system performance statistics in CLI using SMI-S interface

* Requires Python 3 with 'pywbem' module
* Before running svcstats.py, enable statistic on SVC/Storwize system: ```svctask startstats -interval <1-60 minutes>```


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

## scstat.sh - Report IBM SVC/Storwize Cluster-level performance statistics using SSH
* Requires keys for SSH authorisation or use SSH wrapper
```
Usage:
 scstat.sh <target> <user>
```
