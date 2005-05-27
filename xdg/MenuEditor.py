""" CLass to edit XDG Menus """

from xdg.Menu import *
from xdg.BaseDirectory import *
from xdg.Exceptions import *
from xdg.DesktopEntry import *

import xml.dom.minidom
import os

# FIXME: pass AppDirs/DirectoryDirs around in the edit/move functions
# FIXME: delete functions

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
			self.doc = xml.dom.minidom.parseString('<!DOCTYPE Menu PUBLIC "-//freedesktop//DTD Menu 1.0//EN" "http://standards.freedesktop.org/menu-spec/menu-1.0.dtd"><Menu><Name>Applications</Name><MergeFile type="parent">' + xdg_config_dirs[1] + '/menus/applications.menu</MergeFile></Menu>')
		except xml.parsers.expat.ExpatError:
			raise ParsingError('Not a valid .menu file', self.filename)

	def save(self):
		self.__saveEntries(self.menu)
		self.__saveMenu()

	def createEntry(self, parent, name, command=None, comment=None, icon=None, term=None, after=None):
		# create the entry
		filename = self.__getFileName(name, ".desktop")
		entry = MenuEntry(filename)
		entry.Menus.append(parent)
		entry = self.editEntry(entry, name, command, comment, icon, term)
		self.__addEntry(parent, entry, after)

		# create the xml
		xml_menu = self.__getXmlMenu(parent.getPath(True, True))
		self.__addXmlFilename(xml_menu, filename, 'Include')

		# layout stuff
		if after:
			self.__addLayout(parent)
			self.__addXmlLayout(xml_menu, parent.Layout)

		sort(parent)

		return entry

	def createMenu(self, parent, name, comment=None, icon=None, after=None):
		# create the entry
		filename = self.__getFileName(name, ".directory")
		menu = Menu()
		menu = self.editMenu(menu, name, comment, icon)

		menuname = self.__getFixedName(name)
		menu.Name = menuname

		menu.Layout = parent.DefaultLayout
		menu.DefaultLayout = parent.DefaultLayout

		self.__addEntry(parent, menu, after)

		# create the xml
		xml_menu = self.__getXmlMenu(menu.getPath(True, True))
		self.__addXmlTextElement(xml_menu, 'Directory', filename)

		# layout stuff
		if after:
			self.__addLayout(parent)
			self.__addXmlLayout(xml_menu, parent.Layout)

		sort(parent)

		return menu

	def createSeparator(self, parent, after=None):
		# create the separator
		separator = Separator()

		self.__addEntry(parent, separator, after)
		self.__addLayout(parent)

		# create the xml and layout stuff
		menu = self.__getXmlMenu(parent.getPath(True, True))
		self.__addXmlLayout(menu, parent.Layout)

		return separator

	def moveEntry(self, entry, oldparent, newparent, after=None):
		# remove the entry
		oldparent.DeskEntries.remove(entry)
		oldparent.Entries.remove(entry)
		entry.Menus.remove(oldparent)
		sort(oldparent)

		self.__addEntry(newparent, entry, after)
		entry.Menus.append(newparent)
		sort(newparent)

		# create the xml
		old_menu = self.__getXmlMenu(oldparent.getPath(True, True))
		new_menu = self.__getXmlMenu(newparent.getPath(True, True))
		self.__addXmlFilename(old_menu, entry.DesktopFileID, "Exclude")
		self.__addXmlFilename(new_menu, entry.DesktopFileID, "Include")

		# layout stuff
		if after:
			self.__addLayout(oldparent)
			self.__addLayout(newparent)
			self.__addXmlLayout(old_menu, oldparent.Layout)
			self.__addXmlLayout(new_menu, newparent.Layout)

		return entry

	def moveMenu(self, menu, oldparent, newparent, after=None):
		# remove the entry
		oldparent.Submenus.remove(entry)
		oldparent.Entries.remove(entry)
		sort(oldparent)

		self.__addEntry(newparent, menu, after)
		sort(newparent)

		# create the xml
		old_menu = self.__getXmlMenu(oldparent.getPath(True, True))
		new_menu = self.__getXmlMenu(newparent.getPath(True, True))
		self.__addXmlMove(self.doc, os.path.join(oldparent.getPath(True), menu.Name), os.path.join(newparent.getPath(True), menu.Name))

		# layout stuff
		if after:
			self.__addLayout(oldparent)
			self.__addLayout(newparent)
			self.__addXmlLayout(old_menu, oldparent.Layout)
			self.__addXmlLayout(new_menu, newparent.Layout)

		return menu

	def moveSeparator(self, separator, parent, after=None):
		# move the entry
		index = parent.Entries.index(separator)
		parent.Entries.remove(index)

		# add it again
		self.__addEntry(parent, separator, after)

		# create the xml and layout stuff
		menu = self.__getXmlMenu(parent.getPath(True, True))
		self.__addXmlLayout(menu, parent.Layout)

		return separator

	def editEntry(self, entry, name=None, genericname=None, comment=None, command=None, icon=None, term=None, nodisplay=None):
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

		if nodisplay == True:
			deskentry.set("NoDisplay", "true")
		elif nodisplay == False:
			deskentry.set("NoDisplay", "false")

		return entry

	def editMenu(self, menu, name=None, genericname=None, comment=None, icon=None, nodisplay=None):
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

		if nodisplay == True:
			deskentry.set("NoDisplay", "true")
		elif nodisplay == False:
			deskentry.set("NoDisplay", "false")

		return menu

	def hideEntry(self, entry):
		entry = self.editEntry(entry, nodisplay=True)
		for menu in entry.Menus:
			sort(menu)
		return entry

	def unhideEntry(self, entry):
		entry = self.editEntry(entry, nodisplay=False)
		for menu in entry.Menus:
			sort(menu)
		return entry

	def hideMenu(self, menu):
		menu = self.editMenu(menu, nodisplay=True)
		sort(menu.Parent)
		return menu

	def unhideMenu(self, menu):
		menu = self.editMenu(menu, nodisplay=False)
		sort(menu.Parent)
		return menu


	def deleteEntry(self, entry):
		pass

	def deleteMenu(self, menu):
		pass

	def deleteSeparator(self, separator):
		pass


	""" Private Stuff """
	def __saveEntries(self, menu):
		if not menu:
			menu = self.menu
		if isinstance(menu.Directory, MenuEntry):
			menu.Directory.save()
		for entry in menu.getEntries(hidden=True):
			if isinstance(entry, MenuEntry):
				entry.save()
			elif isinstance(entry, Menu):
				self.__saveEntries(entry)

	def __saveMenu(self):
		if not os.path.isdir(os.path.dirname(self.filename)):
			os.makedirs(os.path.dirname(self.filename))
		fd = open(self.filename, 'w')
		fd.write(self.doc.toxml().replace('<?xml version="1.0" ?>\n', ''))
		fd.close()

	def __getFileName(self, name, extension):
		name = self.__getFixedName(name)

		postfix = 0
		#prefix = "xdg-changed-"
		while 1:
			#filename = prefix + name + "-" + str(postfix) + extension
			filename = name + "-" + str(postfix) + extension
			if extension == ".desktop":
				dir = "applications"
			elif extension == ".directory":
				dir = "desktop-directories"
			if not os.path.isfile(os.path.join(xdg_data_dirs[0], dir, filename)):
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
			element = self.doc

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
			node = self.__addXmlMenuElement(element, name)
			if path:
				found = self.__getXmlMenu(path, node)
			else:
				found = node

		return found

	def __addXmlMenuElement(self, element, name):
		node = self.doc.createElement('Menu')
		self.__addXmlTextElement(node, 'Name', name)
		return element.appendChild(node)

	def __addXmlTextElement(self, element, name, text):
		node = self.doc.createElement(name)
		text = self.doc.createTextNode(text)
		node.appendChild(text)
		return element.appendChild(node)

	def __addXmlFilename(self, element, filename, type = "Include"):
		node = self.doc.createElement(type)
		node.appendChild(self.__addXmlTextElement(node, 'Filename', filename))
		return element.appendChild(node)

	def __addXmlMove(self, element, old, new):
		node = self.doc.createElement("Move")
		node.appendChild(self.__addXmlTextElement(node, 'Old', old))
		node.appendChild(self.__addXmlTextElement(node, 'New', new))
		return element.appendChild(node)

	def __addXmlLayout(self, element, layout):
		# remove old layout
		for node in element.childNodes:
			if node.nodeType == xml.dom.Node.ELEMENT_NODE and node.nodeName == 'Layout':
				element.removeChild(node)
				break

		# add new layout
		node = self.doc.createElement("Layout")
		for order in layout.order:
			if order[0] == "Separator":
				child = self.doc.createElement("Separator")
				node.appendChild(child)
			elif order[0] == "Filename":
				child = self.__addXmlTextElement(node, "Filename", order[1])
			elif order[0] == "Menuname":
				child = self.__addXmlTextElement(node, "Menuname", order[1])
			elif order[0] == "Merge":
				child = self.doc.createElement("Merge")
				child.setAttribute("type", order[1])
				node.appendChild(child)
		return element.appendChild(node)

	def __addEntry(self, parent, entry, after):

		if after:
			index = parent.Entries.index(after) + 1
			if index > len(parent.Entries):
				parent.Entries.append(entry)
			else:
				parent.Entries.insert(index, entry)
		else:
			parent.Entries.append(entry)

		if isinstance(entry, Menu):
			parent.Submenus.add(entry)
		elif isinstance(entry, MenuEntry):
			parent.DeskEntries.append(entry)

		return entry

	def __addLayout(self, parent):
		layout = Layout()
		layout.order = []
		layout.show_empty = parent.Layout.show_empty
		layout.inline = parent.Layout.inline
		layout.inline_header = parent.Layout.inline_header
		layout.inline_alias = parent.Layout.inline_alias
		layout.inline_limit = parent.Layout.inline_limit

		layout.order.append(["Merge", "menus"])
		for entry in parent.Entries:
			if isinstance(entry, Menu):
				layout.parseMenuname(entry.Name)
			elif isinstance(entry, MenuEntry):
				layout.parseFilename(entry.DesktopFileID)
			elif isinstance(entry, Separator):
				layout.parseSeparator()
		layout.order.append(["Merge", "files"])

		parent.Layout = layout

		return layout
