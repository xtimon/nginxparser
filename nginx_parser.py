#!/usr/bin/env python3
import getopt, re, sys

# Using log format:
# log_format myformat '$remote_addr - [$time_local] "$host" "$request" '
#                     '$status ($bytes_sent) "$http_referer" '
#                     '"$uri $args" [$request_time]';

# Creation of a regular expression for the format used
log_format = \
    '([\d.]+) \- \[(.+)\] "([\d.]+)" "(.+) (.+) .+" (\d{3}) \((\d+)\) "(.+)" "(.+) (.+)" \[([\d.]+)]'
line_re = re.compile(log_format)

def progress_bar(progress):
    sys.stdout.write('\r[{0}] {1}%'.format('#'*(progress), progress))

def analyze_log(logfile, outfile, time):
    summary = {'by_types': {'Overall': 0},
               'by_time': {'Overall': 0},
               'by_status':{}}
    log_line_nu = 0
    progress = 0
    lines_count = sum(1 for l in open(logfile))
    for log_line in open(logfile, 'r'):
        log_line_nu += 1
        if log_line_nu % (lines_count // 100) == 0:
            progress += 1
            progress_bar(progress)
        line_opts = line_re.findall(log_line)
        if line_opts:
# Get the values from a line
            remote_addr = line_opts[0][0]
            time_local =line_opts[0][1]
            host = line_opts[0][2]
            request_type = line_opts[0][3]
            request = line_opts[0][4]
            status = line_opts[0][5]
            bytes_sent = line_opts[0][6]
            http_refferer = line_opts[0][7]
            uri = line_opts[0][8]
            args = line_opts[0][9]
            request_time = float(line_opts[0][10])
# Creation summary
# By types
            summary['by_types']['Overall'] += 1
            if request_type in summary['by_types'].keys():
                summary['by_types'][request_type] += 1
            else: summary['by_types'][request_type] = 1
# By time
            summary['by_time']['Overall'] += request_time
            if request_type in summary['by_time'].keys():
                summary['by_time'][request_type] += request_time
            else: summary['by_time'][request_type] = request_time
# By status
            if status in summary['by_status'].keys():
                summary['by_status'][status] += 1
            else: summary['by_status'][status] = 1
    print(summary)

def usage():
    print("Usage info")

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "htl:o:", ["help", "time", "logfile=", "outfile="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    time = False
    logfile = None
    outfile = None
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-l", "--logfile"):
            logfile = a
        elif o in ("-o", "--output"):
            outfile = a
        elif o in ("-t", "--time"):
            time = True
        else:
            assert False, "unhandled option"
    if logfile:
        analyze_log(logfile, outfile, time)
    else:
        usage()
        sys.exit()

if __name__ == "__main__":
    main()