# nginxparser

### NGINX log parser and analyzer

Installation:

    pip install nginxparser

Using log format:

    log_format myformat '$remote_addr - [$time_local] "$host" "$request" '
                        '$status ($bytes_sent) "$http_referer" '
                        '"$uri $args" [$request_time] [$upstream_response_time]';

usage: 

    nginxparser [-h] [--uri] [--time] [--clients] [--grep GREP] [--dump DUMP]
                [--no_report] [--debug]
                log_file


optional arguments:

      -h, --help            show this help message and exit
      --uri, -u             Get uri-based report
      --time, -t            Get time-based report
      --clients, -c         Get client-based report
      --grep GREP, -g GREP  Grep lines, where 'upstream_time' more than the
                            specified
      --dump DUMP, -d DUMP  Export parsed data to the json.file
      --no_report, -N       Don't print the report
      --debug, -D           Print not parsed lines


examples:

    nginxparser --uri /path/to/access_nginx.log
    nginxparser --time /path/to/access_nginx.log
    nginxparser --clients /path/to/access_nginx.log
    nginxparser --grep 10 /path/to/access_nginx.log
    nginxparser -utcN -d out.json /path/to/access_nginx.log
