"""
Implementation of the XDG Menu Specification Version 1.0.draft-1
http://standards.freedesktop.org/menu-spec/
"""

from __future__ import generators
import os, xml.dom.minidom

from xdg.BaseDirectory import *
from xdg.DesktopEntry import *
from xdg.Exceptions import *

import xdg.Locale
import xdg.Config
import xdg.IconTheme

ELEMENT_NODE = xml.dom.Node.ELEMENT_NODE

class Menu:
	def __init__(self):
		# Public stuff
		self.Name = ""
		self.Entries = []
		self.Doc = ""
		self.Filename = ""
#		self.Parent = ""

		# for getHidden() / getNoDisplay()
		self.Show = True
		self.Visible = 0

		# Private stuff, only needed for parsing
		self.AppDirs = []
		self.DefaultLayout = ""
		self.Deleted = False
		self.DeskEntries = []
		self.CacheDeskEntries = []
		self.Directory = []
		self.DirectoryDirs = []
		self.Layout = ""
		self.Moves = []
		self.OnlyUnallocated =  False
		self.Rules = []
		self.Submenus = []

	def __str__(self):
		return self.Name

	def __add__(self, other):
		for dir in other.getAppDirs():
			self.addAppDir(dir)

		self.Deleted = other.Deleted

		for entry in other.getDirectories():
			self.addDirectory(entry)

		for dir in other.getDirectoryDirs():
			self.addDirectoryDir(dir)

		for move in other.getMoves():
			self.addMove(move)

		self.OnlyUnallocated = other.OnlyUnallocated

		for rule in other.getRules():
			self.addRule(rule)

		for submenu in other.Submenus:
			self.addSubmenu(submenu)

		return self

	def __cmp__(self, other):
		return cmp(self.getName(), other.getName())

	def __eq__(self,other):
		if self.Name == str(other):
			return True
		else:
			return False

	def getEntries(self, all = False):
		for entry in self.Entries:
			if all == True:
				yield entry
			elif entry.Show == True:
				yield entry

	def searchEntry(self, filename, deep = True, action = "echo"):
		for entry in self.Entries:
			if isinstance(entry, MenuEntry):
				if entry.DesktopEntry.getFileName() == filename:
					if action == "echo":
						print self.getPath()
						return ""
					elif action == "return":
						return self.getPath()
			elif isinstance(entry, Menu) and deep == True:
				for submenu in self.Submenus:
					submenu.searchEntry(filename, deep, action)

	def getPath(self, org = False, toplevel = False):
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
		if toplevel == False:
			names.pop(0)
		for name in names:
			path = os.path.join(path, name)
		return path

	def getName(self):
		if self.Directory:
			try:
				return self.Directory.getName()
			except:
				return self.Name
		else:
			return self.Name

	def getGenericName(self):
		try:
			return self.Directory.getGenericName()
		except:
			return ""

	def getComment(self):
		try:
			return self.Directory.getComment()
		except:
			return ""

	def getIcon(self):
		try:
			value = self.Directory.getIcon()
			return xdg.IconTheme.getIconPath(value)
		except:
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

	def addDeskEntry(self, entry):
		self.DeskEntries.append(entry)
	def getDeskEntries(self):
		return self.DeskEntries
	def getDeskEntry(self, name):
		try:
			index = self.getDeskEntries().index(name)
			return self.getDeskEntries()[index]
		except ValueError:
			return ""

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
		# parses recursive menus
		array = name.split("/")
		try:
			index = self.getSubmenus().index(array[0])
			if len(array) > 1:
				return self.getSubmenus()[index].getSubmenu(array[1])
			else:
				return self.getSubmenus()[index]
		except ValueError:
			return ""
	def removeSubmenu(self, newmenu):
		# parse recursive menus
		try:
			self.Submenus.remove(newmenu)
			return True
		except:
			for submenu in self.Submenus:
				value = submenu.removeSubmenu(newmenu)
				if value == True:
					break

