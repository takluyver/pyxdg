""" CLass to edit XDG Menus """

from xdg.Menu import *
from xdg.BaseDirectory import *
from xdg.Exceptions import *
from xdg.DesktopEntry import *
import xml.dom.minidom
import os

class MenuEditor:
	def __init__(self, menu=None, filename=None)
		self.menu = None
		self.filename = None
		self.doc = None
		self.parse(menu, filename)

	def parse(self, menu=None, filename=None)
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

	def __saveEntries(self, menu)
		if not menu:
			menu = self.menu
		if isinstance(menu.Directory, DesktopEntry):
			menu.Directory.save()
		for entry in self.getEntries(hidden = True):
			if isinstance(entry, MenuEntry):
				entry.save()
			elif isinstance(entry, Menu):
				self.save(entry)

	def __saveMenu():
		if not os.path.isdir(os.path.basename(self.filename)):
			os.makedirs(os.path.basename(self.filename))
		fd = open(self.filename, 'w')
		fd.write(self.doc.toprettyxml().replace('<?xml version="1.0" ?>\n', ''))
		fd.close()

	def createEntry(self, menu, name, comment, command, icon, term, after=None):
		pass

	def createMenu(self, menu, name, comment, icon, after=None):
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
		pass

	def editMenu(self, menu, name=None, comment=None, icon=None):
		pass

	def hideMenu(self, menu):
		pass

	def unhideMenu(self, menu):
		pass

	def hideEntry(self, entry):
		pass

	def unhideEntry(self, entry):
		pass

	def deleteSeparator(self, separator):
		pass
