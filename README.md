# nginx_parser
It works on python2.7 and python 3.*

Using log format:

    log_format myformat '$remote_addr - [$time_local] "$host" "$request" '
                        '$status ($bytes_sent) "$http_referer" '
                        '"$uri $args" [$request_time]';

usage: 

    usage: nginx_parser.py [-h] --logfile LOGFILE [--outfile OUTFILE]
                           [--exclude [EXCLUDE [EXCLUDE ...]]] [--time] [--count]
                           [--median] [--remote] [--status [STATUS [STATUS ...]]]
                           [--debug]

optional arguments:

      -h, --help            show this help message and exit
      --logfile LOGFILE, -l LOGFILE
                            Log file for analysis
      --outfile OUTFILE, -o OUTFILE
                            File to save the output reports
      --exclude [EXCLUDE [EXCLUDE ...]], -e [EXCLUDE [EXCLUDE ...]]
                            The part of URL that are excluded from reporting
      --time, -t            Print the report based on the total call time
      --count, -c           Print the report based on the total number of queries
      --median, -m          Print the report based on a median duration of calls
      --remote, -r          Print the report based on the number of calls from
                            remote hosts
      --status [STATUS [STATUS ...]], -s [STATUS [STATUS ...]]
                            Print the report, based on the request status
      --debug, -d           Displays the count of unparsed lines and the unparsed
                            line numbers
              
   examples:

    ./nginx_parser.py -l /path/to/access_nginx.log -t -e /static /exclude
    ./nginx_parser.py -l /path/to/access_nginx.log -s 500 499 -o /path/to/outfile.txt
    ./nginx_parser.py -l ../nginx_access.log -o ../test_all.txt -e /static /pull -tcmr -s 499 500
