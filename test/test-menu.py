#!/usr/bin/python

import sys

import xdg.Menu
import xdg.DesktopEntry

def show_menu(menu, depth = 0):
#	print depth*"-" + "\x1b[01m" + menu.getName().encode("ascii", 'ignore') + "\x1b[0m"
#	depth += 1
	for entry in menu.getEntries():
		if isinstance(entry, xdg.Menu.Menu):
			show_menu(entry, depth)
		elif isinstance(entry, xdg.Menu.MenuEntry):
#			print depth*"-" + entry.DesktopEntry.getName().encode("ascii", 'ignore')
			print menu.getPath() + "/\t" + entry.DesktopFileID + "\t" + entry.DesktopEntry.getFileName()
#		elif isinstance(entry, xdg.Menu.Separator):
#			print depth*"-" + "|||"
#		elif isinstance(entry, xdg.Menu.Header):
#			print depth*"-" + "\x1b[01m" + entry.Name + "\x1b[0m"
#	depth -= 1

show_menu(xdg.Menu.parse())
#xdg.Menu.parse()
