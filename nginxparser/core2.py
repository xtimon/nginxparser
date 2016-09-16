#!/usr/bin/env python

import re
from patterns import log_format


def read_file_line(file_name):
    with open(file_name, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            yield line


def parse_line(log_format):
    a = analyze()
    next(a)
    total_count = 0
    parsed_count = 0
    while True:
        line = (yield)
        m = re.match(log_format, line)
        total_count += 1
        try:
            a.send(m.groupdict())
            parsed_count += 1
        except AttributeError:
            print('Line {}: {} not parsed'.format(total_count, line))
        print('total count: {}\tparsed_count: {}'.format(total_count, parsed_count))


def analyze():
    cm = count_methods()
    next(cm)
    responsed_count = 0
    while True:
        d = (yield)
        try:
            upstream_time = float(d['upstream_time'])
            responsed_count +=1
        except ValueError:
            upstream_time = -1
        request_time = float(d['request_time'])
        print(upstream_time)
        cm.send({'method': d['method'], 'request_time': request_time, 'upstream_time': upstream_time})


def count_methods():
    count = {}
    while True:
        d = (yield)
        method = d['method']
        request_time = d['request_time']
        upstream_time = d['upstream_time']
        not_responded = 0
        if upstream_time == -1:
            not_responded = 1
            upstream_time = 0
        if method in count.keys():
            count[method]['count'] += 1
            count[method]['upstream_time'] += upstream_time
            count[method]['request_time'] += request_time
            count[method]['not_responded'] += not_responded
        else:
            count[method] = {
                'count': 1,
                'upstream_time': upstream_time,
                'request_time': request_time,
                'not_responded': not_responded
            }
        print(count)


parse = parse_line(log_format)
next(parse)
lines = read_file_line("test.log")
parse.send(lines.__next__())
# parse.send(next(lines))
