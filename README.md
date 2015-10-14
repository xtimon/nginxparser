# nginx_parser
It works on python2.7 and python 3.*

usage: 

    nginx_parser.py [-h] --logfile LOGFILE [--outfile OUTFILE] [--time] [--count] [--exclude [EXCLUDE [EXCLUDE ...]]] [--status [STATUS [STATUS ...]]]

optional arguments:

    -h, --help            show this help message and exit
      --logfile LOGFILE, -l LOGFILE
                            Log file for analysis
      --outfile OUTFILE, -o OUTFILE
                            File to save the output reports
      --time, -t            Print the report based on the total call time
      --count, -c           Print the report based on the total number of queries
      --median, -m          Print the report based on a median duration of calls
      --exclude [EXCLUDE [EXCLUDE ...]], -e [EXCLUDE [EXCLUDE ...]]
                            The part of URL that are excluded from reporting
      --status [STATUS [STATUS ...]], -s [STATUS [STATUS ...]]
                            Print the report, based on the request status
      --debug, -d           Displays the count of unparsed lines and the unparsed
                            line numbers
              
   examples:

    ./nginx_parser.py -l /path/to/access_nginx.log -t -e /static /exclude
    ./nginx_parser.py -l /path/to/access_nginx.log -s 500 499 -o /path/to/outfile.txt
