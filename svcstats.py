#!/usr/bin/env python3
#
# Report IBM SVC/Storwize storage system performance statistics in CLI using SMI-S interface
#
# Requires Python 3 with 'pywbem' module
#
# Before running svcstats.py, enable statistic on SVC/Storwize system:
# svctask startstats -interval <1-60 minutes>
#
# 2017.09.28    v 1.0       Mikhail Zakharov <zmey20000@yahoo.com>
# 2017.10.02    v 1.0.1     Mikhail Zakharov <zmey20000@yahoo.com>  Volume output statistics fix
# 2018.01.09    v 1.0.1.1   Mikhail Zakharov <zmey20000@yahoo.com>  Code cleaning
# 2018.01.31    v 1.0.2.0   Mikhail Zakharov <zmey20000@yahoo.com>  Output format enhancements
# 2018.02.07    v 1.0.2.1   Mikhail Zakharov <zmey20000@yahoo.com>  Minor fixes and code decorations

# IBM SVC/Storwize CIM agent documentation:
# https://www.ibm.com/support/knowledgecenter/STPVGU/com.ibm.storage.svc.console.720.doc/svc_sdkintro_215ebp.html

# Used CIM Classes:
# System info - IBMTSSVC_Cluster
# Performance statistics - IBMTSSVC_NodeStatistics, IBMTSSVC_StorageVolumeStatistics,
# IBMTSSVC_BackendVolumeStatistics and IBMTSSVC_DiskDriveStatistics


import pywbem
import time
import sys
import getopt


query_language = 'DMTF:CQL'                     # CIM Query Language
# query_language = 'WQL'                        # WBEM Query Language

headers = {
    # Field names to request and headers to show
    'IBMTSSVC_Cluster': {
        'request': [
            # Fields we are requesting
            'ID', 'ElementName', 'CodeLevel', 'ConsoleIP', 'OtherIdentifyingInfo', 'Status', 'StatusDescriptions',
            'StatisticsFrequency', 'StatisticsStatus'
        ],
        'result': [
            # Headers we show in the result
            'ID', 'Name', 'CodeLevel', 'ConsoleIP', 'Model', 'Status', 'StatusDescriptions',
            'StatisticsFrequency', 'StatisticsStatus'
        ]
    },
    'IBMTSSVC_BackendVolumeStatistics': {
        'request': [
            'StatisticTime', 'InstanceID', 'KBytesRead', 'KBytesWritten', 'KBytesTransferred', 'ReadIOs', 'WriteIOs',
            'TotalIOs', 'ReadIOTimeCounter',  'WriteIOTimeCounter', 'IOTimeCounter'
        ],
        'result': ['Time', 'ID', 'rKB/s', 'wKB/s', 'tKB/s', 'rIO/s', 'wIO/s', 'tIO/s', 'ms/rIO', 'ms/wIO', 'ms/tIO']
    },
    'IBMTSSVC_DiskDriveStatistics': {
        # Suppose to be internal drives. General info only for now as I do not have internal drives to test.
        'request': [
            'StatisticTime', 'InstanceID', 'KBytesRead', 'KBytesWritten', 'KBytesTransferred',
            'ReadIOs', 'WriteIOs', 'TotalIOs'
        ],
        'result': ['Time', 'ID', 'rKB/s', 'wKB/s', 'tKB/s', 'rIO/s', 'wIO/s', 'tIO/s']
    },
    'IBMTSSVC_NodeStatistics': {
        'request': ['StatisticTime', 'InstanceID', 'ReadIOs', 'WriteIOs', 'TotalIOs', 'ReadHitIOs', 'WriteHitIOs'],
        'result': ['Time', 'ID', 'rIO/s', 'wIO/s', 'tIO/s', 'rHitIO/s', 'wHitIO/s']
    },
    'IBMTSSVC_StorageVolumeStatistics': {
        'request': [
            'StatisticTime', 'InstanceID', 'KBytesRead', 'KBytesWritten', 'KBytesTransferred', 'ReadIOs', 'WriteIOs',
            'TotalIOs', 'ReadIOTimeCounter', 'WriteIOTimeCounter', 'IOTimeCounter', 'ReadHitIOs', 'WriteHitIOs'
        ],
        'result': [
            'Time', 'ID', 'rKB/s', 'wKB/s', 'tKB/s', 'rIO/s', 'wIO/s', 'tIO/s', 'ms/rIO', 'ms/wIO', 'ms/tIO',
            'rHitIO/s', 'wHitIO/s'
        ]
    }
}

