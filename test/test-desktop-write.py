#!/usr/bin/python
from xdg.DesktopEntry import *

import os, sys

test = DesktopEntry()
test.parse("/usr/share/applications/gedit.desktop")
test.removeKey("Name")
test.addGroup("Hallo")
test.set("key", "value", "Hallo")
test.write("test.desktop")
