"""
Implementation of the XDG Menu Specification Version 0.7
http://www.freedesktop.org/standards/menu-spec/

Not Supported (and not planed):
    - <LegacyDir>, <KDELegacyDirs>
"""

from __future__ import generators
import re, os, xml.dom.minidom

from xdg.BaseDirectory import *
from xdg.DesktopEntry import *
from xdg.Exceptions import *

class Menu:
	def __init__(self):
		# Public stuff
		self.Name = ""
		self.Entries = []
#		self.Parent = ""

		# Private stuff, only needed for parsing
		self.AppDirs = []
		self.DefaultLayout = ""
		self.Deleted = "notset"
		self.DeskEntries = []
		self.Directory = []
		self.DirectoryDirs = []
		self.Layout = ""
		self.Moves = []
		self.OnlyUnallocated = "notset"
		self.Rules = []
		self.Submenus = []

		# caching
		self.cache = dict()

	def __str__(self):
		return self.Name

	def __add__(self, other):
		for dir in other.getAppDirs():
			self.addAppDir(dir)

		if self.getDeleted() == "notset":
			self.setDeleted(other.getDeleted())

		for entry in other.getDeskEntries():
			self.addDeskEntry(entry)

		for entry in other.getDirectories():
			self.addDirectory(entry)

		for dir in other.getDirectoryDirs():
			self.addDirectoryDir(dir)

		for move in other.getMoves():
			self.addMove(move)

		if self.getOnlyUnallocated() == "notset":
			self.setOnlyUnallocated(other.getOnlyUnallocated())

		for rule in other.getRules():
			self.addRule(rule)

		for submenu in other.getSubmenus():
			self.addSubmenu(submenu)

		return self

	def __cmp__(self, other):
		if isinstance(other, unicode):
			return cmp(self.Name, other)
		else:
			return cmp(self.Name, other.Name)

	def setWM(self, wm):
		for entry in self.Entries:
			if isinstance(entry, MenuEntry):
				if ( entry.DesktopEntry.hasKey("OnlyShowIn") and not wm in entry.DesktopEntry.getOnlyShowIn()) \
				or ( entry.DesktopEntry.hasKey("NotShowIn") and wm in entry.DesktopEntry.getNotShowIn()):
					entry.Show = False
				else:
					entry.Show = True
			elif isinstance(entry, Menu):
				entry.setWM(wm)

	def setLocale(self, lc_messages, level = 0):
		for entry in self.Entries:
			if isinstance(entry, MenuEntry):
				entry.DesktopEntry.setLocale(lc_messages)
				entry.Name = entry.DesktopEntry.getName()
			elif isinstance(entry, Menu):
				level += 1
				entry.Directory.setLocale(lc_messages)
				entry.cache = dict()
				entry.setLocale(lc_messages, level)
				level -= 1
		if level == 0:
			print "fucking bullshit"
			sort(self)

	def getEntries(self):
		for entry in self.Entries:
			if isinstance(entry, MenuEntry) and entry.Show == True:
				yield entry
			elif isinstance(entry, Menu):
				yield entry

	def searchEntry(self, filename, deep = True, action = "echo"):
		for entry in self.DeskEntries:
			if entry.DesktopEntry.getFileName() == filename:
				if action == "echo":
					print self.getPath()
					return ""
				elif action == "return":
					return self.getPath()
		if deep == True:
			for submenu in self.Submenus:
				submenu.searchEntry(filename, deep, action)

	def getPath(self, org = False):
		parent = self
		names=[]
		while 1:
			if org:
				names.append(parent.Name)
			else:
				names.append(parent.getName())
			try:
				parent = parent.Parent
			except AttributeError:
				break
		names.reverse()
		path = ""
		for name in names:
			path = path + "/" + name
		return path

	def getName(self):
		if self.cache.has_key("name"):
			return self.cache["name"]

		value = self.Directory.getName()
		if value:
			return value
			self.cache["name"] = value
		else:
			return self.Name
			self.cache["name"] = self.Name

	def getGenericName(self):
		value = self.Directory.getGenericName()
		if value:
			return value
		else:
			return ""

	def getComment(self):
		value = self.Directory.getComment()
		if value:
			return value
		else:
			return ""

	def getIcon(self):
		value = self.Directory.getIcon()
		if value:
			return value
		else:
			return ""

	def addAppDir(self, dir, pos = -1):
		if not dir in self.getAppDirs():
			if pos == -1:
				self.AppDirs.append(dir)
			else:
				self.AppDirs.insert(pos,dir)
	def getAppDirs(self, reverse = False):
		dirs = self.AppDirs[:]
		if reverse:
			dirs.reverse()
		return dirs

	def setDeleted(self, boolean):
		self.Deleted = boolean
	def getDeleted(self):
		return self.Deleted

	def addDeskEntry(self, entry):
		if not entry in self.getDeskEntries():
			self.DeskEntries.append(entry)
	def getDeskEntries(self):
		return self.DeskEntries

	def addDirectory(self, entry):
		if not entry in self.getDirectories():
			self.Directory.append(entry)
	def setDirectory(self, entry):
		self.Directory = entry
	def getDirectories(self):
		return self.Directory

	def addDirectoryDir(self, dir, pos = -1):
		if not dir in self.getDirectoryDirs():
			if pos == -1:
				self.DirectoryDirs.append(dir)
			else:
				self.DirectoryDirs.insert(pos,dir)
	def getDirectoryDirs(self, reverse = False):
		dirs = self.DirectoryDirs[:]
		if reverse:
			dirs.reverse()
		return dirs

	def addMove(self, newmove):
		for move in self.getMoves():
			if newmove.Old == move.Old:
				move = newmove
				break
		else:
			self.Moves.append(newmove)
	def getMoves(self):
		return self.Moves

	def setOnlyUnallocated(self, boolean):
		self.OnlyUnallocated = boolean
	def getOnlyUnallocated(self):
		return self.OnlyUnallocated

	def addRule(self, rule):
		self.Rules.append(rule)
	def getRules(self):
		return self.Rules

	def addSubmenu(self, newmenu):
		for submenu in self.getSubmenus():
			if submenu == newmenu:
				submenu += newmenu
				break
		else:
			self.Submenus.append(newmenu)
			newmenu.Parent = self

	def getSubmenus(self):
		return self.Submenus

	def getSubmenu(self, name):
		try:
			index = self.getSubmenus().index(name)
			return self.getSubmenus()[index]
		except ValueError:
			return ""

	def removeSubmenu(self, newmenu):
		self.Submenus.remove(newmenu)


