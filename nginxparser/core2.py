#!/usr/bin/env python

import re
import json
import sys
from argparse import ArgumentParser
from datetime import datetime
from patterns import log_format


def read_file_line(file_name):
    with open(file_name, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            yield line


def count_methods():
    methods = {}
    while True:
        d = (yield)
        if d:
            method = d['method']
            uri = re.sub('\d+', '%d', d['uri'])
            bytes = int(d['bytes_sent'])
            request_time = float(d['request_time'])
            status = d['status']
            try:
                upstream_time = float(d['upstream_time'])
                responded = 1
            except ValueError:
                upstream_time = 0
                responded = 0
            methods[method] = methods.get(method, {})
            methods[method][uri] = methods[method].get(uri, {
                "count": 0,
                "responded": 0,
                "bytes_sent": 0,
                "request_time": 0,
                "upstream_time": 0,
                "status": {}
            })
            methods[method][uri]["status"][status] = methods[method][uri]["status"].get(status, 0) + 1
            methods[method][uri]["count"] += 1
            methods[method][uri]["responded"] += responded
            methods[method][uri]["bytes_sent"] += bytes
            methods[method][uri]["request_time"] += request_time
            methods[method][uri]["upstream_time"] += upstream_time
        yield methods


def count_timeline():
    timeline = {}
    while True:
        d = (yield)
        if d:
            timestamp = datetime.strptime(d['local_time'][:-9], '%d/%b/%Y:%H:%M')
            status = d['status']
            timeline[timestamp] = timeline.get(timestamp, {})
            timeline[timestamp][status] = timeline[timestamp].get(status, 0) + 1
        yield timeline


def count_clients():
    clients = {}
    while True:
        d = (yield)
        if d:
            remote_addr = d['remote_addr']
            request_time = float(d['request_time'])
            try:
                upstream_time = float(d['upstream_time'])
                responded = 1
                responded_request_time = request_time
            except ValueError:
                upstream_time = 0
                responded = 0
                responded_request_time = 0
            clients[remote_addr] = clients.get(remote_addr, {
                "total_count": 0,
                "responded": 0,
                "total_request_time": 0,
                "responded_request_time": 0,
                "upstream_time": 0
            })
            clients[remote_addr]["total_count"] += 1
            clients[remote_addr]["responded"] += responded
            clients[remote_addr]["total_request_time"] += request_time
            clients[remote_addr]["responded_request_time"] += responded_request_time
            clients[remote_addr]["upstream_time"] += upstream_time
        yield clients


def progress_bar(total, current, parsed):
    sys.stdout.write('\rTotal: {}\tCurrent: {} ({}%)\tParsed: {} ({}%)'.format(
        total,
        current,
        current * 100 // total,
        parsed,
        parsed * 100 // total
    ))
    sys.stdout.flush()


def parse(log_file, debug=False, log_format=log_format):
    lines_count = sum(1 for l in open(log_file))
    lines = read_file_line(log_file)
    total_count = 0
    parsed_count = 0
    cm = count_methods()
    ct = count_timeline()
    cc = count_clients()
    next(cm)
    next(ct)
    next(cc)
    for line in lines:
        m = re.match(log_format, line)
        total_count += 1
        try:
            parsed_line = m.groupdict()
            parsed_count += 1
            cm.send(parsed_line)
            ct.send(parsed_line)
            cc.send(parsed_line)
        except AttributeError:
            if debug:
                print('Line {}: {} not parsed'.format(total_count, line))
        if total_count % 1000 == 0:
            progress_bar(lines_count, total_count, parsed_count)
    methods = cm.send(None)
    timeline = ct.send(None)
    clients = cc.send(None)
    cm.close()
    ct.close()
    cc.close()
    return {
        "total_count": total_count,
        "parsed_count": parsed_count,
        "methods": methods,
        "timeline": timeline,
        "clients": clients
    }


def date_to_json(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj


def dump_data_to_json(data, json_file):
    for dt in list(data["timeline"].keys()):
        data["timeline"][date_to_json(dt)] = data["timeline"][dt]
        del data["timeline"][dt]
    with open(json_file, 'w') as jf:
        json.dump(data, jf)


def main():
    arguments = ArgumentParser(
        description='using log format: \'$remote_addr - [$time_local] "$host" "$request" '
                    '$status ($bytes_sent) "$http_referer" '
                    '"$uri $args" [$request_time] [$upstream_response_time]\'',
        # epilog='version = {}'.format(__version__)
    )
    arguments.add_argument("log_file", help='NGINX log file with defined format')
    arguments.add_argument("out_json_report", help='Write report to json file')
    arguments.add_argument("--debug", "-D", action='count', help='Print not parsed lines')
    args = arguments.parse_args()
    data = parse(args.log_file, args.debug)
    dump_data_to_json(data, args.out_json_report)


if __name__ == "__main__":
    main()
