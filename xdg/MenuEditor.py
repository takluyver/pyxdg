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
			self.doc = xml.dom.minidom.parseString('<!DOCTYPE Menu PUBLIC "-//freedesktop//DTD Menu 1.0//EN" "http://standards.freedesktop.org/menu-spec/menu-1.0.dtd"><Menu><Name>Applications</Name><MergeFile type="parent">' + xdg_data_dirs[1] + '</MergeFile></Menu>')
		except xml.parsers.expat.ExpatError:
			raise ParsingError('Not a valid .menu file', self.filename)

	def save(self):
		self.__saveEntries(self.menu)
		self.__saveMenu()

	def __saveEntries(self, menu):
		if not menu:
			menu = self.menu
		if isinstance(menu.Directory, MenuEntry):
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

	def createEntry(self, parent, name, command=None, comment=None, icon=None, term=None, after=None):
		filename = self.__getFileName(name, ".desktop")
		entry = MenuEntry(filename)
		entry = self.editEntry(entry, name, command, comment, icon, term)

		# FIXME: Layout tag respecting after

		parent.DeskEntries.append(entry)
		sort(parent)

		xml_menu = self.__getXmlMenu(parent.getPath())
		self.__addFilename(xml_menu, filename, 'Include')

		return entry

	def createMenu(self, parent, name, comment=None, icon=None, after=None):
		filename = self.__getFileName(name, ".directory")
		menu = Menu()
		menu = self.editMenu(menu, name, comment, icon)

		menuname = self.__getFixedName(name)
		menu.Name = menuname

		# FIXME: Layout tag respecting after
		menu.Layout = parent.DefaultLayout
		menu.DefaultLayout = parent.DefaultLayout

		parent.addSubmenu(menu)
		sort(menu)

		xml_menu = self.__getXmlMenu(menu.getPath())
		self.__addTextElement(xml_menu, 'Directory', filename)

		return menu

	def __getFileName(self, name, extension):
		name = self.__getFixedName(name)

		postfix = 0
		while 1:
			filename = name + "-" + str(postfix) + extension
			if not os.path.isfile(os.path.join(xdg_data_dirs[0], filename)):
				break
			else:
				postfix += 1

		return filename

	def __getFixedName(self, name):
		chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456790"
		for char in name:
			if char not in chars:
				name = name.replace(char, "")
		return name

	def __getXmlMenu(self, path, element=None):
		if not element:
			element = self.doc.documentElement

		if "/" in path:
			(name, path) = path.split("/", 1)
		else:
			name = path
			path = ""

		found = False
		for node in element.childNodes:
			if node.nodeType == xml.dom.Node.ELEMENT_NODE and node.nodeName == 'Menu':
				for subnode in node.childNodes:
					if subnode.nodeType == xml.dom.Node.ELEMENT_NODE and subnode.nodeName == 'Name':
						if subnode.childNodes[0].nodeValue == name:
							if path:
								found = self.__getXmlMenu(path, node)
							else:
								found = node
							break
			if found:
				break
		if not found:
			node = self.__addMenuElement(element, name)
			if path:
				found = self.__getXmlMenu(path, node)
			else:
				found = node

		return found

	def __addMenuElement(self, element, name):
		node = self.doc.createElement('Menu')
		self.__addTextElement(node, 'Name', name)
		return element.appendChild(node)

	def __addTextElement(self, element, name, text):
		node = self.doc.createElement(name)
		text = self.doc.createTextNode(text)
		node.appendChild(text)
		return element.appendChild(node)

	def __addFilename(self, element, filename, type = "Include"):
		node = self.doc.createElement(type)
		node.appendChild(self.__addTextElement(node, 'Filename', filename))
		return element.appendChild(node)

	def moveEntry(self, entry, oldparent, newparent, after=None):
		index = oldparent.DeskEntries.index(entry)
		oldparent.DeskEntries.remove(index)
		newparent.DeskEntries.append(entry)

		# FIXME: Layout tag respecting after
		sort(oldparent)
		sort(newparent)

		# FIXME: Also pass AppDirs around
		old_menu = self.__getXmlMenu(oldparent)
		new_menu = self.__getXmlMenu(newparent)
		self.__addFilename(old_menu, entry.DesktopFileID, "Exclude")
		self.__addFilename(new_menu, entry.DesktopFileID, "Include")

	def moveMenu(self, menu, oldparent, newparent, after=None):
		index = oldparent.Submenus.index(menu)
		oldparent.Submenus.remove(index)
		newparent.addSubmenu(menu)

		# FIXME: Layout tag respecting after
		sort(oldparent)
		sort(newparent)

		# FIXME: Also pass DirectoryDirs around
		self.__addMove(self.doc, os.path.join(oldparent.getPath(), menu.Name), os.path.join(newparent.getPath(), menu.Name))

	def __addMove(self, element, old, new):
		node = self.doc.createElement("Move")
		node.appendChild(self.__addTextElement(node, 'Old', old))
		node.appendChild(self.__addTextElement(node, 'New', new))
		return element.appendChild(node)

	def editEntry(self, entry, name=None, genericname=None, comment=None, command=None, icon=None, term=None, hidden=None):
		# FIXME: Also pass AppDirs around
		deskentry = entry.DesktopEntry

		if name:
			if not deskentry.hasKey("Name"):
				deskentry.set("Name", name)
			deskentry.set("Name", name, locale = True)
		if comment:
			if not deskentry.hasKey("Comment"):
				deskentry.set("Comment", comment)
			deskentry.set("Comment", comment, locale = True)
		if genericname:
			if not deskentry.hasKey("GnericNe"):
				deskentry.set("GenericName", genericname)
			deskentry.set("GenericName", genericname, locale = True)
		if command:
			deskentry.set("Command", command)
		if icon:
			deskentry.set("Icon", icon)

		if term == True:
			deskentry.set("Terminal", "true")
		elif term == False:
			deskentry.set("Terminal", "false")

		if hidden == True:
			deskentry.set("Hidden", "true")
		elif hidden == False:
			deskentry.set("Hidden", "false")

		return entry

	def editMenu(self, menu, name=None, genericname=None, comment=None, icon=None, hidden=None):
		# FIXME: respect DirectoryDir
		if isinstance(menu.Directory, MenuEntry):
			deskentry = menu.Directory.DesktopEntry
		else:
			deskentry = MenuEntry(self.__getFileName(name))
			menu.Directory = deskentry

		if name:
			if not deskentry.hasKey("Name"):
				deskentry.set("Name", name)
			deskentry.set("Name", name, locale = True)
		if genericname:
			if not deskentry.hasKey("GenericName"):
				deskentry.set("GenericName", genericname)
			deskentry.set("GenericName", genericname, locale = True)
		if comment:
			if not deskentry.hasKey("Comment"):
				deskentry.set("Comment", comment)
			deskentry.set("Comment", comment, locale = True)
		if icon:
			deskentry.set("Icon", icon)

		if hidden == True:
			deskentry.set("Hidden", "true")
		elif hidden == False:
			deskentry.set("Hidden", "false")

		return menu

	def hideEntry(self, entry):
		return self.editEntry(entry, hidden=True)

	def unhideEntry(self, entry):
		return self.editEntry(entry, hidden=False)

	def hideMenu(self, menu):
		return self.editMenu(menu, hidden=True)

	def unhideMenu(self, menu):
		return self.editMenu(menu, hidden=False)

	def deleteEntry(self, entry):
		pass

	def deleteMenu(self, menu):
		pass

	def createSeparator(self, parent, after=None):
		pass

	def moveSeparator(self, separator, after=None):
		pass

	def deleteSeparator(self, separator):
		pass
