#!/bin/bash

# -----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# zmey20000@yahoo.com wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return Mikhail Zakharov
# -----------------------------------------------------------------------------

#
# An example script to feed RRD database with IBM SVC/Storwize Controller level statistics
# and create some simple HTML report
#

# 2018.03.14    v 1.0.0   Mikhail Zakharov <zmey20000@yahoo.com>	Initial release

# To check if the script works, run it from your shell like below: 
#	while true; do date; ./2rrd_scstat-controller.sh; sleep 60; done
# To get permanet statistic updates, add the script to cron.


# Change variables below:
address="ibm-svc-storage-system"
user="username"
password="TopSecret1!"

# Performance metrics to work with (one per line):
perf_metrics="compression_cpu_pc
cpu_pc
fc_io
fc_mb
mdisk_io
mdisk_mb
mdisk_ms
mdisk_r_io
mdisk_r_mb
mdisk_r_ms
mdisk_w_io
mdisk_w_mb
mdisk_w_ms
total_cache_pc
vdisk_io
vdisk_mb
vdisk_ms
vdisk_r_io
vdisk_r_mb
vdisk_r_ms
vdisk_w_io
vdisk_w_mb
vdisk_w_ms
write_cache_pc"

interval=60																# Update interval in seconds

basedir="/path/to/svcstat/2rrd"												# Directories and files
svcstat=${basedir}/"scstat_ssh.py"
python=${basedir}/"venv/bin/python3"

rrd_tool="/usr/bin/rrdtool"
rrd_dir=${basedir}/"rrd"
rrd_storage=${address}													# Or give it your name
rrd_item="Controller"
rrd_file=${rrd_dir}/${rrd_storage}-${rrd_item}.rrd						# RRD datamase is here

html_file=${rrd_dir}/${rrd_storage}-${rrd_item}.html					# Resulted HTML filename


# -- RRD Magic goes below ----------------------------------------------------------------------------------------------
dinterval=$(expr $interval '*' 2)										# Double interval in seconds

if [ ! -f ${rrd_file} ]; then											# Create RRD if there is no db
	# Build the list of metrics to create in the RRD
	rrd_metrics=$(for m in $perf_metrics; do
		printf "DS:${m}:GAUGE:${dinterval}:U:U\n"
	done | sort)

	# RRD params: 
	#	1440 = 24 hours with 1 minutes resolution
	#	288 = 48 hours, 10 minute averages (1 * 10 * 288 / 60)
	#	336 = 7 days, 30 minute averages (1 * 30 * 336 / 60 / 24)
	${rrd_tool} create ${rrd_file} \
		--step ${interval} --start 1417983679 \
		${rrd_metrics} \
		RRA:AVERAGE:0.5:1:1440 \
		RRA:AVERAGE:0.5:10:288 \
		RRA:AVERAGE:0.5:30:336
fi

# A bit ugly way to collect (strip/filter/parse/format) current pefrormance values of the Controller
perf_values=$(${python} ${svcstat} -a ${address} -u ${user} -p ${password} -s 1 -z -o csv | 
	grep --fixed-strings "$perf_metrics" | sort | cut -d , -f 2 | xargs | tr ' ' ':')

# Update the RRD database with the collected values
${rrd_tool} update ${rrd_file} N:${perf_values}


# -- Create graphics ---------------------------------------------------------------------------------------------------

# CPU/Cache utilization
rrdtool graph ${rrd_dir}/${rrd_storage}-${rrd_item}-resources.png --lazy --slope-mode \
	--title "${rrd_storage} - ${rrd_item} - Resource usage, %" \
	--rigid --lower-limit 0 --upper-limit 100 \
	DEF:cpu_pc=${rrd_file}:cpu_pc:AVERAGE LINE1:cpu_pc#FF0000:"Main CPU" \
	DEF:comp_cpu_pc=${rrd_file}:compression_cpu_pc:AVERAGE LINE1:comp_cpu_pc#0000FF:"Compression CPU" \
	DEF:w_cache=${rrd_file}:write_cache_pc:AVERAGE LINE1:w_cache#00FF00:"Write Cache" \
	DEF:t_cache=${rrd_file}:total_cache_pc:AVERAGE LINE1:t_cache#00FFFF:"Total Cache" > /dev/null