class Move:
	"A move operation"
	def __init__(self, node):
		self.Old = ""
		self.New = ""
		self.parseNode(node)

	def __cmp__(self, other):
		return cmp(self.Old, other.Old)

	def parseNode(self, node):
		for child in node.childNodes:
			if child.nodeType == ELEMENT_NODE:
				if child.tagName == "Old":
					try:
						self.parseOld(child.childNodes[0].nodeValue)
					except IndexError:
						raise ValidationError('Old cannot be empty', '??')                                            
				elif child.tagName == "New":
					try:
						self.parseNew(child.childNodes[0].nodeValue)
					except IndexError:
						raise ValidationError('New cannot be empty', '??')                                            

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
			self.inline_limit = node.getAttribute("inline_limit") or 4
			self.inline_header = node.getAttribute("inline_header") or "true"
			self.inline_alias = node.getAttribute("inline_alias") or "false"
			self.inline_limit = int(self.inline_limit)
			self.parseNode(node)
		else:
			self.show_empty = "false"
			self.inline = "false"
			self.inline_limit = 4
			self.inline_headers = "true"
			self.inline_alias = "false"
			self.order.append(["Merge", "menus"])
			self.order.append(["Merge", "files"])

	def parseNode(self, node):
		for child in node.childNodes:
			if child.nodeType == ELEMENT_NODE:
				if child.tagName == "Menuname":
					self.parseMenuname(child)
				elif child.tagName == "Separator":
					self.parseSeparator(child)
				elif child.tagName == "Filename":
					self.parseFilename(child)
				elif child.tagName == "Merge":
					self.parseMerge(child)

	def parseMenuname(self, child):
		self.order.append([
			"Menuname",
			child.childNodes[0].nodeValue,
			child.getAttribute("show_empty") or "false",
			child.getAttribute("inline") or "false",
			child.getAttribute("inline_limit") or 4,
			child.getAttribute("inline_header") or "true",
			child.getAttribute("inline_alias") or "false"
		])
		self.order[-1][4] = int(self.order[-1][4])

	def parseSeparator(self, child):
		self.order.append(["Separator"])

	def parseFilename(self, child):
		try:
			self.order.append(["Filename", child.childNodes[0].nodeValue])
		except IndexError:
			raise ValidationError('Filename cannot be empty')

	def parseMerge(self, child):
		self.order.append(["Merge", child.getAttribute("type")])


class Rule:
	"Inlcude / Exclude Rules Class"
	def __init__(self, type, node = None):
		# Type is Include or Exclude
		self.Type = type
		# Rule is a python expression
		self.Rule = ""

		# Private attributes, only needed for parsing
		self.Depth = 0
		self.Expr = [ "or" ]
		self.New = True

		# Begin parsing
		if node != None:
			self.parseNode(node)
			self.compile()

	def __str__(self):
		return self.Rule

	def compile(self):
		exec("""
def do(entries, type, run):
    for entry in entries:
		if run == 2 and entry.MatchedInclude == True \
		or entry.Allocated == True:
			continue
		elif %s:
		    if type == "Include":
				entry.Add = True
				entry.MatchedInclude = True
		    else:
				entry.Add = False
    return entries
""" % self.Rule) in self.__dict__

	def parseNode(self, node):
		for child in node.childNodes:
			if child.nodeType == ELEMENT_NODE:
				if child.tagName == 'Filename':
					try:
						self.parseFilename(child.childNodes[0].nodeValue)
					except IndexError:
						raise ValidatingError('Filename cannot be empty', "???")
				elif child.tagName == 'Category':
					try:
						self.parseCategory(child.childNodes[0].nodeValue)
					except IndexError:
						raise ValidatingError('Category cannot be empty', "???")
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
		self.Rule += "entry.DesktopFileID == '%s'" % value.strip()

	def parseCategory(self, value):
		self.parseNew()
		self.Rule += "'%s' in entry.Categories" % value.strip()

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
	def __init__(self, Entry, Id = "", Allocated = False):
		self.DesktopEntry = Entry
		self.DesktopFileID = Id
		self.Allocated = Allocated
		self.Add = False
		self.MatchedInclude = False
		# Needed for getHidden() / getNoDisplay()
		self.Show = True
		# Caching
		self.Categories = ""
		self.cache()

	def cache(self):
		self.Categories = self.DesktopEntry.getCategories()

	def __cmp__(self, other):
		return cmp(self.DesktopEntry.getName(), other.DesktopEntry.getName())

	def __eq__(self,other):
		if self.DesktopFileID == str(other):
			return True
		else:
			return False

	def __repr__(self):
		return self.DesktopFileID


