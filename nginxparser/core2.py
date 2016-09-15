#!/usr/bin/env python

from re import compile


def read_file_line(file_name):
    with open(file_name, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            yield line


def grep(pattern):
    print("Searching for", pattern)
    while True:
        line = (yield)
        if pattern in line:
            print(line)


def parse_line(log_format):
    lf = compile(log_format)
    while True:
        line = (yield)
        print(lf.findall(line))


log_format = '([\d.]+) \- \[(.+)\] "([\w\.\-]+)" "([A-Z]+) ([\w\.\-\/]+).+" ' \
             '(\d{3}) \((\d+)\) "(.+)" ' \
             '"(.+) (.+)" \[([\d\.]+)] \[([\d\.-]+)]'






search = grep('buyouts')
next(search)

parse = parse_line(log_format)
next(parse)

lines = read_file_line("test.log")

search.send(lines.__next__())

parse.send(lines.__next__())