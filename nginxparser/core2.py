#!/usr/bin/env python

import asyncio
import re
from datetime import datetime
from patterns import log_format


def read_file_line(file_name):
    with open(file_name, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            yield line


def parse_line(log_format):
    total_count = 0
    parsed_count = 0
    while True:
        line = (yield)
        m = re.match(log_format, line)
        total_count += 1
        try:
            parsed_line = m.groupdict()
            parsed_count += 1
            cm.send(parsed_line)
            ct.send(parsed_line)
        except AttributeError:
            print('Line {}: {} not parsed'.format(total_count, line))
        print('total count: {}\tparsed_count: {}'.format(total_count, parsed_count))


def count_methods():
    methods = {}
    while True:
        d = (yield)
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
        print(methods)


def count_timeline():
    timeline = {}
    while True:
        d = (yield)
        timestamp = datetime.strptime(d['local_time'][:-9], '%d/%b/%Y:%H:%M')
        status = d['status']
        timeline[timestamp] = timeline.get(timestamp, {})
        timeline[timestamp][status] = timeline[timestamp].get(status, 0) + 1
        print(timeline)


parse = parse_line(log_format)
next(parse)
lines = read_file_line("test.log")
cm = count_methods()
ct = count_timeline()
next(cm)
next(ct)
parse.send(lines.__next__())
# parse.send(next(lines))