class Separator:
	"Just a dummy class for Separators"
	pass


class Header:
	"Class for Inline Headers"
	def __init__(self, Name, GenericName, Comment):
		self.Name = Name
		self.GenericName = GenericName
		self.Comment = Comment

	def __str__(self):
		return self.Name


tmp = {}

def parse(file = ""):
	# if no file given, try default files
	if not file:
		for dir in xdg_config_dirs:
			file = os.path.join (dir, "menus" , "applications.menu")
			if os.path.isdir(dir) and os.path.isfile(file):
				break

	# convert to absolute path
	if not os.path.isabs(file):
		file = os.path.abspath(file)

	# check if it is a .menu file
	if not os.path.splitext(file)[1] == ".menu":
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
	tmp["mergeFiles"] = []
	tmp["DirectoryDirs"] = []
	tmp["cache"] = DesktopEntryCache()

	__parse(doc, file, tmp["Root"])
	__parsemove(tmp["Root"])
	__postparse(tmp["Root"])

	tmp["Root"].Doc = doc
	tmp["Root"].Filename = file

	# generate the menu
	__genmenuNotOnlyAllocated(tmp["Root"])
	__genmenuOnlyAllocated(tmp["Root"])

	# and finally sort
	sort(tmp["Root"])

	return tmp["Root"]


def __parse(node, file, parent = ""):
	for child in node.childNodes:
		if child.nodeType == ELEMENT_NODE:
			if child.tagName == 'Menu':
				__parseMenu(child, file, parent)
			elif child.tagName == 'AppDir':
				try:
					__parseAppDir(child.childNodes[0].nodeValue, file, parent)
				except IndexError:
					raise ValidationError('AppDir cannot be empty', file)
			elif child.tagName == 'DefaultAppDirs':
				__parseDefaultAppDir(file, parent)
			elif child.tagName == 'DirectoryDir':
				try:
					__parseDirectoryDir(child.childNodes[0].nodeValue, file, parent)
				except IndexError:
					raise ValidationError('DirectoryDir cannot be empty', file)
			elif child.tagName == 'DefaultDirectoryDirs':
				__parseDefaultDirectoryDir(file, parent)
			elif child.tagName == 'Name' :
				try:
					parent.Name = child.childNodes[0].nodeValue
				except IndexError:
					raise ValidationError('Name cannot be empty', file)
			elif child.tagName == 'Directory' :
				try:
					parent.addDirectory(child.childNodes[0].nodeValue)
				except IndexError:
					raise ValidationError('Directory cannot be empty', file)
			elif child.tagName == 'OnlyUnallocated':
				parent.OnlyUnallocated = True
			elif child.tagName == 'NotOnlyUnallocated':
				parent.OnlyUnallocated = False
			elif child.tagName == 'Deleted':
				parent.Deleted = True
			elif child.tagName == 'NotDeleted':
				parent.Deleted = False
			elif child.tagName == 'Include' or child.tagName == 'Exclude':
				parent.addRule(Rule(child.tagName, child))
			elif child.tagName == 'MergeFile':
				# TODO: can a MergeFile be empty if it's got type="parent"??
				try:
					__parseMergeFile(child.childNodes[0].nodeValue, child, file, parent)
				except IndexError:
					raise ValidationError('MergeFile cannot be empty', file)
			elif child.tagName == 'MergeDir':
				try:
					__parseMergeDir(child.childNodes[0].nodeValue, child, file, parent)
				except IndexError:
					raise ValidationError('MergeDir cannot be empty', file)
			elif child.tagName == 'DefaultMergeDirs':
				__parseDefaultMergeDirs(child, file, parent)
			elif child.tagName == 'Move':
				parent.addMove(Move(child))
			elif child.tagName == 'Layout':
				if len(child.childNodes) > 1:
					parent.Layout = Layout(child)
			elif child.tagName == 'DefaultLayout':
				if len(child.childNodes) > 1:
					parent.DefaultLayout = Layout(child)
			elif child.tagName == 'LegacyDir':
				try:
					__parseLegacyDir(child.childNodes[0].nodeValue, child.getAttribute("prefix"), file, parent)
				except IndexError:
					raise ValidationError('LegacyDir cannot be empty', file)
			elif child.tagName == 'KDELegacyDirs':
				__parseKDELegacyDirs(file, parent)