class Move:
	"A move operation"
	def __init__(self, node):
		self.Old = ""
		self.New = ""
		self.parseNode(node)

	def __eq__(self, other):
		return cmp(self.Old, other.Old)

	def parseNode(self, node):
		for child in node.childNodes:
			if child.nodeType == xml.dom.Node.ELEMENT_NODE:
				if child.tagName == "Old":
					self.parseOld(child.childNodes[0].nodeValue)
				elif child.tagName == "New":
					self.parseNew(child.childNodes[0].nodeValue)

	def parseOld(self, value):
		self.Old = value
	def parseNew(self, value):
		self.New = value


class Layout:
	"Menu Layout class"
	def __init__(self, node = ""):
		self.order = []
		if node:
			self.show_empty = node.getAttribute("show_empty") or "false"
			self.inline = node.getAttribute("inline") or "false"
			self.inline_limit = node.getAttribute("inline_limit") or "4"
			self.inline_header = node.getAttribute("inline_header") or "true"
			self.inline_alias = node.getAttribute("inline_alias") or "false"
			self.parseNode(node)
		else:
			self.show_empty = "false"
			self.inline = "false"
			self.inline_limit = "4"
			self.inline_headers = "true"
			self.inline_alias = "false"
			self.order.append(["Merge", "menus"])
			self.order.append(["Merge", "files"])

	def parseNode(self, node):
		for child in node.childNodes:
			if child.nodeType == xml.dom.Node.ELEMENT_NODE:
				if child.tagName == "Menuname":
					self.parseMenuname(child)
				elif child.tagName == "Seperator":
					self.parseSeperator(child)
				elif child.tagName == "Filename":
					self.parseFilename(child)
				elif child.tagName == "Merge":
					self.parseMerge(child)

	def parseMenuname(self, child):
		self.order.append([
			"Menuname",
			child.childNodes[0].nodeValue,
			child.getAttribute("show_empty"),
			child.getAttribute("inline"),
			child.getAttribute("inline_lmit"),
			child.getAttribute("inline_header"),
			child.getAttribute("inline_alias")
		])

	def parseSeperator(self, child):
		self.order.append(["Seperator"])

	def parseFilename(self, child):
		self.order.append(["Filename", child.childNodes[0].nodeValue])

	def parseMerge(self, child):
		self.order.append(["Merge", child.getAttribute("type")])


