#!/usr/bin/env python

import re
import json
from datetime import datetime
from patterns import log_format


def read_file_line(file_name):
    with open(file_name, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            yield line


def date_to_json(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj


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


def parse(log_format=log_format, **kwargs):
    log_file = kwargs.get('log_file', '')
    out_json_file = kwargs.get('out_json_file', '')
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
            print('Line {}: {} not parsed'.format(total_count, line))
    methods = cm.send(None)
    timeline = ct.send(None)
    clients = cc.send(None)
    cm.close()
    ct.close()
    cc.close()
    if out_json_file:
        with open(out_json_file, 'w') as ojf:
            json_timeline = {}
            for tm in timeline.keys():
                json_timeline[date_to_json(tm)] = timeline[tm]
            json.dump({
                "total_count": total_count,
                "parsed_count": parsed_count,
                "methods": methods,
                "timeline": json_timeline,
                "clients": clients
            }, ojf)


parse(**{'log_file': "test.log", 'out_json_file': "out.json"})