def __parsemove(menu):
	for submenu in menu.getSubmenus():
		__parsemove(submenu)

	# parse move operations
	for move in menu.getMoves():
		move_from_menu = menu.getSubmenu(move.Old)
		if move_from_menu:
			move_to_menu = menu.getSubmenu(move.New)

			if not move_to_menu:
				move_to_menu = Menu()
				move_to_menu.Name = move.New
				menu.addSubmenu(move_to_menu)

			move_to_menu += move_from_menu
			menu.removeSubmenu(move_from_menu)


def __postparse(menu):
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
		# add parent's app/directory dirs
		for dir in menu.getAppDirs(reverse = True):
			submenu.addAppDir(dir, 0)
		for dir in menu.getDirectoryDirs(reverse = True):
			submenu.addDirectoryDir(dir, 0)

		# get the valid .directory file out of the list
		entry = None
		for directory in submenu.getDirectories():
			for dir in submenu.getDirectoryDirs():
				if os.path.exists(os.path.join(dir, directory)):
					try:
						entry = DesktopEntry()
						entry.parse(os.path.join(dir, directory))
					except:
						pass
		submenu.setDirectory(entry)

		# enter submenus
		__postparse(submenu)

# Menu parsing stuff
def __parseMenu(child, file, parent):
	m = Menu()
	__parse(child, file, m)
	if parent:
		parent.addSubmenu(m)
	else:
		tmp["Root"] = m

# helper function
def __check(value, file, type):
	path = os.path.dirname(file)

	if not os.path.isabs(value):
		value = os.path.join(path, value)

	value = os.path.abspath(value)

	if type == "dir" and os.path.exists(value) and os.path.isdir(value):
		return value
	elif type == "file" and os.path.exists(value) and os.path.isfile(value):
		return value
	else:
		return False

# App/Directory Dir Stuff
def __parseAppDir(value, file, parent):
	value = __check(value, file, "dir")
	if value:
		parent.addAppDir(value)

def __parseDefaultAppDir(file, parent):
	for dir in xdg_data_dirs:
		__parseAppDir(os.path.join(dir, "applications"), file, parent)

def __parseDirectoryDir(value,file,parent):
	value = __check(value, file, "dir")
	if value:
		parent.addDirectoryDir(value)

def __parseDefaultDirectoryDir(file,parent):
	for dir in xdg_data_dirs:
		__parseDirectoryDir(os.path.join(dir, "desktop-directories"), file, parent)

# Merge Stuff
def __parseMergeFile(value, child, file, parent):
	if child.getAttribute("type") == "parent":
		for dir in xdg_config_dirs:
			rel_file = file.replace(dir, "").strip("/")
			if rel_file != file:
				for p in xdg_config_dirs:
					if dir == p:
						continue
					if os.path.isfile(os.path.join(p,rel_file)):
						__mergeFile(os.path.join(p,rel_file),child,parent)
						break
	else:
		value = __check(value, file, "file")
		if value:
			__mergeFile(value, child, parent)

def __parseMergeDir(value, child, file, parent):
	value = __check(value, file, "dir")
	if value:
		files = os.listdir(value)
		for file in files:
			if os.path.splitext(file)[1] == ".menu":
				__mergeFile(os.path.join(value, file), child, parent)

def __parseDefaultMergeDirs(child, file, parent):
	basename = os.path.splitext(os.path.basename(file))[0]
	for dir in xdg_config_dirs:
		__parseMergeDir(os.path.join(dir, "menus", basename + "-merged"), child, file, parent)