data = {
    # A structure for holding results data
    'IBMTSSVC_Cluster': {
        'current': [],
        'previous': [],
    },
    'IBMTSSVC_BackendVolumeStatistics': {
        'current': [],
        'previous': [],
        'delta': []
    },
    'IBMTSSVC_DiskDriveStatistics': {
        'current': [],
        'previous': [],
        'delta': []
    },
    'IBMTSSVC_NodeStatistics': {
        'current': [],
        'previous': [],
        'delta': []
    },
    'IBMTSSVC_StorageVolumeStatistics': {
        'current': [],
        'previous': [],
        'delta': []
    }
}

# Warning/error messages
nop_error = 'Error! You must specify all mandatory options to get data.'
frequency_warn = 'Warning! Sample frequency is invalid. Using frequency value from the storage system: {}.'


# CIM Classes description
#  System info: IBMTSSVC_Cluster
# Performance statistics: IBMTSSVC_NodeStatistics, IBMTSSVC_StorageVolumeStatistics,
# IBMTSSVC_BackendVolumeStatistics and IBMTSSVC_DiskDriveStatistics


def usage(err_code=1, err_text=''):
    if err_text:
        print(err_text, '\n', file=sys.stderr)

    print('Report IBM SVC/Storwize storage system performance statistics\n'
          '\n'
          'Usage:\n'
          '\tsvcstats.py -n|-v|-m|-d -a address -u user -p password [-f minutes] [-ht]\n'
          '\n'
          'Options:\n'
          '\t-n, -v, -m or -d\n'
          'Show nodes, vdisks, mdisks or drives performance statistics\n'
          '\t-a address -u user -p password\n'
          'Valid IP/DNS address, username and passwors to connect with IBM SVC/Storwize storage system\n'
          '\t[-f minutes]\n'
          'Optional report frequency interval. Must not be less then default "StatisticsFrequency" value\n'
          '\t[-h]\n'
          'Disable column headers\n'
          '\t[-t]\n'
          'Show report date/time creation timestamp on the storage system\n'
          )
    sys.exit(err_code)


def exit_prog(err_code=1, err_text=''):
    """Write a text and exit"""
    if err_text:
        print(err_text, '\n', file=sys.stderr)
    sys.exit(err_code)


def get_cmdopts():
    opts = ''
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'nvmda:u:p:f:ht')
    except getopt.GetoptError as err:
        usage(1, str(err))

    if not opts:
        usage(1, nop_error)

    # Defaults
    cim_class = ''
    target = ''
    user = ''
    password = ''
    frequency = 0                                            # Fetch RefreshInterval from the storage system
    skip_header = False
    skip_time = True

    for opt, arg in opts:
        if opt == '-n':
            cim_class = 'IBMTSSVC_NodeStatistics'
        elif opt == '-v':
            cim_class = 'IBMTSSVC_StorageVolumeStatistics'
        elif opt == '-m':
            cim_class = 'IBMTSSVC_BackendVolumeStatistics'
        elif opt == '-d':
            cim_class = 'IBMTSSVC_DiskDriveStatistics'
        elif opt == '-a':
            target = arg
        elif opt == '-u':
            user = arg
        elif opt == '-p':
            password = arg
        elif opt == '-f':                                   # frequency
            try:
                frequency = int(arg) * 60
            except ValueError:
                frequency = 0                                # Print warning later
        elif opt == '-h':
            skip_header = True
        elif opt == '-t':
            skip_time = False
        else:
            pass                                            # Unknown options are detected by getopt() exception above

    if not cim_class or not target or not user or not password:
        usage(1, nop_error)

    return {
        'cim_class': cim_class, 'target': target, 'user': user, 'password': password, 'frequency': frequency,
        'skip_header': skip_header, 'skip_time': skip_time
    }


