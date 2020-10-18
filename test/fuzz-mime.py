#!/usr/bin/env python3
"""Run this manually to test xdg.Mime.get_type2 against all files in a directory.

Syntax: ./fuzz-mime.py /dir/to/test/
"""
from __future__ import print_function

import sys, os
from xdg import Mime

testdir = sys.argv[1]
files = os.listdir(testdir)

for f in files:
    f = os.path.join(testdir, f)
    try:
        print(f, Mime.get_type2(f))
    except:
        print(f)
        raise