def __mergeFile(file, child, parent):
	# check for infinite loops
	if file in tmp["mergeFiles"]:
		if debug:
			raise ParsingError('Infinite MergeFile loop detected', file)
		else:
			return

	tmp["mergeFiles"].append(file)

	# load file
	try:
		doc = xml.dom.minidom.parse(file)
	except IOError:
		raise ParsingError('File not found', file)
	except xml.parsers.expat.ExpatError:
		raise ParsingError('Not a valid .menu file', file)

	# append file
	for child in doc.childNodes:
		if child.nodeType == ELEMENT_NODE:
			__parse(child,file,parent)
			break

# Legacy Dir Stuff
def __parseLegacyDir(dir, prefix, file, parent):
	m = __mergeLegacyDir(dir,prefix,file,parent)
	if m:
		parent += m

def __mergeLegacyDir(dir, prefix, file, parent):
	dir = __check(dir,file,"dir")
	if dir and dir not in tmp["DirectoryDirs"]:
		tmp["DirectoryDirs"].append(dir)

		m = Menu()
		m.addAppDir(dir)
		m.addDirectoryDir(dir)
		m.Name = os.path.basename(dir)

		for entry in os.listdir(dir):
			if entry == ".directory":
				m.addDirectory(entry)
			elif os.path.isdir(os.path.join(dir,entry)):
				m.addSubmenu(__mergeLegacyDir(os.path.join(dir,entry), prefix, file, parent))

		tmp["cache"].addEntries([dir],prefix, False)
		entries = tmp["cache"].getEntries([dir])

		for entry in entries:
			categories = entry.Categories
			if len(categories) == 0:
				r = Rule("Include")
				r.parseFilename(entry.DesktopFileID)
				r.compile()
				m.addRule(r)
			if not dir in parent.getAppDirs():
				categories.append("Legacy")
				entry.Categories = categories

		return m

def __parseKDELegacyDirs(file, parent):
	f=os.popen3("kde-config --path apps")
	output = f[1].readlines()
	for dir in output[0].split(":"):
		__parseLegacyDir(dir,"kde", file, parent)

# Finally generate the menu
def __genmenuNotOnlyAllocated(menu):
	for submenu in menu.getSubmenus():
		__genmenuNotOnlyAllocated(submenu)

	if menu.OnlyUnallocated == False:
		tmp["cache"].addEntries(menu.getAppDirs())
		entries = []
		for rule in menu.getRules():
			entries = rule.do(tmp["cache"].getEntries(menu.getAppDirs()), rule.Type, 1)
		for entry in entries:
		    if entry.Add == True:
				entry.Add = False
				entry.Allocated = True
				menu.addDeskEntry(entry)

def __genmenuOnlyAllocated(menu):
	for submenu in menu.getSubmenus():
		__genmenuOnlyAllocated(submenu)

	if menu.OnlyUnallocated == True:
		tmp["cache"].addEntries(menu.getAppDirs())
		entries = []
		for rule in menu.getRules():
			entries = rule.do(tmp["cache"].getEntries(menu.getAppDirs()), rule.Type, 2)
		for entry in entries:
		    if entry.Add == True:
			#	entry.Add = False
			#	entry.Allocated = True
				menu.addDeskEntry(entry)

