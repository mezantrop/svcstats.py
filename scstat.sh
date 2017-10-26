#!/bin/sh

# -----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# zmey20000@yahoo.com wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return Mikhail Zakharov
# -----------------------------------------------------------------------------

# Report IBM SVC/Storwize Cluster-level performance statistics in CSV using SSH

# 2017.10.04	v1.0	Mikhail Zakharov <zmey20000@yahoo.com>	Initial
# 2017.10.26	v1.1	Mikhail Zakharov <zmey20000@yahoo.com>	Simplification


delim=","					# Delimiter
interval=1					# Interval
# Command:
lsss="while true; do lssystemstats -nohdr -delim $delim; sleep $interval; done"
# Header:
header="stat_name"$delim"stat_current$delim"stat_peak$delim"stat_peak_time"

# ----------------------------------------------------------------------------- 
usage() {
    echo "Usage:"
    echo " scstat.sh <user> <target>"
    exit 1
}

# ----------------------------------------------------------------------------- 
[ "$#" -ne 2 ] && usage

echo "$header"
ssh "$1"@"$2" "$lsss"
