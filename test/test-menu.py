#!/usr/bin/env python2

import re, sys

import xdg.Menu
import xdg.DesktopEntry

def show_menu(menu, depth = 0):
#	print depth*"-" + "\x1b[01m" + menu.getName().encode("ascii", 'ignore') + "\x1b[0m"
	depth += 1
	for entry in menu.getEntries():
		if isinstance(entry, xdg.Menu.Menu):
			show_menu(entry, depth)
		elif isinstance(entry, xdg.Menu.MenuEntry):
#			print depth*"-" + entry.DesktopEntry.getName().encode("ascii", 'ignore')
			print re.sub("/KDE/", "", menu.getPath()) + "/\t" + entry.DesktopFileID + "\t" + entry.DesktopEntry.getFileName()
	depth -= 1

try:
	menu = xdg.Menu.parse(sys.argv[1])
	menu.setWM("GNOME")
	menu.setLocale("de")
	show_menu(menu)
except IndexError:
	show_menu(xdg.Menu.parse(), 0)
