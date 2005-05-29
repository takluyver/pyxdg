""" CLass to edit XDG Menus """

from xdg.Menu import *
from xdg.BaseDirectory import *
from xdg.Exceptions import *
from xdg.DesktopEntry import *

import xml.dom.minidom
import os

# XML-Cleanups: Move / Exclude
# FIXME: pass AppDirs/DirectoryDirs around in the edit/move functions
# FIXME: copy functions
# FIXME: More Layout stuff
# FIXME: unod/redo function / remove menu...
# FIXME: Advanced MenuEditing Stuff: LegacyDir/MergeFile
#        Complex Rules/Deleted/OnlyAllocated/AppDirs/DirectoryDirs

class MenuEditor:
	def __init__(self, menu=None, filename=None):
		self.menu = None
		self.filename = None
		self.doc = None
		self.parse(menu, filename)

		# fix for creating two menus with the same name on the fly
		self.filenames = []

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

	def createEntry(self, parent, name, command=None, genericname=None, comment=None, icon=None, terminal=None, after=None, before=None):
		entry = MenuEntry(self.__getFileName(name, ".desktop"))
		entry = self.editEntry(entry, name, genericname, comment, command, icon, terminal)

		self.__addEntry(parent, entry, after, before)

		sort(self.menu)

		return entry

	def createMenu(self, parent, name, genericname=None, comment=None, icon=None, after=None, before=None):
		menu = Menu()
		menu = self.editMenu(menu, name, genericname, comment, icon)

		self.__addEntry(parent, menu, after, before)

		menu.Name = menu.Directory.Filename.replace(".directory", "")
		menu.Layout = parent.DefaultLayout
		menu.DefaultLayout = parent.DefaultLayout

		xml_menu = self.__getXmlMenu(menu.getPath(True, True))
		self.__addXmlTextElement(xml_menu, 'Directory', menu.Directory.Filename)

		sort(self.menu)

		return menu

	def createSeparator(self, parent, after=None, before=None):
		separator = Separator(parent)

		self.__addEntry(parent, separator, after, before)

		sort(self.menu)

		return separator

	def moveEntry(self, entry, oldparent, newparent, after=None, before=None):
		self.__deleteEntry(oldparent, entry, after, before)
		self.__addEntry(newparent, entry, after, before)

		sort(self.menu)

		return entry

	def moveMenu(self, menu, oldparent, newparent, after=None, before=None):
		self.__deleteEntry(oldparent, menu, after, before)
		self.__addEntry(newparent, menu, after, before)

		root_menu = self.__getXmlMenu(self.menu.Name)
		if oldparent.getPath(True) != newparent.getPath(True):
			self.__addXmlMove(root_menu, os.path.join(oldparent.getPath(True), menu.Name), os.path.join(newparent.getPath(True), menu.Name))

		sort(self.menu)

		return menu

	def moveSeparator(self, separator, parent, after=None, before=None):
		self.__deleteEntry(parent, separator, after, before)
		self.__addEntry(parent, separator, after, before)

		sort(self.menu)

		return separator

	def editEntry(self, entry, name=None, genericname=None, comment=None, command=None, icon=None, terminal=None, nodisplay=None):
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
			deskentry.set("Exec", command)
		if icon:
			deskentry.set("Icon", icon)

		if terminal == True:
			deskentry.set("Terminal", "true")
		elif terminal == False:
			deskentry.set("Terminal", "false")

		if nodisplay == True:
			deskentry.set("NoDisplay", "true")
		elif nodisplay == False:
			deskentry.set("NoDisplay", "false")

		if len(entry.Parents) > 0:
			sort(self.menu)

		return entry

	def editMenu(self, menu, name=None, genericname=None, comment=None, icon=None, nodisplay=None):
		# Hack for legacy dirs
		if isinstance(menu.Directory, MenuEntry) and menu.Directory.Filename == ".directory":
			xml_menu = self.__getXmlMenu(menu.getPath(True, True))
			self.__addXmlTextElement(xml_menu, 'Directory', menu.Name + ".directory")
			menu.Directory.setAttributes(menu.Name + ".directory")
		# Hack for New Entries
		elif not isinstance(menu.Directory, MenuEntry):
			menu.Directory = MenuEntry(self.__getFileName(name, ".directory").replace("/", ""))

		deskentry = menu.Directory.DesktopEntry

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

		if isinstance(entry.Parent, Menu):
			sort(self.menu)

	def deleteEntry(self, entry):
		if "delete" in self.getActions(entry):
			self.__deleteFile(entry.DesktopEntry.filename)
			for parent in entry.Parents:
				self.__deleteEntry(parent, entry)
			sort(self.menu)
		return entry

	def revertEntry(self, entry):
		if "revert" in self.getActions(entry):
			self.__deleteFile(entry.DesktopEntry.filename)
			for parent in entry.Parents:
				index = parent.Entries.index(entry)
				parent.Entries[index] = entry.Original
				index = parent.DeskEntries.index(entry)
				parent.DeskEntries[index] = entry.Original
			sort(self.menu)
		return entry

	def deleteMenu(self, menu):
		if "delete" in self.getActions(menu):
			self.__deleteFile(menu.Directory.DesktopEntry.filename)
			self.__deleteEntry(menu.Parent, menu)
			xml_menu = self.__getXmlMenu(menu.getPath(True, True))
			xml_menu.parentNode.removeChild(xml_menu)
			sort(self.menu)
		return menu

	def revertMenu(self, menu):
		if "revert" in self.getActions(menu):
			self.__deleteFile(menu.Directory.DesktopEntry.filename)
			menu.Directory = menu.Directory.Original
			sort(self.menu)
		return menu

	def deleteSeparator(self, separator):
		self.__deleteEntry(separator.Parent, separator)

		sort(self.menu)

		return separator

	""" Private Stuff """
	def getActions(self, entry):
		if isinstance(entry, Menu):
			if not isinstance(entry.Directory, MenuEntry):
				return "none"
			elif entry.Directory.Type == "Both":
				return "revert"
			elif entry.Directory.Type == "User":
				xml_menu = self.__getXmlMenu(entry.getPath(True, True), False)
				if not xml_menu:
					return "revert"
				else:
					for node in self.__getXmlNodesByName("Directory", xml_menu):
						return ["delete", "revert"]
					return "delete"

		elif isinstance(entry, MenuEntry):
			if entry.Type == "Both":
				return "revert"
			elif entry.Type == "User":
				return "delete"

		return "none"

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
		postfix = 0
		#prefix = "xdg-changed-"
		while 1:
			#filename = prefix + name + "-" + str(postfix) + extension
			if postfix == 0:
				filename = name + extension
			else:
				filename = name + "-" + str(postfix) + extension
			if extension == ".desktop":
				dir = "applications"
			elif extension == ".directory":
				dir = "desktop-directories"
			if not filename in self.filenames and not \
				os.path.isfile(os.path.join(xdg_data_dirs[0], dir, filename)):
				self.filenames.append(filename)
				break
			else:
				postfix += 1

		return filename

	def __getXmlMenu(self, path, create=True, element=None):
		if not element:
			element = self.doc

		if "/" in path:
			(name, path) = path.split("/", 1)
		else:
			name = path
			path = ""

		found = None
		for node in self.__getXmlNodesByName("Menu", element):
			for child in self.__getXmlNodesByName("Name", node):
				if child.childNodes[0].nodeValue == name:
					if path:
						found = self.__getXmlMenu(path, create, node)
					else:
						found = node
					break
			if found:
				break
		if not found and create == True:
			node = self.__addXmlMenuElement(element, name)
			if path:
				found = self.__getXmlMenu(path, create, node)
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
		# remove old filenames
		for node in self.__getXmlNodesByName(["Include", "Exclude"], element):
			if node.childNodes[0].nodeName == "Filename" and node.childNodes[0].childNodes[0].nodeValue == filename:
				element.removeChild(node)

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
		for node in self.__getXmlNodesByName("Layout", element):
			element.removeChild(node)

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

	def __getXmlNodesByName(self, name, element):
		for	child in element.childNodes:
			if child.nodeType == xml.dom.Node.ELEMENT_NODE and child.nodeName in name:
				yield child

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

	def __addEntry(self, parent, entry, after=None, before=None):
		if after or before:
			if after:
				index = parent.Entries.index(after) + 1
			elif before:
				index = parent.Entries.index(before)
			parent.Entries.insert(index, entry)
		else:
			parent.Entries.append(entry)

		xml_parent = self.__getXmlMenu(parent.getPath(True, True))

		if isinstance(entry, MenuEntry):
			parent.DeskEntries.append(entry)
			entry.Parents.append(parent)
			self.__addXmlFilename(xml_parent, entry.DesktopFileID, "Include")
		elif isinstance(entry, Menu):
			parent.addSubmenu(entry)

		if after or before:
			self.__addLayout(parent)
			self.__addXmlLayout(xml_parent, parent.Layout)

	def __deleteEntry(self, parent, entry, after=None, before=None):
		parent.Entries.remove(entry)

		xml_parent = self.__getXmlMenu(parent.getPath(True, True))

		if isinstance(entry, MenuEntry):
			entry.Parents.remove(parent)
			parent.DeskEntries.remove(entry)
			self.__addXmlFilename(xml_parent, entry.DesktopFileID, "Exclude")
		elif isinstance(entry, Menu):
			parent.Submenus.remove(entry)

		if after or before:
			self.__addLayout(parent)
			self.__addXmlLayout(xml_parent, parent.Layout)

	def __deleteFile(self, filename):
		try:
			os.remove(filename)
		except OSError:
			pass
		try:
			self.filenames.remove(filename)
		except IndexError:
			pass