# And sorting ...
def sort(menu):
	menu.Entries = []

	for submenu in menu.getSubmenus():
		sort(submenu)

		# remove separators at the beginning and at the end
		if len(submenu.Entries) > 0:
			if isinstance(submenu.Entries[0], Separator):
				submenu.Entries.pop(0)
		if len(submenu.Entries) > 0:
			if isinstance(submenu.Entries[-1], Separator):
				submenu.Entries.pop(-1)

	tmp_s = []
	tmp_e = []

	for order in menu.Layout.order:
		if order[0] == "Filename":
			tmp_e.append(order[1])
		elif order[0] == "Menuname":
			tmp_s.append(order[1])

	for order in menu.Layout.order:
		if order[0] == "Separator":
			menu.Entries.append(Separator())
		elif order[0] == "Filename":
			entry = menu.getDeskEntry(order[1])
			if entry:
				menu.Entries.append(entry)
		elif order[0] == "Menuname":
			submenu = menu.getSubmenu(order[1])
			if submenu:
				__parse_inline(submenu, menu)
		elif order[0] == "Merge":
			if order[1] == "files" or order[1] == "all":
				menu.DeskEntries.sort()
				for entry in menu.getDeskEntries():
					if entry not in tmp_e:
						menu.Entries.append(entry)
			elif order[1] == "menus" or order[1] == "all":
				menu.Submenus.sort()
				for submenu in menu.getSubmenus():
					if submenu.Name not in tmp_s:
						__parse_inline(submenu, menu)

	# getHidden / NoDisplay / OnlyShowIn / NotOnlyShowIn / Deleted
	hide = []
	for entry in menu.Entries:
		entry.Show = True
		menu.Visible += 1
		if isinstance(entry, Menu):
			if entry.Deleted == True:
				hide.append(entry)
			elif entry.Directory:
				if entry.Directory.getHidden() == True or entry.Directory.getNoDisplay() == True:
					hide.append(entry)
		elif isinstance(entry, MenuEntry):
			if entry.DesktopEntry.getHidden() == True or entry.DesktopEntry.getNoDisplay() == True:
				hide.append(entry)
			elif xdg.Config.windowmanager != None:
				if ( entry.DesktopEntry.getOnlyShowIn() != [] and xdg.Config.windowmanager not in entry.DesktopEntry.getOnlyShowIn() ) \
				or xdg.Config.windowmanager in entry.DesktopEntry.getNotShowIn():
					hide.append(entry)
	for entry in hide:
		entry.Show = False
		menu.Visible -= 1

	# show_empty tag
	for entry in menu.Entries:
		if isinstance(entry,Menu) and entry.Layout.show_empty == "false" and menu.Visible == 0:
				entry.Show = False

# inline tags
def __parse_inline(submenu, menu):
	if submenu.Layout.inline == "true":
		if len(submenu.Entries) == 1 and submenu.Layout.inline_alias == "true":
			entry = submenu.Entries[0]
			locale = "[" + xdg.Locale.langs[0] + "]"
			entry.DesktopEntry.set("Name" + locale, submenu.getName())
			entry.DesktopEntry.set("GenericName" + locale, submenu.getGenericName())
			entry.DesktopEntry.set("Comment" + locale, submenu.getComment())
			menu.Entries.append(entry)
		elif len(submenu.Entries) <= submenu.Layout.inline_limit or submenu.Layout.inline_limit == 0:
			if submenu.Layout.inline_header == "true":
				header = Header(submenu.getName(), submenu.getGenericName(), submenu.getComment())
				menu.Entries.append(header)
			for entry in submenu.getEntries():
				menu.Entries.append(entry)
		else:
			menu.Entries.append(submenu)
	else:
		menu.Entries.append(submenu)

class DesktopEntryCache:
	"Class to cache Desktop Entries"
	def __init__(self):
		self.cacheEntries = {}
		self.cache = {}

	def addEntries(self, dirs, prefix = "", recursive = True):
		for dir in dirs:
			if not self.cacheEntries.has_key(dir):
				self.cacheEntries[dir] = []
				self.__addFiles(dir, "", prefix, recursive)

	def __addFiles(self, dir, subdir, prefix, recursive):
		files = os.listdir(os.path.join(dir,subdir))
		for file in files:
			if os.path.splitext(file)[1] == ".desktop":
				try:
					deskentry = DesktopEntry()
					deskentry.parse(os.path.join(dir, subdir, file))
				except ParsingError:
					continue

				entry = MenuEntry(deskentry, os.path.join(prefix,subdir,file).replace("/", "-"))
				self.cacheEntries[dir].append(entry)
			elif os.path.isdir(os.path.join(dir,subdir,file)) and recursive == True:
				self.__addFiles(dir, os.path.join(subdir,file), prefix, recursive)

	def getEntries(self, dirs):
		list = []
		ids = []
		# cache the results again
		key = "".join(dirs)
		try:
			return self.cache[key]
		except KeyError:
			pass
		for dir in dirs:
			if self.cacheEntries.has_key(dir):
				for entry in self.cacheEntries[dir]:
					if entry.DesktopFileID not in ids:
						ids.append(entry.DesktopFileID)
						list.append(entry)
		self.cache[key] = list
		return list
