#!/usr/bin/env python3
import sys
from argparse import ArgumentParser
from operator import itemgetter
from os import path, popen
from re import compile

# Using log format:
# log_format myformat '$remote_addr - [$time_local] "$host" "$request" '
#                     '$status ($bytes_sent) "$http_referer" '
#                     '"$uri $args" [$request_time]';

# Creation of a regular expression for the format used
log_format = '([\d.]+) \- \[(.+)\] "([\d.]+)" "(.+) (.+) .+" (\d{3}) \((\d+)\) "(.+)" "(.+) (.+)" \[([\d.]+)]'
line_re = compile(log_format)


def progress_bar(progress):

    # The density of the progress bar
    density = 2

    # Getting the size of the console
    rows, columns = popen('stty size', 'r').read().split()
    if int(columns):
        density = int(round(120 / int(columns) + 0.5))
        if density == 0:
            density = 1
    sys.stdout.write('\r[{}{}] {}%'.
                     format('#' * (progress // density), ' ' * (100 // density - progress // density), progress))
    sys.stdout.flush()


def analyze_log(logfile, outfile, time, count, exclude, status_rep):
    summary = {'by_types': {'Overall': 0},
               'by_time': {'Overall': 0},
               'by_status': {}}
    if time or count:
        time_total = {}
        count_total = {}
    if status_rep:
        status_rep_count_dict = {}
        status_rep_time_dict = {}
        for s in status_rep:
            status_rep_count_dict[s] = {}
            status_rep_time_dict[s] = {}
    lines_count = sum(1 for l in open(logfile))
    percent = lines_count // 100
    progress = 0
    log_line_nu = 0
    for log_line in open(logfile, 'r'):
        log_line_nu += 1
        if lines_count >= 100000:
            if log_line_nu % percent == 0:
                progress += 1
                progress_bar(progress)
        line_opts = line_re.findall(log_line)
        if line_opts:

            # Get the values from a line
            # remote_addr = line_opts[0][0]
            # time_local =line_opts[0][1]
            # host = line_opts[0][2]
            request_type = line_opts[0][3]
            request = line_opts[0][4]
            status = line_opts[0][5]
            # bytes_sent = line_opts[0][6]
            # http_refferer = line_opts[0][7]
            # uri = line_opts[0][8]
            # args = line_opts[0][9]
            request_time = float(line_opts[0][10])

            stop = False
            if exclude:
                for e in exclude:
                    if e in request:
                        stop = True
                        break
            if stop:
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

            # Creation the report, based on the request status
            if status_rep:
                for s in status_rep:
                    if s == status:
                        if request in status_rep_count_dict[s].keys():
                            status_rep_count_dict[s][request] += 1
                        else:
                            status_rep_count_dict[s][request] = 1
                        if request in status_rep_time_dict[s].keys():
                            status_rep_time_dict[s][request] += request_time
                        else:
                            status_rep_time_dict[s][request] = request_time

    # Redirect out to the file
    if outfile:
        print('\nReports are stored in this file: {}'.format(outfile))
        sys.stdout = open(outfile, 'w')

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
        print("|{0:>17}|{1:>20}|{2:>17}| {3:<}".
              format("Calls", "Total time (sec)", "Resp. rate (s/c)", "URL pattern"))
        for e in sorted_time_total:
            print("|{0:>17}|{1:>20}|{2:>17}| {3:<}".
                  format(count_total[e[0]], round(e[1], 2), round(e[1] / count_total[e[0]], 2), e[0]))

    # Sort and print the count report
    if count:
        sorted_count_total = sorted(count_total.items(), key=itemgetter(1), reverse=True)
        print("\n= The report, based on the total number of queries {}".format("=" * 56))
        print("|{0:>17}|{1:>20}|{2:>17}| {3:<}".
              format("Calls", "Total time (sec)", "Resp. rate (s/c)", "URL pattern"))
        for e in sorted_count_total:
            print("|{0:>17}|{1:>20}|{2:>17}| {3:<}".
                  format(e[1], round(time_total[e[0]], 2), round(time_total[e[0]] / e[1], 2), e[0]))

    # Sort and print the reports, based on the request status
    if status_rep:
        for s in status_rep:
            sorted_status_rep = sorted(status_rep_count_dict[s].items(), key=itemgetter(1), reverse=True)
            print("\n= The report, based on the request status = {} {}".format(s, "=" * 59))
            print("|{0:>17}|{1:>20}|{2:>17}| {3:<}".
                  format("Calls", "Total time (sec)", "Resp. rate (s/c)", "URL pattern"))
            for e in sorted_status_rep:
                print("|{0:>17}|{1:>20}|{2:>17}| {3:<}".
                      format(e[1], round(status_rep_time_dict[s][e[0]], 2),
                             round(status_rep_time_dict[s][e[0]] / e[1], 2), e[0]))


def main():
    parser = ArgumentParser()
    parser.add_argument('--logfile', '-l', action='store',
                        help='Log file for analysis', required=True)
    parser.add_argument('--outfile', '-o', action='store',
                        help='File to save the output reports')
    parser.add_argument('--time', '-t', action='count',
                        help='Print the report, based on the total call time')
    parser.add_argument('--count', '-c', action='count',
                        help='Print the report, based on the total number of queries')
    parser.add_argument('--exclude', '-e', action='store', nargs='*',
                        help='The part of URL that are excluded from reporting')
    parser.add_argument('--status', '-s', action='store', nargs='*',
                        help='Print the report, based on the request status')
    args = parser.parse_args()
    if path.isfile(args.logfile):
        analyze_log(args.logfile, args.outfile, args.time, args.count, args.exclude, args.status)
    else:
        print("This is not a file: {}".format(args.logfile))


if __name__ == "__main__":
    main()