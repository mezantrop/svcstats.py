# svcstats.py
Report IBM SVC/Storwize storage system performance statistics in CLI using SMI-S interface

Usage:
    svcstat.py -n|-v|-m|-d -a address -u user -p password [-f minutes] [-ht]

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
