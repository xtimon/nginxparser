nginx_parser
^^^^^^^^^^^^

************************************
It works on python2.7 and python 3.*
************************************

Using log format:
=================

log_format myformat '$remote_addr - [$time_local] "$host" "$request" $status ($bytes_sent) "$http_referer" "$uri $args" [$request_time]';

usage:
======

usage: nginxparser [-h] --logfile LOGFILE [--outfile OUTFILE] [--exclude [EXCLUDE [EXCLUDE ...]]] [--time] [--count] [--median] [--remote] [--status [STATUS [STATUS ...]]] [--limit LIMIT] [--debug]

optional arguments:
===================

-h, --help            show this help message and exit

--logfile LOGFILE, -l LOGFILE Log file for analysis

--outfile OUTFILE, -o OUTFILE File to save the output reports

--period PERIOD PERIOD, -p PERIOD PERIOD Specify the period for which you need to make reports. Using format: Y.m.d_H:M:S. Example: --period 2015.10.19_00:00:00 2015.10.20_00:00:00

--exclude [EXCLUDE [EXCLUDE ...]], -e [EXCLUDE [EXCLUDE ...]] The part of URL that are excluded from reporting

--time, -t            Print the report based on the total call time

--count, -c           Print the report based on the total number of queries

--median, -m          Print the report based on a median duration of calls

--remote, -r          Print the report based on the number of calls from remote hosts
                  
--status [STATUS [STATUS ...]], -s [STATUS [STATUS ...]] Print the report, based on the request status

--limit LIMIT, -L LIMIT Limit the output reports. Default 100.

--debug, -d           Displays the count of unparsed lines and the unparsed line numbers

examples:
=========

nginxparser -l /path/to/access_nginx.log -t -e /static /exclude

nginxparser -l /path/to/access_nginx.log -s 500 499 -o /path/to/outfile.txt

nginxparser -l ../nginx_access.log -o ../test_all.txt -e /static /pull -tcmr -s 499 500 -p 2015.10.06_00:00:00 2015.10.07_00:00:00
