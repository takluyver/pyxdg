#!/usr/bin/python
from xdg.IconTheme import *

print("Finding an icon that probably exists:")
print (getIconPath("firefox"))

print("Finding one that doesn't (should print None):")
print (getIconPath("oijeorjewrjkngjhbqefew"))

print("Validating icon theme...")
theme = IconTheme()
theme.parse("/usr/share/icons/hicolor/index.theme")
theme.validate()
