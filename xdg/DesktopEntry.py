"""
Complete implementation of the XDG Desktop Entry Specification Version 0.9.4
http://www.freedesktop.org/standards/desktop-entry-spec/

Not supported:
- Encoding: Legacy Mixed
- Does not check exec parameters
- Does not completly validate deprecated/kde items
- Does not check Category entries
- Does not check OnlyShowIn entries
"""

from xdg.IniFile import *

class DesktopEntry(IniFile):
	"Class to parse and validate DesktopEntries"
	def __init__(self):
		IniFile.__init__(self)

	def __str__(self):
		return self.getName()

	def __cmp__(self, other):
		return cmp(self, other)

	def parse(self, file):
		IniFile.parse(self, file, ["Desktop Entry", "KDE Desktop Entry"])

	# start standard keys
	def getType(self):
		return self.get('Type')
	def getVersion(self):
		return self.get('Version', type = "numeric")
	def getEncoding(self):
		return self.get('Encoding')
	def getName(self):
		return self.get('Name', locale = True)
	def getGenericName(self):
		return self.get('GenericName', locale = True)
	def getComment(self):
		return self.get('Comment', locale = True)
	def getNoDisplay(self):
		return self.get('NoDisplay', type = "boolean")
	def getIcon(self):
		return self.get('Icon', locale = True)
	def getHidden(self):
		return self.get('Hidden', type = "boolean")
	def getFilePattern(self):
		return self.get('FilePattern', type = "regex")
	def getTryExec(self):
		return self.get('TryExec')
	def getExec(self):
		return self.get('Exec')
	def getPath(self):
		return self.get('Path')
	def getTerminal(self):
		return self.get('Terminal', type = "boolean")
	def getSwallowTitle(self):
		return self.get('SwallowTitle', locale = True)
	def getSwallowExec(self):
		return self.get('SwallowExec')
	def getActions(self):
		return self.get('Actions', list = True)
	def getMimeType(self):
		return self.get('MimeType', list = True, type = "regex")
	def getSortOrder(self):	
		return self.get('SortOrder', list = True)
	def getDev(self):
		return self.get('Dev')
	def getFSType(self):
		return self.get('FSType')
	def getMountPoint(self):
		return self.get('MountPoint')
	def getReadonly(self):
		return self.get('ReadOnly', type = "boolean")
	def getUnmountIcon(self):
		return self.get('UnmountIcon', locale = True)
	def getURL(self):
		return self.get('URL')
	def getCategories(self):
		return self.get('Categories', list = True)
	def getOnlyShowIn(self):
		return self.get('OnlyShowIn', list = True)
	def getNotShowIn(self):
		return self.get('NotShowIn', list = True)
	def getStartupNotify(self):
		return self.get('StartupNotify', type = "boolean")
	def getStartupWMClass(self):
		return self.get('StartupWMClass')
	# end standard keys

	# start kde keys
	def getServiceTypes(self):
		return self.get('ServiceTypes', list = True)
	def getDocPath(self):
		return self.get('DocPath')
	def getwords(self):
		return self.get('Keywords', list = True, locale = True)
	def getInitialPreference(self):
		return self.get('InitialPreference')
	# end kde keys

	# start deprecated keys
	def getMiniIcon(self):
		return self.get('MiniIcon', locale = True)
	def getTerminalOptions(self):
		return self.get('TerminalOptions')
	def getDefaultApp(self):
		return self.get('DefaultApp')
	def getProtocols(self):
		return self.get('Protocols', list = True)
	def getExtensions(self):
		return self.get('Extensions', list = True)
	def getBinaryPattern(self):
		return self.get('BinaryPattern')
	def getMapNotify(self):
		return self.get('MapNotify')
	# end deprecated keys

	# validation stuff
	def checkExtras(self):
		# header
		if self.defaultGroup == "KDE Desktop Entry":
			self.warnings.append('[KDE Desktop Entry]-Header is deprecated')

		# file extension
		if self.fileExtension == "kdelnk":
			self.warnings.append("File extension .kdelnk is deprecated")
		elif self.fileExtension != "desktop" and self.fileExtension != "directory":
			self.warnings.append('Unknown File extension')

		# Type
		try:
			self.type = self.content[self.defaultGroup]["Type"]
		except KeyError:
			self.errors.append("Key 'Type' is missing")

		# Encoding
		try:
			self.encoding = self.content[self.defaultGroup]["Encoding"]
		except KeyError:
			self.errors.append("Key 'Encoding' is missing")

		# Version
		try:
			self.version = self.content[self.defaultGroup]["Version"]
		except KeyError:
			self.warnings.append("Key 'Version' is missing")

		# Name
		try:
			self.name = self.content[self.defaultGroup]["Name"]
		except KeyError:
			self.errors.append("Key 'Name' is missing")

	def checkGroup(self, group):
		# check if group header is valid
		if not (group == self.defaultGroup \
		or re.match("^\Desktop Action [a-zA-Z]+\$", group) \
		or (re.match("^\X-", group) and group.encode("ascii", 'ignore') == group)):
			self.errors.append("Invalid Group name: %s" % group.encode("ascii", "replace"))
		else:
		    #OnlyShowIn and NotShowIn
		    if self.content[group].has_key("OnlyShowIn") and self.content[group].has_key("NotShowIn"):
			self.errors.append("Group may either have OnlyShowIn or NotShowIn, but not both")

	def checkKey(self, key, value, group):
		# standard keys		
		if key == "Type":
			if value == "ServiceType" or value == "Service":
				self.warnings.append("Type=%s is a KDE extension" % key)
			elif value == "MimeType":
				self.warnings.append("Type=MimeType is deprecated")
			elif not (value == "Application" or value == "Link" or value == "FSDevice" or value == "Directory"):
				self.errors.append("Value of key 'Type' must be Application, Link, FSDevice or Directory, but is '%s'" % value)

			if self.fileExtension == "directory" and not value == "Directory":
				self.warnings.append("File extension is .directory, but Type is '%s'" % value)
			elif self.fileExtension == "desktop" and value == "Directory":
				self.warnings.append("Files with Type=Directory should have the extension .directory")

		elif key == "Version":
			self.checkNumber(key, value)

		elif key == "Encoding":
			if value == "Legacy-Mixed":
				self.errors.append("Encoding=Legacy-Mixed is deprecated and not supported by this parser")
			elif not value == "UTF-8":
				self.errors.append("Value of key 'Encoding' must be UTF-8")

		elif re.match("^Name"+self.locale+"$", key):
			pass # locale string

		elif re.match("^GenericName"+self.locale+"$", key):
			pass # locale string

		elif re.match("^Comment"+self.locale+"$", key):
			pass # locale string

		elif key == "NoDisplay":
			self.checkBoolean(key, value)

		elif key == "Hidden":
			self.checkBoolean(key, value)

		elif key == "Terminal":
			self.checkBoolean(key, value)
			self.checkType(key, "Application")

		elif key == "TryExec":
			self.checkString(key, value)
			self.checkType(key, "Application")

		elif key == "Exec":
			self.checkString(key, value)
			self.checkType(key, "Application")

		elif key == "Path":
			self.checkString(key, value)
			self.checkType(key, "Application")

		elif re.match("^Icon"+self.locale+"$", key):
			self.checkString(key, value)

		elif re.match("^SwallowTitle"+self.locale+"$", key):
			self.checkType(key, "Application")

		elif key == "SwallowExec":
			self.checkString(key, value)
			self.checkType(key, "Application")

		elif key == "FilePatterns":
			self.checkRegex(key, value)
			self.checkType(key, "Application")

		elif key == "Actions":
			self.checkString(key, value)
			self.checkType(key, "Application")

		elif key == "MimeType":
			self.checkRegex(key, value)
			self.checkType(key, "Application")

		elif key == "Categories":
			self.checkString(key, value)
			self.checkType(key, "Application")

		elif key == "OnlyShowIn":
			self.checkString(key, value)

		elif key == "NotShowIn":
			self.checkString(key, value)

		elif key == "StartupNotify":
			self.checkBoolean(key, value)
			self.checkType(key, "Application")

		elif key == "StartupWMClass":
			self.checkType(key, "Application")

		elif key == "SortOrder":
			self.checkString(key, value)
			self.checkType(key, "Directory")

		elif key == "URL":
			self.checkString(key, value)
			self.checkType(key, "URL")

		elif key == "Dev":
			self.checkString(key, value)
			self.checkType(key, "FSDevice")

		elif key == "FSType":
			self.checkString(key, value)
			self.checkType(key, "FSDevice")

		elif key == "MountPoint":
			self.checkString(key, value)
			self.checkType(key, "FSDevice")

		elif re.match("^UnmountIcon"+self.locale+"$", key):
			self.checkString(key, value)
			self.checkType(key, "FSDevice")

		elif key == "ReadOnly":
			self.checkBoolean(key, value)
			self.checkType(key, "FSDevice")

		# kde extensions
		elif key == "ServiceTypes":
			self.checkString(key, value)
			self.warnings.append("Key '%s' is a KDE extension" % key)

		elif key == "DocPath":
			self.checkString(key, value)
			self.warnings.append("Key '%s' is a KDE extension" % key)

		elif re.match("^Keywords"+self.locale+"$", key):
			self.warnings.append("Key '%s' is a KDE extension" % key)

		elif key == "InitialPreference":
			self.checkNumber(key, value)
			self.warnings.append("Key '%s' is a KDE extension" % key)

		# deprecated keys
		elif re.match("^MiniIcon"+self.locale+"$", key):
			self.checkString(key, value)
			self.warnings.append("Key '%s' is deprecated" % key)

		elif key == "TerminalOptions":
			self.checkString(key, value)
			self.warnings.append("Key '%s' is deprecated" % key)

		elif key == "DefaultApp":
			self.checkString(key, value)
			self.warnings.append("Key '%s' is deprecated" % key)

		elif key == "Protocols":
			self.checkString(key, value)
			self.warnings.append("Key '%s' is deprecated" % key)

		elif key == "^Extensions":
			self.checkString(key, value)
			self.warnings.append("Key '%s' is deprecated" % key)

		elif key == "BinaryPattern":
			self.checkString(key, value)
			self.warnings.append("Key '%s' is deprecated" % key)

		elif key == "MapNotify":
			self.checkString(key, value)
			self.warnings.append("Key '%s' is deprecated" % key)

		# "X-" extensions
		elif re.match("^X-[a-zA-Z0-9-]+", key):
			pass

		else:
			self.errors.append("Invalid key: %s" % key)

	def checkType(self, key, type):
		if not self.type == type:
			self.errors.append("Key '%s' only allowed in Type=%s" % (key, type))