class Rule:
	"Inlcude / Exclude Rules Class"
	def __init__(self, type, node):
		# Type is Include or Exclude
		self.Type = type
		# Rule is a python expression
		self.Rule = ""

		# Private attributes, only needed for parsing
		self.Depth = 0
		self.Expr = [ "or" ]
		self.New = True

		# Begin parsing
		self.parseNode(node)

	def __str__(self):
		return self.Rule

	def parseNode(self, node):
		for child in node.childNodes:
			if child.nodeType == xml.dom.Node.ELEMENT_NODE:
				if child.tagName == 'Filename':
					self.parseFilename(child.childNodes[0].nodeValue)
				elif child.tagName == 'Category':
					self.parseCategory(child.childNodes[0].nodeValue)
				elif child.tagName == 'All':
					self.parseAll()
				elif child.tagName == 'And':
					self.parseAnd(child)
				elif child.tagName == 'Or':
					self.parseOr(child)
				elif child.tagName == 'Not':
					self.parseNot(child)

	def parseNew(self, set = True):
		if not self.New:
			self.Rule += " " + self.Expr[self.Depth] + " "
		if not set:
			self.New = True
		elif set:
			self.New = False

	def parseFilename(self, value):
		self.parseNew()
		self.Rule += "entry.DesktopFileID == '" + value + "'"

	def parseCategory(self, value):
		self.parseNew()
		self.Rule += "'" + value + "' in categories"

	def parseAll(self):
		self.parseNew()
		self.Rule += "True"

	def parseAnd(self, node):
		self.parseNew(False)
		self.Rule += "("
		self.Depth += 1
		self.Expr.append("and")
		self.parseNode(node)
		self.Depth -= 1
		self.Expr.pop()
		self.Rule += ")"

	def parseOr(self, node):
		self.parseNew(False)
		self.Rule += "("
		self.Depth += 1
		self.Expr.append("or")
		self.parseNode(node)
		self.Depth -= 1
		self.Expr.pop()
		self.Rule += ")"

	def parseNot(self, node):
		self.parseNew(False)
		self.Rule += "not ("
		self.Depth += 1
		self.Expr.append("or")
		self.parseNode(node)
		self.Depth -= 1
		self.Expr.pop()
		self.Rule += ")"


class MenuEntry:
	"Wrapper for 'Menu Style' Desktop Entries"
	def __init__(self, Entry = "", Id = "", Allocated = False):
		self.DesktopEntry = Entry
		self.DesktopFileID = Id
		self.Allocated = Allocated
		# to implement the OnlyShowIn/NotShowIn keys
		self.Show = True
		# Caching
		if self.DesktopEntry:
			self.Name = self.DesktopEntry.getName()

	def __cmp__(self, other):
		if isinstance(other, MenuEntry):
			return cmp(self.Name, other.Name)
		elif isinstance(other, Menu):
			return cmp(self.Name, other.getName())

	def __ne__(self, other):
		return cmp(self.DesktopFileID, other.DesktopFileID)

	def __str_(self):
		return self.DesktopFileID()


