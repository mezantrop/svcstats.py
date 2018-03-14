#!/usr/bin/env python3

# Report IBM SVC/Storwize Cluster-level performance statistics using SSH

# Requires Python 3 with 'paramiko' module

# 2017.10.04    v 1.0.0   Mikhail Zakharov <zmey20000@yahoo.com>    Initial release
# 2017.01.30    v 1.0.1   Mikhail Zakharov <zmey20000@yahoo.com>    Time formatting


import sys
import paramiko
import time
import getopt

frequency = 5                                               # Report frequency interval: 1 to 60 seconds. Default is 5.
delimiter_svc = ','                                         # Delimiter for the storage system interaction
delimiter_csv = ','                                         # Delimiter we want to see in CSV output
sample_count = 1000000000                                   # The number of samples we are interested in
skip_zero = True                                            # Set 'False' here to show lines with zero values
out_format = 'stat'                                         # Default output format is 'stat'. We support CSV as well.
# out_format = 'csv'
output_formats = ('stat', 'csv')                            # Supported output formats

header = ['stat_name', 'stat_current', 'stat_peak', 'stat_peak_time']   # Change this if you want to customize a header

# Error and warning definitions
nop_error = 'Error! You must specify all mandatory options to get data.'
frequency_error = 'Error! Wrong frequency interval. Use 1 to 60 seconds.'
count_error = 'Error! Wrong [-s count] value.'
outformat_error = 'Error! Wrong output format specified.'


def usage(err_code=1, err_text=''):
    if err_text:
        print(err_text, '\n', file=sys.stderr)

    print('Report IBM SVC/Storwize Cluster-level performance statistics\n'
          '\n'
          'Usage:\n'
          '\tscstat_ssh.py -a address -u user -p password [-f seconds][-s count][-o stat|csv][-z]\n'
          '\n'
          'Options:\n'
          '\t-a address -u user -p password\n'
          'Valid IP/DNS address, username and password to connect with IBM SVC/Storwize storage system\n'
          '\t[-f seconds]\n'
          'Report frequency interval: 1 to 60 seconds. Default is 5\n'
          '\t[-s count]\n'
          'Stop statistic collection after "count" times and exit\n'   
          '\t[-o stat|csv]\n'
          'Output format style. Default is "stat"\n'
          '\t[-z]\n'
          'Show lines with zero values\n')
    sys.exit(err_code)


def ssh_exec(command, target, user, password, port=22):
    """Execute a command via SSH and read results"""

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(target, username=user, password=password, port=port)
    except:
        print('Error: {user}@{targ}: Target is inaccessible:'.format(user=user, targ=target), sys.exc_info()[1])
        sys.exit(1)

    stdin, stdout, stderr = client.exec_command(command)

    error = stderr.read()
    if error:
        error = error.decode('US-ASCII')
        print('Error: {user}@{targ}: "{cmd}" returned: {err}'.format(user=user, targ=target, cmd=command, err=error))
        client.close()
        sys.exit(1)

    data = stdout.read()
    client.close()

    try:
        data = data.decode('UTF-8')
    except UnicodeDecodeError:
        data = data.decode('US-ASCII')

    return data


try:
    opts, args = getopt.getopt(sys.argv[1:], 'a:u:p:f:s:o:z')
except getopt.GetoptError as err:
    usage(1, str(err))

if not opts:
    usage(1, nop_error)

for opt, arg in opts:
    if opt == '-a':
        target = arg
    elif opt == '-u':
        user = arg
    elif opt == '-p':
        password = arg
    elif opt == '-f':                                   # frequency
        try:
            frequency = int(arg)
        except ValueError or frequency > 60 or frequency < 1:
            usage(1, frequency_error)
    elif opt == '-s':                                   # Sample count
        try:
            sample_count = int(arg)
        except ValueError:
            usage(1, count_error)
    elif opt == '-z':                                   # How to deal with zeroes
        skip_zero = False
    elif opt == '-o':
        if arg in output_formats:
            out_format = arg
        else:
            usage(1, outformat_error)
    else:
        pass                                            # Unknown options are detected by getopt() exception above

if out_format == 'csv':
    # Write header once only
    print(delimiter_csv.join(header))

while True:
    if out_format != 'csv':
        # Clear screen and move cursor to the upper left corner
        sys.stdout.write("\x1b[2J\x1b[H")

    stats_raw = ssh_exec('lssystemstats -delim {}'.format(delimiter_svc), target, user, password)

    if out_format == 'stat':
        # Write header for each sample
        print('{0:19s}{1:>12s}{2:>12s}{3:>18s}'.format(header[0], header[1], header[2], header[3]))

    for ln in stats_raw.split('\n')[1:]:
        if ln:
            stats = ln.split(delimiter_svc)
            if skip_zero and stats[1] == '0' and stats[2] == '0':
                pass
            else:
                if out_format == 'csv':
                    # We want CSV format
                    print(delimiter_csv.join(stats), flush=True)
                else:
                    # We want nice stat format
                    peak_time = time.strftime('%y-%m-%d %H:%M:%S', time.strptime(stats[3], '%y%m%d%H%M%S'))
                    print('{0:19s}{1:>12s}{2:>12s}{3:>18s}'.format(stats[0], stats[1], stats[2], peak_time), flush=True)

    sample_count -= 1
    if not sample_count:
        sys.exit(0)

    time.sleep(frequency)