def get_system(wbem_connection):
    """Get storage system general info to check if we can query the system. 'StatisticsFrequency' and
    'StatisticsStatus' are useful if we'd like to have performance collection parameters to be autodetected"""

    # Get field list
    fields = headers['IBMTSSVC_Cluster']['request']

    # Request useful fields only
    request = "SELECT " + ','.join(fields) + " FROM IBMTSSVC_Cluster"
    result = [headers['IBMTSSVC_Cluster']['result']]

    sys_info = wbem_connection.ExecQuery(query_language, request)
    if not sys_info:                                                # Nothing to report to
        return None

    for fld in sys_info:
        # Process fields explicitly as they have to be handled differently before adding them into the list.
        result.append(
            [
                fld.properties['ID'].value, fld.properties['ElementName'].value, fld.properties['CodeLevel'].value,
                fld.properties['ConsoleIP'].value, fld.properties['OtherIdentifyingInfo'].value[4],
                fld.properties['Status'].value, fld.properties['StatusDescriptions'].value[0],
                int(fld.properties['StatisticsFrequency'].value), bool(fld.properties['StatisticsStatus'].value)
            ]
        )

    return result


def datetime(dtstr):
    """Convert datetime into human readable form"""
    return time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(dtstr, '%Y%m%d%H%M%S'))


def get_stats(wbem_connection, cim_class, fields=(), inst_list=(), toint=True):
    """Get performance statistics for the 'cim_class'.
       Optional 'fields' argument specifies columns to retrieve, defaults are taken from headers[cim_class].
       Optional argument 'inst_list' is a filter to select desired instances."""

    flds = list(fields)
    if not flds:
        # Use default fields
        flds = headers[cim_class]['request']                              # Fields to request

    inst_filter = ''
    if inst_list:
        # Requesting selected only Instances
        inst_selectors = {
            'IBMTSSVC_BackendVolumeStatistics': 'BackendVolumeStats', 'IBMTSSVC_DiskDriveStatistics': 'DiskDriveStats',
            'IBMTSSVC_FCPortStatistics': 'FCPortStatistics', 'IBMTSSVC_NodeStatistics': 'NodeStats',
            'IBMTSSVC_StorageVolumeStatistics': 'StorageVolumeStats'
        }

        inst_filter_var = "' or InstanceID='" + inst_selectors[cim_class] + " "
        inst_filter = " WHERE InstanceID='" + inst_selectors[cim_class] + " " + \
                      inst_filter_var.join(str(inst) for inst in inst_list) + "'"

    # Form "select" request string
    request = "SELECT " + ','.join(flds) + " FROM " + cim_class + "{WHERE}".format(WHERE=inst_filter)

    # header will be the first member in the result
    result = [headers[cim_class]['result']]                                # Fields to be in the report header

    # Request WBEM
    stats = wbem_connection.ExecQuery(query_language, request)
    if not stats:
        return None                                                         # Nothing to report

    for stat in stats:
        # Handle 'InstanceID' and 'StatisticTime'
        if cim_class != 'IBMTSSVC_FCPortStatistics':
            ln = [
                datetime(str(stat.properties['StatisticTime'].value).split('.')[0]),    # 'StatisticTime'
                int(stat.properties['InstanceID'].value.split()[1])                     # 'InstanceID'
            ]
        else:
            # FCPortStatistics is different to everything else
            ln = [
                datetime(str(stat.properties['StatisticTime'].value).split('.')[0]),    # 'StatisticTime'
                str(stat.properties['InstanceID'].value.split()[1])                     # 'InstanceID'
            ]

        # Collect all the rest of the fields in a loop
        for fld in flds:
            if fld != 'InstanceID' and fld != 'StatisticTime':
                if cim_class == 'IBMTSSVC_FCPortStatistics' and fld == 'ElementName':
                    ports2nodes = stat.properties[fld].value.split()
                    ln.insert(2, int(ports2nodes[7]))                            # Node
                    ln.insert(3, int(ports2nodes[4]))                            # Port
                else:
                    if toint:
                        # We want data to be converted to integers. Very useful for performance statistics.
                        # Warning! Use it on numbers only!
                        ln.append(int(stat.properties[fld].value))
                    else:
                        # Save values as strings
                        ln.append(stat.properties[fld].value)
        result.append(ln)

    return result


