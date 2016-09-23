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
            timestamp = d['local_time'][:-9]
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


def grep_upstream(value):
    print("Grep lines where upstream_time >= {}\n".format(value))
    while True:
        d = (yield)
        try:
            if float(d['upstream_time']) >= value:
                print('{} - [{}] "{}" "{} {}" {} ({}) "{}" "{} {}" [{}] [{}]'.format(
                    d['remote_addr'],
                    d['local_time'],
                    d['host'],
                    d['method'],
                    d['request'],
                    d['status'],
                    d['bytes_sent'],
                    d['http_referer'],
                    d['uri'],
                    d['args'],
                    d['request_time'],
                    d['upstream_time']
                ))
        except ValueError:
            pass


def progress_bar(total, current, parsed):
    sys.stdout.write('\rTotal: {}\tCurrent: {} ({}%)\tParsed: {} ({}%)'.format(
        total,
        current,
        current * 100 // total,
        parsed,
        parsed * 100 // total
    ))
    sys.stdout.flush()


def parse(log_file, debug=False, uri=False, time=False, clients=False, grep=False, log_format=log_format):
    lines_count = sum(1 for l in open(log_file))

    lines = read_file_line(log_file)

    total_count = 0
    parsed_count = 0
    methods = {}
    timeline={}
    clients_ip={}

    if uri:
        cm = count_methods()
        next(cm)

    if time:
        ct = count_timeline()
        next(ct)

    if clients:
        cc = count_clients()
        next(cc)

    if grep:
        gu = grep_upstream(grep)
        next(gu)

    for line in lines:
        m = re.match(log_format, line)
        total_count += 1
        try:
            parsed_line = m.groupdict()
            parsed_count += 1

            if uri:
                cm.send(parsed_line)

            if time:
                ct.send(parsed_line)

            if clients:
                cc.send(parsed_line)

            if grep:
                gu.send(parsed_line)

        except AttributeError:
            if debug:
                print('Line {} not parsed: {} '.format(total_count, line))

        if total_count % 1000 == 0 and not grep:
            progress_bar(lines_count, total_count, parsed_count)

    if uri:
        methods = cm.send(None)
        cm.close()

    if time:
        timeline = ct.send(None)
        ct.close()

    if clients:
        clients_ip = cc.send(None)
        cc.close()

    if grep:
        gu.close()

    return {
        "total_count": total_count,
        "parsed_count": parsed_count,
        "methods": methods,
        "timeline": timeline,
        "clients": clients_ip
    }


def dump_data_to_json(data, json_file):
    with open(json_file, 'w') as jf:
        json.dump(data, jf)
        print("dump exported")


def print_report(data):
    print("\n\nParsed {} from {} lines".format(data["parsed_count"], data["total_count"]))

    if data["methods"]:
        for method in data["methods"].keys():
            print("\n{0} {1} {0}".format((78 - len(method) // 2) * "=", method))
            print("{:>10}\t{:>10}\t{:>10}\t{:>5}\t{:>10}\t{:>5}\t{:>12}\t{:>5}\t{:<30}\t{:<}".format(
                "Count",
                "Responded",
                "ReqTime",
                "AvgRT",
                "UpstTime",
                "AvgUT",
                "Bytes",
                "AvgB",
                "Uri",
                "StatusCount"
            ))
            m_count = 0
            m_responded = 0
            m_request_time = 0
            m_upstream_time = 0
            m_bytes_sent = 0
            m_status = {}
            for uri in data["methods"][method].keys():
                count = data["methods"][method][uri]["count"]
                responded = data["methods"][method][uri]["responded"]
                request_time = data["methods"][method][uri]["request_time"]
                upstream_time = data["methods"][method][uri]["upstream_time"]
                bytes_sent = data["methods"][method][uri]["bytes_sent"]
                m_count += count
                m_responded += responded
                m_request_time += request_time
                m_upstream_time += upstream_time
                m_bytes_sent += bytes_sent
                status_line = "["
                for status in data["methods"][method][uri]["status"].keys():
                    s_count = data["methods"][method][uri]["status"][status]
                    m_status[status] = m_status.get(status, 0) + s_count
                    status_line += "{}:{}, ".format(status, s_count)
                try:
                    avg_upstream_time = upstream_time / responded
                except ZeroDivisionError:
                    avg_upstream_time = 0
                line = "{:>10}\t{:>10}\t{:>10.2f}\t{:>5.2f}\t{:>10.2f}\t{:>5.2f}\t{:>12}\t{:>5.0f}\t{:<30}\t{:<}".format(
                    count,
                    responded,
                    request_time,
                    request_time / count,
                    upstream_time,
                    avg_upstream_time,
                    bytes_sent,
                    bytes_sent / count,
                    uri,
                    status_line[:-2] + "]"
                )
                print(line)


def main():
    arguments = ArgumentParser(
        description='using log format: \'$remote_addr - [$time_local] "$host" "$request" '
                    '$status ($bytes_sent) "$http_referer" '
                    '"$uri $args" [$request_time] [$upstream_response_time]\'',
        # epilog='version = {}'.format(__version__)
    )
    arguments.add_argument("log_file", help="NGINX log file, with defined format")
    arguments.add_argument("--uri", "-u", action="count", help="Get uri-based report")
    arguments.add_argument("--time", "-t", action="count", help="Get time-based report")
    arguments.add_argument("--clients", "-c", action="count", help="Get client-based report")
    arguments.add_argument("--grep", "-g", action="store", type=float,
                           help="Grep lines, where 'upstream_time' more than the specified")
    arguments.add_argument("--dump", "-d", action="store", help="Export parsed data to the json.file")
    arguments.add_argument("--no_report", "-N", action="count", help="Don't print the report")
    arguments.add_argument("--debug", "-D", action="count", help="Print not parsed lines")
    args = arguments.parse_args()

    if not any([args.uri, args.time, args.clients, args.grep]):
        print("You didn't choised a parsing parameters")
        exit()

    data = parse(args.log_file, args.debug, args.uri, args.time, args.clients, args.grep)
    if not args.no_report:
        print_report(data)

    if args.dump:
        dump_data_to_json(data, args.dump)


if __name__ == "__main__":
    main()
