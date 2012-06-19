#!/usr/bin/python
from xdg.IconTheme import *

print (getIconPath("firefox"))

theme = IconTheme()
theme.parse("/usr/share/icons/hicolor/index.theme")
theme.validate()
