# nginx_parser
##It works on python2.7 and python 3.*

###Caution in this version of the log format is changed!
###Added $upstream_response_time.
###All reports are based on this value.
###Also added the report is based on the difference between $request_time and $upstream_response_time.

Installation:

    pip install nginxparser

Using log format:

    log_format myformat '$remote_addr - [$time_local] "$host" "$request" '
                        '$status ($bytes_sent) "$http_referer" '
                        '"$uri $args" [$request_time] [$upstream_response_time]';

usage: 

    usage: nginxparser [-h] --logfile LOGFILE [--outfile OUTFILE]
                   [--period PERIOD PERIOD]
                   [--exclude [EXCLUDE [EXCLUDE ...]]] [--time] [--count]
                   [--median] [--status [STATUS [STATUS ...]]] [--remote]
                   [--difference DIFFERENCE] [--limit LIMIT] [--debug]

optional arguments:

      -h, --help            show this help message and exit
      --logfile LOGFILE, -l LOGFILE
                            Log file for analysis
      --outfile OUTFILE, -o OUTFILE
                            File to save the output reports
      --period PERIOD PERIOD, -p PERIOD PERIOD
                            Specify the period for which you need to make reports.
                            Using format: Y.m.d_H:M:S. Example: --period
                            2015.10.19_00:00:00 2015.10.20_00:00:00
      --exclude [EXCLUDE [EXCLUDE ...]], -e [EXCLUDE [EXCLUDE ...]]
                            The part of URL that are excluded from reporting
      --time, -t            Print the report based on the total call time
      --count, -c           Print the report based on the total number of queries
      --median, -m          Print the report based on a median duration of calls
      --remote, -r          Print the report based on the number of calls from
                            remote hosts
      --difference DIFFERENCE, -d DIFFERENCE
                            Print the report is based on the difference between
                            $request_time and $upstream_response_time. It
                            specifies the minimum difference, in seconds, for the
                            registration of the request. Example -d 0.5
      --status [STATUS [STATUS ...]], -s [STATUS [STATUS ...]]
                            Print the report, based on the request status
      --limit LIMIT, -L LIMIT
                            Limit the output reports. Default 100.
      --debug, -D           Displays the count of unparsed lines and the unparsed
                            line numbers
              
examples:

    nginxparser -l /path/to/access_nginx.log -t -e /static /exclude
    nginxparser -l /path/to/access_nginx.log -s 500 499 -o /path/to/outfile.txt
    nginxparser -l ../nginx_access.log -o ../test_all.txt -e /static /pull -tcmrS -s 499 500 -p 2015.10.06_00:00:00 2015.10.07_00:00:00
