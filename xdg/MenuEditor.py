""" CLass to edit XDG Menus """

from xdg.Menu import *
from xdg.BaseDirectory import *
from xdg.Exceptions import *
from xdg.DesktopEntry import *

import xml.dom.minidom
import os

class MenuEditor:
	def __init__(self, menu=None, filename=None):
		self.menu = None
		self.filename = None
		self.doc = None
		self.parse(menu, filename)

	def parse(self, menu=None, filename=None):
		if isinstance(menu, Menu):
			self.menu = menu
		elif isinstance(menu, unicode):
			self.menu = parse(menu)
		else:
			self.menu = parse()

		if filename:
			self.filename = filename
		elif os.access(self.menu.Filename, os.W_OK):
			self.filename = self.menu.Filename
		else:
			self.filename = os.path.join(xdg_config_dirs[0], "menus", "applications.menu")

		try:
			self.doc = xml.dom.minidom.parse(self.filename)
		except IOError:
			self.doc = xml.dom.parseString('<!DOCTYPE Menu PUBLIC "-//freedesktop//DTD Menu 1.0//EN" "http://standards.freedesktop.org/menu-spec/menu-1.0.dtd"><Menu><Name>Applications</Name><MergeFile type="parent">/etc/xdg/menus/applications.menu</MergeFile></Menu>')
		except xml.parsers.expat.ExpatError:
			raise ParsingError('Not a valid .menu file', self.filename)

	def save(self):
		self.__saveEntries(self.menu)
		self.__saveMenu()

	def __saveEntries(self, menu):
		if not menu:
			menu = self.menu
		if isinstance(menu.Directory, DesktopEntry):
			menu.Directory.save()
		for entry in menu.getEntries(hidden = True):
			if isinstance(entry, MenuEntry):
				entry.save()
			elif isinstance(entry, Menu):
				self.__saveEntries(entry)

	def __saveMenu(self):
		if not os.path.isdir(os.path.basename(self.filename)):
			os.makedirs(os.path.basename(self.filename))
		fd = open(self.filename, 'w')
		fd.write(self.doc.toprettyxml().replace('<?xml version="1.0" ?>\n', ''))
		fd.close()

	def createEntry(self, menu, name, command=None, comment=None, icon=None, term=None, after=None):
		filename = self.__getFileName(name, ".desktop")
		menu_entry = MenuEntry(filename)
		menu_entry = self.editEntry(menu_entry, name, command, comment, icon, term)

		menu.DeskEntries.append(menu_entry)
		sort(menu)

		# FIXME: create the xml
		# FIXME: Layout tag respecting after

		return menu_entry

	def createMenu(self, menu, name, comment=None, icon=None, after=None):
		filename = self.__getFileName(name, ".directory")
		new_menu = Menu()
		new_menu.Name = name
		new_menu.Directory = DesktopEntry(filename)
		new_menu.Depth = menu.Depth + 1
		new_menu = self.editMenu(new_menu, name, comment, icon)

		menu.Submenus.append(new_menu)
		sort(menu)

		# FIXME: create the xml
		# FIXME: Layout tag respecting after

		return new_menu

	def __getFileName(self, name, extension):
		postfix = 0
		while True:
			filename = name + "-" + str(postfix) + extension
			if os.path.isfile(os.path.join(xdg_data_dirs[0], filename)):
				break
			else:
				postfix += 1
		return filename

	def __getMenu(self, item):
		# FIXME: return or create the xml node for the menu
		pass

	def createSeparator(self, menu, after=None):
		pass

	def moveEntry(self, entry, oldmenu, newmenu, after=None):
		pass

	def moveMenu(self, menu, oldmenu, newmenu, after=None):
		pass

	def moveSeparator(self, separator, after=None):
		pass

	def editEntry(self, entry, name=None, comment=None, command=None, icon=None, term=None):
		# FIXME: locale options
		if name:
			entry.DesktopEntry.set("Name", name)
		if command:
			entry.DesktopEntry.set("Command", command)
		if comment:
			entry.DesktopEntry.set("Comment", comment)
		if icon:
			entry.DesktopEntry.set("Icon", icon)
		if term:
			entry.DesktopEntry.set("Terminal", term)
		return entry

	def editMenu(self, menu, name=None, comment=None, icon=None):
		# FIXME: What if a Menu has no .directory file
		if name:
			menu.Directory.set("Name", name)
		if comment:
			menu.Directory.set("Comment", comment)
		if icon:
			menu.Directory.set("Icon", icon)
		return menu

	def hideEntry(self, entry):
		# FIXME what to set NoDisplay or Hidden?
		entry.DesktopEntry.set("NoDisplay", True)
		return entry

	def unhideEntry(self, entry):
		# FIXME what to set NoDisplay or Hidden?
		entry.DesktopEntry.set("NoDisplay", False)
		return entry

	def hideMenu(self, menu):
		# FIXME: What if a Menu has no .directory file
		menu.Directory.set("Hidden", True)
		return menu

	def unhideMenu(self, menu):
		menu.Directory.set("Hidden", False)
		return menu

	def deleteEntry(self, entry):
		pass

	def deleteMenu(self, menu):
		pass

	def deleteSeparator(self, separator):
		pass
