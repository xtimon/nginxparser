# patterns.py

# using log format: '$remote_addr - [$time_local] "$host" "$request" '\
#                   ' $status ($bytes_sent) "$http_referer" \
#                   '"$uri $args" [$request_time] [$upstream_response_time]'

log_format = '(?P<remote_addr>[\d.]+) \- \[(?P<local_time>.+)\] "(?P<host>[\w\.\-]+)" "(?P<method>[A-Z]+) (?P<request>[\w\.\-\/]+).+" ' \
             '(?P<status>\d{3}) \((?P<bytes_sent>\d+)\) "(?P<http_referer>.+)" ' \
             '"(?P<uri>.+) (?P<args>.+)" \[(?P<request_time>[\d\.]+)] \[(?P<upstream_time>[\d\.-]+)]'