class Seperator:
	"Just a dummy class for Seperators"
	pass


tmp = {}
tmp["mergeFiles"] = []

def parse(file = ""):
	# if no file given, try default files
	if not file:
		dirs = xdg_config_dirs
		for dir in dirs:
			file = os.path.join (dir, "menus" , "applications.menu")
			if os.path.isdir(dir) and os.path.isfile(file):
				break

	# convert to absolute path
	if not os.path.isabs(file):
		file = os.path.abspath(file)

	# check if it is a .menu file
	if not re.search('\.menu$', file):
		raise ParsingError('Not a .menu file', file)

	# create xml parser
	try:
		doc = xml.dom.minidom.parse(file)
	except IOError:
		raise ParsingError('File not found', file)
	except xml.parsers.expat.ExpatError:
		raise ParsingError('Not a valid .menu file', file)

	# parse menufile
	tmp["Root"] = ""
	__preparse(doc, file)
	__parse(doc, tmp["Root"])
	__postparse(tmp["Root"])

	# generate the menu
	cache = DesktopEntryCache()
	__genmenuNotOnlyAllocated(tmp["Root"], cache)
	__genmenuOnlyAllocated(tmp["Root"], cache)

	# and finally sort
	sort(tmp["Root"])

	return tmp["Root"]

def __preparse(doc, file):
	# extrace path and basename from file
	path = os.path.dirname(file)
	(basename, None) = re.split(".[^.]*$", os.path.basename(file))

	# replace default dir stuff
	for name in [ "DefaultAppDirs", "DefaultDirectoryDirs", "DefaultMergeDirs" ]:
		if name == "DefaultMergeDirs":
			dirs = xdg_config_dirs
		else:
			dirs = xdg_data_dirs
		dirs.reverse()

		nodes = doc.getElementsByTagName(name)
		for node in nodes:
			parent = node.parentNode
			for dir in dirs:
				if name == "DefaultAppDirs":
					value = os.path.join(dir, "applications")
				elif name == "DefaultDirectoryDirs":
					value = os.path.join(dir, "desktop-directories")
				elif name == "DefaultMergeDirs":
					value = os.path.join(dir, "menus", basename + "-merged")

				entry = doc.createElement(re.sub("Default", "", name).replace("Dirs", "Dir"))
				entry.appendChild(doc.createTextNode(value))
				parent.insertBefore(entry, node)
			parent.removeChild(node)

	# remove duplicate stuff, convert to absolute path and remove not existing path
	for name in [ "MergeDir", "MergeFile", "DirectoryDir", "AppDir" ]:
		values  = []
		parents = []
		nodes = doc.getElementsByTagName(name)
		for node in nodes:
			if not os.path.isabs(node.childNodes[0].nodeValue):
				node.childNodes[0].nodeValue = os.path.join(path, node.childNodes[0].nodeValue)
			value = node.childNodes[0].nodeValue
			if ( value in values and node.parentNode in parents ) \
			or ( not os.path.exists(value) ) \
			or ( name != "MergeFile" and not os.path.isdir(value) ) \
			or ( name == "MergeFile" and not os.path.isfile(value) ):
				node.parentNode.removeChild(node)
			else:
				parents.append(node.parentNode)
				values.append(value)

