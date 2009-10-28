#!/usr/bin/python
from xdg.DesktopEntry import *

import os, sys

def checkfiles(path):
    if os.path.isdir(path):
        ls = os.listdir(path)
        for file in ls:
            checkfiles(os.path.join(path, file))
    else:
        entry = DesktopEntry()
        try:
            entry.parse(path)
        except ParsingError, e:
            print e
            return

        #entry.setLocale("C")
        entry.getName()

        try:
            entry.validate()
        except ValidationError, e:
            print e

try:
    checkfiles(sys.argv[1])

except IndexError:
    print("No file or directory given!")