# Mdisk IO
rrdtool graph ${rrd_dir}/${rrd_storage}-${rrd_item}-mdisk_io.png --lazy --slope-mode \
	--title "${rrd_storage} - ${rrd_item} - Mdisk IOPS" \
	DEF:mdisk_r_io=${rrd_file}:mdisk_r_io:AVERAGE LINE1:mdisk_r_io#FF0000:"Mdisk Read" \
	DEF:mdisk_w_io=${rrd_file}:mdisk_w_io:AVERAGE LINE1:mdisk_w_io#0000FF:"Mdisk Write" \
	DEF:mdisk_io=${rrd_file}:mdisk_io:AVERAGE LINE1:mdisk_io#00FF00:"Mdisk Total" > /dev/null

# Mdisk Throuhput
rrdtool graph ${rrd_dir}/${rrd_storage}-${rrd_item}-mdisk_mb.png --lazy --slope-mode \
	--title "${rrd_storage} - ${rrd_item} - Mdisk Throuhput, Mb" \
	DEF:mdisk_r_mb=${rrd_file}:mdisk_r_mb:AVERAGE LINE1:mdisk_r_mb#FF0000:"Mdisk Read" \
	DEF:mdisk_w_mb=${rrd_file}:mdisk_w_mb:AVERAGE LINE1:mdisk_w_mb#0000FF:"Mdisk Write" \
	DEF:mdisk_mb=${rrd_file}:mdisk_mb:AVERAGE LINE1:mdisk_mb#00FF00:"Mdisk Total" > /dev/null

# Mdisk Response
rrdtool graph ${rrd_dir}/${rrd_storage}-${rrd_item}-mdisk_ms.png --lazy --slope-mode \
	--title "${rrd_storage} - ${rrd_item} - Mdisk Response, ms" \
	DEF:mdisk_r_ms=${rrd_file}:mdisk_r_ms:AVERAGE LINE1:mdisk_r_ms#FF0000:"Mdisk Read" \
	DEF:mdisk_w_ms=${rrd_file}:mdisk_w_ms:AVERAGE LINE1:mdisk_w_ms#0000FF:"Mdisk Write" \
	DEF:mdisk_ms=${rrd_file}:mdisk_ms:AVERAGE LINE1:mdisk_ms#00FF00:"Mdisk Total" > /dev/null

# Vdisk IO
rrdtool graph ${rrd_dir}/${rrd_storage}-${rrd_item}-vdisk_io.png --lazy --slope-mode \
	--title "${rrd_storage} - ${rrd_item} - Vdisk IOPS" \
	DEF:vdisk_r_io=${rrd_file}:vdisk_r_io:AVERAGE LINE1:vdisk_r_io#FF0000:"Vdisk Read" \
	DEF:vdisk_w_io=${rrd_file}:vdisk_w_io:AVERAGE LINE1:vdisk_w_io#0000FF:"Vdisk Write" \
	DEF:vdisk_io=${rrd_file}:vdisk_io:AVERAGE LINE1:vdisk_io#00FF00:"Vdisk Total" > /dev/null

# Vdisk Throuhput
rrdtool graph ${rrd_dir}/${rrd_storage}-${rrd_item}-vdisk_mb.png --lazy --slope-mode \
	--title "${rrd_storage} - ${rrd_item} - Vdisk Throuhput, Mb" \
	DEF:vdisk_r_mb=${rrd_file}:vdisk_r_mb:AVERAGE LINE1:vdisk_r_mb#FF0000:"Vdisk Read" \
	DEF:vdisk_w_mb=${rrd_file}:vdisk_w_mb:AVERAGE LINE1:vdisk_w_mb#0000FF:"Vdisk Write" \
	DEF:vdisk_mb=${rrd_file}:vdisk_mb:AVERAGE LINE1:vdisk_mb#00FF00:"Vdisk Total" > /dev/null

# Vdisk Response
rrdtool graph ${rrd_dir}/${rrd_storage}-${rrd_item}-vdisk_ms.png --lazy --slope-mode \
	--title "${rrd_storage} - ${rrd_item} - Vdisk Response, ms" \
	DEF:vdisk_r_ms=${rrd_file}:vdisk_r_ms:AVERAGE LINE1:vdisk_r_ms#FF0000:"Vdisk Read" \
	DEF:vdisk_w_ms=${rrd_file}:vdisk_w_ms:AVERAGE LINE1:vdisk_w_ms#0000FF:"Vdisk Write" \
	DEF:vdisk_ms=${rrd_file}:vdisk_ms:AVERAGE LINE1:vdisk_ms#00FF00:"Vdisk Total" > /dev/null

