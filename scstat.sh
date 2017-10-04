#!/bin/sh

# -----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# zmey20000@yahoo.com wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return Mikhail Zakharov
# -----------------------------------------------------------------------------

# Report IBM SVC/Storwize Cluster-level performance statistics in CSV using SSH

delim=","			# Main delimiter
fashion="../fashion/fashion"	# fashion SSH wrapper. Useful if you have 
				# passwords instead of keys for authentication
lssystemstats="lssystemstats -nohdr -delim $delim"
header="stat_name,stat_current,stat_peak,stat_peak_time"	# Header names
interval=1			# Default interval is 1 second

# ----------------------------------------------------------------------------- 
usage() {
    echo "Usage:"
    echo " scstat.sh <target> <user> <password> [interval]"
    exit 1
}

# ----------------------------------------------------------------------------- 
[ "$#" -gt 4 ] && usage

target="$1"
user="$2"
password="$3"
[ "$4" ] && interval="$4"

echo "$header"
while true
do
	# To use pure ssh with keys uncomment the line below and remark fashion
	#ssh "$user"@"$target""$lssystemstats"
	$fashion "$target" "$user" "$password" "$lssystemstats" 2>/dev/null
	sleep $interval
done