def build_delta(cim_class, stats, sample_frequency):
    """Build relative performance data table based on absolute statistic values. 'index' column (default 0) contains
    unique IDs to be used as keys. Argument 'date' (column 1) is date/time of the sample. Performance data starts
    from default 'perf' (column 2). Row 'header' (default 0) is skipped, if needed set header=-1 to include line zero"""

    current = stats[cim_class]['current']
    previous = stats[cim_class]['previous']

    index = 1                                                   # ID aka index column
    date = 0                                                    # date/time column
    header = 0                                                  # header row
    perf = 2                                                    # performance columns start here

    # If we don't have previous data, return current
    if not previous:
        return current

    # Initialize delta with header
    result = [current[0]]

    for r in range(header + 1, len(current)):
        row = [
            current[r][date],                               # Date/time
            current[r][index],                              # Index aka ID aka Instance ID
        ]

        if current[r][date] == previous[r][date]:           # We are still in the same time interval!
            return None

        if current[r][index] == previous[r][index]:         # Subtract matrices if we have previous stats values ...
            for c in range(perf, len(current[0])):
                row.append(round(float(current[r][c] - previous[r][c]) / sample_frequency, 2))
        else:                                               # ... or pre-fill the row with current values only
            for c in range(perf, len(current[0])):
                row.append(current[r][c])

        if cim_class == 'IBMTSSVC_BackendVolumeStatistics' or cim_class == 'IBMTSSVC_StorageVolumeStatistics':
            # Response times calculation
            if row[8] and row[5]:
                row[8] = round(float(row[8] / row[5]), 2)                       # ms/rIO
            if row[9] and row[6]:
                row[9] = round(float(row[9] / row[6]), 2)                       # ms/wIO
            if row[10] and row[7]:
                row[10] = round(float(row[10] / row[7]), 2)                     # ms/tIO

        result.append(row)
    return result


def print_stats(stats, skip_header=False, skip_time=True):
    """Printout stats table"""

    # Header printout
    if not skip_header:
        r_header = ''
        if not skip_time:
            r_header = '{0:>19s}'.format(stats[0][0])               # Date/Time
        r_header += '{0:>6s}'.format(stats[0][1])                   # InstanceID
        for fld in stats[0][2:]:                                    # Add all the rest of the fields to the header
            r_header += '{0:>16s}'.format(fld)
        print(r_header)

    # Data printout
    for ln in stats[1:]:
        r_line = ''
        if not skip_time:
            r_line = '{0:19s}'.format(ln[0])                        # Date/Time
        r_line += '{0:6d}'.format(ln[1])                            # InstanceID

        # run through the rest of the fields:
        for fld in ln[2:]:
            r_line += '{0:16.2f}'.format(fld)

        print(r_line, flush=True)


# Main goes below
params = get_cmdopts()

# Establish connection
wbemc = pywbem.WBEMConnection('https://' + params['target'], (params['user'], params['password']),
                              'root/ibm',  no_verification=True)

data['IBMTSSVC_Cluster']['current'] = get_system(wbemc)
if not data:
    exit_prog(1, 'Error! There is no data for "IBMTSSVC_Cluster"!')

if not data['IBMTSSVC_Cluster']['current'][1][8]:
    exit_prog(0, 'Statistics is turned off on the storage system.\n'
                 'Enable it first: "svctask startstats -interval <1-60 minutes>"')

if int(params['frequency']) < data['IBMTSSVC_Cluster']['current'][1][7] * 60 or int(params['frequency']) > 3600:
    # 60 minutes <= frequency >= 'Statistics Interval' value on the storage system
    params['frequency'] = data['IBMTSSVC_Cluster']['current'][1][7] * 60
    print(frequency_warn.format(data['IBMTSSVC_Cluster']['current'][1][7]), file=sys.stderr)

while True:
    # Performance data processing loop
    data[params['cim_class']]['current'] = get_stats(wbemc, params['cim_class'])
    if not data[params['cim_class']]['current']:
        exit_prog(0, 'There is no data to collect for: "{}".'.format(params['cim_class']))

    delta = build_delta(params['cim_class'], data, params['frequency'])
    if delta:
        data[params['cim_class']]['delta'] = delta
        data[params['cim_class']]['previous'] = data[params['cim_class']]['current']

    print_stats(
        data[params['cim_class']]['delta'], skip_header=bool(params['skip_header']), skip_time=bool(params['skip_time'])
    )

    time.sleep(params['frequency'])
