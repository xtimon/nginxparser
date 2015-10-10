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

def analyze_log(logfile, base, outfile):
    f = open(logfile, 'r')
    for log_line in f:
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
            request_time = line_opts[0][10]
#


    f.close()

def usage():
    print("Usage info")

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hbl:o:", ["help", "base", "logfile=", "outfile="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    base = False
    logfile = None
    outfile = None
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-l", "--logfile"):
            logfile = a
        elif o in ("-b", "--base"):
            base = True
        elif o in ("-o", "--output"):
            outfile = a
        else:
            assert False, "unhandled option"
#    print(opts, args)
    analyze_log(logfile, base, outfile)

if __name__ == "__main__":
    main()

