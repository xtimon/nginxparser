#!/usr/bin/env python3
import getopt
from operator import itemgetter
from os import path
from re import compile
from sys import argv, exit, stdout

# Using log format:
# log_format myformat '$remote_addr - [$time_local] "$host" "$request" '
#                     '$status ($bytes_sent) "$http_referer" '
#                     '"$uri $args" [$request_time]';

# Creation of a regular expression for the format used
log_format = '([\d.]+) \- \[(.+)\] "([\d.]+)" "(.+) (.+) .+" (\d{3}) \((\d+)\) "(.+)" "(.+) (.+)" \[([\d.]+)]'
line_re = compile(log_format)


def progress_bar(progress):
    stdout.write('\r[{}{}] {}%'.format('#' * progress, ' ' * (100-progress), progress))
    stdout.flush()


def analyze_log(logfile, outfile, time, count, exclude):
    summary = {'by_types': {'Overall': 0},
               'by_time': {'Overall': 0},
               'by_status': {}}
    if time or count:
        time_total = {}
        count_total = {}
    log_line_nu = 0
    lines_count = sum(1 for l in open(logfile))
    progress = 0
    percent = lines_count // 100
    for log_line in open(logfile, 'r'):
        log_line_nu += 1
        if lines_count >= 100000:
            if log_line_nu % percent == 0:
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

            if exclude and exclude in request:
                continue

# Creation the summary
# By types
            summary['by_types']['Overall'] += 1
            if request_type in summary['by_types'].keys():
                summary['by_types'][request_type] += 1
            else:
                summary['by_types'][request_type] = 1

# By time
            summary['by_time']['Overall'] += request_time
            if request_type in summary['by_time'].keys():
                summary['by_time'][request_type] += request_time
            else:
                summary['by_time'][request_type] = request_time

# By status
            if status in summary['by_status'].keys():
                summary['by_status'][status] += 1
            else:
                summary['by_status'][status] = 1

# Creation the total timing and the count report
            if time or count:
                if request in time_total.keys():
                    time_total[request] += request_time
                else:
                    time_total[request] = request_time
                if request in count_total.keys():
                    count_total[request] += 1
                else:
                    count_total[request] = 1

# Sort the summary dicts
    sorted_summary_by_types = sorted(summary['by_types'].items(), key=itemgetter(1), reverse=True)
    sorted_summary_by_time = sorted(summary['by_time'].items(), key=itemgetter(1), reverse=True)
    sorted_summary_by_status = sorted(summary['by_status'].items(), key=itemgetter(1), reverse=True)

# Print the summary
    print("\n= Summary {}".format("=" * 97))
    summary_by_types = '| Request types\t\t: '
    for k in sorted_summary_by_types:
        summary_by_types += "{}: {} ".format(k[0], k[1])
    print(summary_by_types)
    summary_by_time = '| Request timing\t: '
    for k in sorted_summary_by_time:
        summary_by_time += "{}: {} ".format(k[0], round(k[1], 2))
    print(summary_by_time)
    summary_by_status = '| Request statuses\t: '
    for k in sorted_summary_by_status:
        summary_by_status += "{}: {} ".format(k[0], k[1])
    print(summary_by_status)

# Sort and print the total timing report
    if time:
        sorted_time_total = sorted(time_total.items(), key=itemgetter(1), reverse=True)
        print("\n= The report, based on the total call time {}".format("=" * 64))
        print("|{0:>17}|{1:>20}|{2:>17}| {3:<}".\
              format("Calls", "Total time (sec)", "Resp. rate (s/c)", "URL pattern"))
        for e in sorted_time_total:
            print("|{0:>17}|{1:>20}|{2:>17}| {3:<}".\
                  format(count_total[e[0]], round(e[1], 2), round(e[1] / count_total[e[0]], 2), e[0]))

# Sort and print the count report
    if count:
        sorted_count_total = sorted(count_total.items(), key=itemgetter(1), reverse=True)
        print("\n= The report, based on the total number of queries {}".format("=" * 56))
        print("|{0:>17}|{1:>20}|{2:>17}| {3:<}".\
              format("Calls", "Total time (sec)", "Resp. rate (s/c)", "URL pattern"))
        for e in sorted_count_total:
            print("|{0:>17}|{1:>20}|{2:>17}| {3:<}".\
                  format(e[1], round(time_total[e[0]], 2), round(time_total[e[0]] / e[1], 2), e[0]))


def usage():
    print('''
Usage: ./nginx_parser.py [OPTION]... -l logfile.log
Mandatory arguments to long options are mandatory for short options too.
  -l, --logfile                 Log file for analysis
  -o, --outfile                 File to output reports (in developing)
  -t, --time                    Print the report, based on the total call time
  -c, --count                   Print the report, based on the total number of queries
  -e, --exclude                 The part of URL that are excluded from reporting
EXAMPLES:
  ./nginx_parser.py --count --logfile=/path/to/logfile.log
  ./nginx_parser.py -ct -e /static/ -l /path/to/logfile.log
    ''')


def main():
    try:
        opts, args = \
            getopt.getopt(argv[1:], "htcl:o:e:", ["help", "time", "count", "logfile=", "outfile=", "exclude="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        exit(2)
    time = False
    count = False
    exclude = ''
    logfile = None
    outfile = None
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            exit()
        elif o in ("-l", "--logfile"):
            logfile = a
        elif o in ("-o", "--output"):
            outfile = a
        elif o in ("-t", "--time"):
            time = True
        elif o in ("-c", "--count"):
            count = True
        elif o in ("-e", "--exclude"):
            exclude = a
        else:
            assert False, "unhandled option"
    if logfile:
        if path.isfile(logfile):
            analyze_log(logfile, outfile, time, count, exclude)
        else:
            print("It is not a file: {}".format(logfile))
            usage()
    else:
        usage()


if __name__ == "__main__":
    main()