def __parse(node, parent = ""):
	for child in node.childNodes:
		if child.nodeType == xml.dom.Node.ELEMENT_NODE:
			if child.tagName == 'Menu':
				__parseMenu(child, parent)
			elif child.tagName == 'AppDir':
				parent.addAppDir(child.childNodes[0].nodeValue)
			elif child.tagName == 'DirectoryDir':
				parent.addDirectoryDir(child.childNodes[0].nodeValue)
			elif child.tagName == 'Name' :
				parent.Name = child.childNodes[0].nodeValue
			elif child.tagName == 'Directory' :
				parent.addDirectory(child.childNodes[0].nodeValue)
			elif child.tagName == 'OnlyUnallocated':
				parent.setOnlyUnallocated(True)
			elif child.tagName == 'NotOnlyUnallocated':
				parent.setOnlyUnallocated(False)
			elif child.tagName == 'Deleted':
				parent.setDeleted(True)
			elif child.tagName == 'NotDeleted':
				parent.setDeleted(False)
			elif child.tagName == 'Include' or child.tagName == 'Exclude':
				parent.addRule(Rule(child.tagName, child))
			elif child.tagName == 'MergeFile':
				__parseMergeFile(child)
			elif child.tagName == 'MergeDir':
				__parseMergeDir(child)
			elif child.tagName == 'Move':
				parent.addMove(Move(child))
			elif child.tagName == 'X-Python-MergeEnd':
				__parseMergeEnd()
			elif child.tagName == 'Layout':
				if len(child.childNodes) > 1:
					parent.Layout = Layout(child)
			elif child.tagName == 'DefaultLayout':
				if len(child.childNodes) > 1:
					parent.DefaultLayout = Layout(child)

def __postparse(menu):
	# parse move operations
	for move in menu.getMoves():
		move_from_menu = menu.getSubmenu(move.Old)
		if move_from_menu:
			move_to_menu = menu.getSubmenu(move.New)
			if move_to_menu:
				move_to_menu += move_from_menu
				menu.removeSubmenu(move_from_menu)
			else:
				move_from_menu.Name = move.New

	# a list of menus to remove
	remove = []

	# Layout Tags
	if not menu.Layout or not menu.DefaultLayout:
		if menu.DefaultLayout:
			menu.Layout = menu.DefaultLayout
		elif menu.Layout:
			if hasattr(menu, "Parent"):
				menu.DefaultLayout = menu.Parent.DefaultLayout
			else:
				menu.DefaultLayout = Layout()
		else:
			if hasattr(menu, "Parent"):
				menu.Layout = menu.Parent.DefaultLayout
				menu.DefaultLayout = menu.Parent.DefaultLayout
			else:
				menu.Layout = Layout()
				menu.DefaultLayout = Layout()

	# go recursive through all menus
	for submenu in menu.getSubmenus():
		# notset required for move operations
		if submenu.getDeleted() == "notset":
			submenu.setDeleted(False)
		if submenu.getOnlyUnallocated() == "notset":
			submenu.setOnlyUnallocated(False)
		# Delete <Deleted> menus
		if submenu.getDeleted() == True:
			remove.append(submenu)
			continue
		# add parent's app/directory dirs
		for dir in menu.getAppDirs(reverse = True):
			submenu.addAppDir(dir, 0)
		for dir in menu.getDirectoryDirs(reverse = True):
			submenu.addDirectoryDir(dir, 0)

		# enter submenus
		__postparse(submenu)

	# get the valid .directory file out of the list
	entry = ""
	for directory in menu.getDirectories():
		for dir in menu.getDirectoryDirs():
			if os.path.exists(os.path.join(dir, directory)):
				try:
					entry = DesktopEntry()
					entry.parse(os.path.join(dir, directory))
				except:
					pass
	if entry:
		menu.setDirectory(entry)
	else:
		menu.setDirectory(DesktopEntry())
	
	# remove menus
	for submenu in remove:
		menu.removeSubmenu(submenu)

# Menu parsing stuff
def __parseMenu(child, parent):
	m = Menu()
	__parse(child, m)
	if parent:
		parent.addSubmenu(m)
	else:
		tmp["Root"] = m

# Merge Stuff
def __parseMergeFile(child):
	__mergeFile(child.childNodes[0].nodeValue, child)

def __parseMergeDir(child):
	files = os.listdir(child.childNodes[0].nodeValue)
	for file in files:
		if re.search('\.menu', file):
			__mergeFile(os.path.join(child.childNodes[0].nodeValue, file), child)

