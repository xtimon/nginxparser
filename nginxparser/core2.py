#!/usr/bin/env python

import re
from .patterns import log_format


def read_file_line(file_name):
    with open(file_name, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            yield line


def parse_line(log_format):
    while True:
        line = (yield)
        m = re.match(log_format, line)
        print(m.groupdict())


parse = parse_line(log_format)
next(parse)
lines = read_file_line("test.log")
parse.send(lines.__next__())