# FC IO
rrdtool graph ${rrd_dir}/${rrd_storage}-${rrd_item}-fc_io.png --lazy --slope-mode \
	--title "${rrd_storage} - ${rrd_item} - FC IOPS" \
	DEF:fc_io=${rrd_file}:fc_io:AVERAGE LINE1:fc_io#FF0000:"FC IOPS" > /dev/null

# FC MB
rrdtool graph ${rrd_dir}/${rrd_storage}-${rrd_item}-fc_mb.png --lazy --slope-mode \
	--title "${rrd_storage} - ${rrd_item} - FC Throughput, Mb" \
	DEF:fc_mb=${rrd_file}:fc_mb:AVERAGE LINE1:fc_mb#FF0000:"FC Mb" > /dev/null

# -- HTML Generation ---------------------------------------------------------------------------------------------------
[ ! -f ${html_file} ] && echo '<!DOCTYPE html>
<html>
	<head>
		<link rel="stylesheet" type="text/css" href="2rrd.css">
		<meta http-equiv="refresh" content="300">
	</head>

	<body>
		<div class="header">
			<div class="cheader">
				'${rrd_storage} - ${rrd_item} - Daily performance statistics'
			</div>
		</div>

		<div class="igallery">
		
			<div class="gallery">
				<a target="_blank" href="'${rrd_dir}/${rrd_storage}-${rrd_item}-resources.png'">
					<img src="'${rrd_dir}/${rrd_storage}-${rrd_item}-resources.png'" alt="Throughput">
				</a>
			</div>

			<div class="gallery">
				<a target="_blank" href="'${rrd_dir}/${rrd_storage}-${rrd_item}-mdisk_io.png'">
					<img src="'${rrd_dir}/${rrd_storage}-${rrd_item}-mdisk_io.png'" alt="IOPS">
				</a>
			</div>

			<div class="gallery">
				<a target="_blank" href="'${rrd_dir}/${rrd_storage}-${rrd_item}-mdisk_mb.png'">
					<img src="'${rrd_dir}/${rrd_storage}-${rrd_item}-mdisk_mb.png'" alt="Latency">
				</a>
			</div>

			<div class="gallery">
				<a target="_blank" href="'${rrd_dir}/${rrd_storage}-${rrd_item}-mdisk_ms.png'">
					<img src="'${rrd_dir}/${rrd_storage}-${rrd_item}-mdisk_ms.png'" alt="Latency">
				</a>
			</div>

			<div class="gallery">
				<a target="_blank" href="'${rrd_dir}/${rrd_storage}-${rrd_item}-vdisk_io.png'">
					<img src="'${rrd_dir}/${rrd_storage}-${rrd_item}-vdisk_io.png'" alt="Latency">
				</a>
			</div>

			<div class="gallery">
				<a target="_blank" href="'${rrd_dir}/${rrd_storage}-${rrd_item}-vdisk_mb.png'">
					<img src="'${rrd_dir}/${rrd_storage}-${rrd_item}-vdisk_mb.png'" alt="Latency">
				</a>
			</div>

			<div class="gallery">
				<a target="_blank" href="'${rrd_dir}/${rrd_storage}-${rrd_item}-vdisk_ms.png'">
					<img src="'${rrd_dir}/${rrd_storage}-${rrd_item}-vdisk_ms.png'" alt="Latency">
				</a>
			</div>

			<div class="gallery">
				<a target="_blank" href="'${rrd_dir}/${rrd_storage}-${rrd_item}-fc_io.png'">
					<img src="'${rrd_dir}/${rrd_storage}-${rrd_item}-fc_io.png'" alt="Latency">
				</a>
			</div>

			<div class="gallery">
				<a target="_blank" href="'${rrd_dir}/${rrd_storage}-${rrd_item}-fc_mb.png'">
					<img src="'${rrd_dir}/${rrd_storage}-${rrd_item}-fc_mb.png'" alt="Latency">
				</a>
			</div>

		</div>

		<div class="footer">
			<div class="rfooter">Generated on: '$(date)'</div>
		</div>
	</body>
</html>' > ${html_file}