def __mergeFile(file, child):
	# load file
	try:
		doc = xml.dom.minidom.parse(file)
	except IOError:
		raise ParsingError('File not found', file)
	except xml.parsers.expat.ExpatError:
		raise ParsingError('Not a valid .menu file', file)

	# check for infinite loops
	if file in tmp["mergeFiles"]:
		raise ParsingError('Infinite MergeFile loop detected', file)

	tmp["mergeFiles"].append(file)

	# append file
	__preparse(doc, file)
	next = child.nextSibling
	for node in doc.childNodes[1].childNodes:
		if node.nodeType == xml.dom.Node.ELEMENT_NODE:
			if node.tagName != "Name":
				child.parentNode.insertBefore(node, next)

	# Make endnode to pop __mergeFiles again
	endnode = doc.createElement("X-Python-MergeEnd")
	child.parentNode.insertBefore(endnode, next)

def __parseMergeEnd():
	tmp["mergeFiles"].pop()

# Finally generate the menu
def __genmenuNotOnlyAllocated(menu, cache):
	if not menu.getOnlyUnallocated():
		cache.addEntries(menu.getAppDirs())
		for entry in cache.getEntries(menu.getAppDirs()):
			categories = entry.DesktopEntry.getCategories()
			inc = False
			for rule in menu.getRules():
				if eval(rule.Rule):
					if rule.Type == "Include":
						inc = True
					else:
						inc = False
			if inc == True:
				entry.Allocated = True
				menu.addDeskEntry(entry)

	for submenu in menu.getSubmenus():
		__genmenuNotOnlyAllocated(submenu, cache)

def __genmenuOnlyAllocated(menu, cache):
	if menu.getOnlyUnallocated():
		cache.addEntries(menu.getAppDirs())
		for entry in cache.getEntries(menu.getAppDirs()):
			categories = entry.DesktopEntry.getCategories()
			if entry.Allocated == True:
				continue
			inc = False
			for rule in menu.Rules:
				if eval(rule.Rule):
					if rule.Type == "Include":
						inc = True
					else:
						inc = False
			if inc == True:
				menu.addDeskEntry(entry)

	for submenu in menu.getSubmenus():
		__genmenuOnlyAllocated(submenu, cache)

# And sorting ...
def sort(menu):
	menu.Entries = []

	remove = []
	for submenu in menu.getSubmenus():
		sort(submenu)
		if len(submenu.Entries) == 0 and submenu.Layout.show_empty == "false":
			remove.append(submenu)

	for submenu in remove:
		menu.removeSubmenu(submenu)

	menu.Submenus.sort()
	for submenu in menu.getSubmenus():
		menu.Entries.append(submenu)
	menu.DeskEntries.sort()
	for entry in menu.getDeskEntries():
		menu.Entries.append(entry)

class DesktopEntryCache:
	"Class to cache Desktop Entries"
	def __init__(self):
		self.cacheEntries = {}

	def addEntries(self, dirs):
		for dir in dirs:
			if not self.cacheEntries.has_key(dir):
				self.cacheEntries[dir] = []
				self.__addFiles(dir, "")

	def __addFiles(self, dir, subdir):
		files = os.listdir(os.path.join(dir,subdir))
		for file in files:
			if re.search('\.desktop', file):
				try:
					deskentry = DesktopEntry()
					deskentry.parse(os.path.join(dir, subdir, file))
					if not deskentry.getHidden() \
					and not deskentry.getNoDisplay():
						entry = MenuEntry(deskentry, re.sub("/", "-", os.path.join(subdir,file)))
						self.cacheEntries[dir].append(entry)
				except:
					pass
			elif os.path.isdir(os.path.join(dir,subdir,file)):
				self.__addFiles(dir, os.path.join(subdir,file))

	def getEntries(self, dirs):
		list = []
		for dir in dirs:
			if self.cacheEntries.has_key(dir):
				for entry in self.cacheEntries[dir]:
					if not entry in list:
						list.append(entry)
		return list
