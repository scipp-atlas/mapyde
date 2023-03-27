#!/usr/bin/env python3

from __future__ import annotations

import argparse

parser = argparse.ArgumentParser(description="Process some arguments.")
parser.add_argument("-i", "--input", help="name of analysis")
parser.add_argument("-o", "--output", help="path to JSON background-only file")
args = parser.parse_args()

output = open(args.output, "w")
for line in open(args.input):
    sline = line.split()
    if len(sline) > 0:
        try:
            particle = int(sline[0])
            if (particle > 1000000 and particle <= 1000016) or (
                particle > 2000000 and particle <= 2000016
            ):
                out = line.replace(sline[1], "2.00000000e+03")
        except ValueError:
            pass
    else:
        out = line
    output.write(out)


output.close()
