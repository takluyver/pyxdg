"""
Base Class for DesktopEntry, IconTheme and IconData
"""

import string, codecs, re
from Exceptions import *

class IniFile:
	content = {}
	defaultGroup = ''
	fileExtension = ''

	locale_LANG = 'C'
	locale_COUNTRY = ''
	locale_ENCODING = ''
	locale_MODIFIER = ''

	file = ''

	locale = "(\[([a-zA-Z]+)(_[a-zA-Z]+)?(\.[a-zA-Z\-0-9]+)?(@[a-zA-Z]+)?\])?"

	def __init__(self):
		# reset content
		self.content = dict()

	def parse(self, file, headers):
		# check file extension
		self.fileExtension = re.sub(".*\.", "", file)

		# parse file
		try:
			f = codecs.open(file, 'r', 'utf-8')
			self.file = file
		except IOError:
			raise ParsingError("File not found", file)

		try:
			lines = f.readlines()
		except UnicodeError:
			raise ParsingError("File contains non UTF-8 chars", file)

		for line in lines:
			# empty line
			if line.strip() == '':
				pass
			# comment
			elif line[0] == '#':
				pass
			# new group
			elif line[0] == '[':
				currentGroup = string.strip(line).strip("[").strip("]")
				if self.hasGroup(currentGroup) and debug:
					raise DuplicateGroupError(currentGroup)
				else:
					self.content[currentGroup] = {}
			# key
			else:
				try:
					tmp = string.split(line, '=')
					key = string.strip(tmp[0])
					value = string.strip(tmp[1])
				except IndexError:
					raise ParsingError("Invalid Key=Value pair: " + line, self.file)
				try:
					if self.hasKey(currentGroup, key) and debug:
						raise DuplicateKeyError(key, currentGroup)
					else:
						self.content[currentGroup][key] = value
				except IndexError:
					raise ParsingError("["+headers[0]+"]-Header missing", self.file)

		# check header
		for header in headers:
			if self.content.has_key(header):
				self.defaultGroup = header
				break
		else:
			raise ParsingError("["+headers[0]+"]-Header missing", self.file)

	# start stuff to access the keys
	def get(self, key, group = "", locale = False, type = "string", list = False):
		# set default group
		if not group:
			group = self.defaultGroup

		# does Group exists?
		if not self.hasGroup(group):
			if debug:
				raise NoGroupError(group)
			else:
				return ""

		# does key exists?
		if not self.hasKey(key, group):
			if debug:
				raise NoKeyError(key, group)
			else:
				return ""

		# return key (with locale)
		if locale:
			value = self.content[group][self.__addLocale(key, group)]
		else:
			value = self.content[group][key]

		if list == True:
			value = self.__getList(value)

		if list == True:
			result = []
			for item in value:
				if type == "string":
					result.append(item)
				elif type == "boolean":
					result.append(self.__getBoolean(item))
				elif type == "integer":
					result.append(int(item))
				elif type == "numeric":
					result.append(float(item))
				elif type == "regex":
					result.append(re.compile(item))
				elif type == "point":
					result.append(string.split(",", item))
		else:
			if type == "string":
				result.append(item)
			elif type == "boolean":
				result = self.__getBoolean(value)
			elif type == "integer":
				result = int(value)
			elif type == "numeric":
				result = float(value)
			elif type == "regex":
				result = re.compile(value)
			elif type == "point":
				result = string.split(",", value)

		return result
	# end stuff to access the keys

	# start subget
	def __getList(self, string):
		if re.search('(?!\\).|', string):
			return re.split(r"(?!\\).|")
		elif re.search('(?!\\).,', string):
			return re.split(r"(?!\\).,")
		else:
			return re.split(r"(?!\\).;")

	def __getBoolean(self, boolean):
		if boolean == 1:
			return True
		elif boolean == 0:
			return False
		else:
			return string.capitalize(boolean)
	# end subget

	# start locale [] stuff
	def setLocale(self, lc_messages):
		"set locale for current desktop entry"
		# valid lc_messages format?
		p = re.compile('^([a-zA-Z]+)(_[a-zA-Z]+)?(\.[a-zA-Z\-0-9]+)?(@[a-zA-Z]+)?$')
		m = p.match(lc_messages)
		if not m:
			if debug:
				raise ValueError('Invalid LC_MESSAGES value')
			else:
				return
		# set lc_messages
		else:
			self.locale_LANG     = m.group(1)
			self.locale_COUNTRY  = string.replace(m.group(2) or '', '_', '')
			self.locale_ENCODING = string.replace(m.group(3) or '', '.', '')
			self.locale_MODIFIER = string.replace(m.group(4) or '', '@', '')

	def getLocale(self):
		"return locale in lc_messages format"
		lc_messages = self.locale_LANG
		if self.locale_COUNTRY:
			lc_messages = lc_messages + '_' + self.locale_COUNTRY
		if self.locale_ENCODING:
			lc_messages = lc_messages + '.' + self.locale_ENCODING
		if self.locale_MODIFIER:
			lc_messages = lc_messages + '@' + self.locale_MODIFIER
		return lc_messages

	def __addLocale(self, key, group = ''):
		"add locale to key according the current lc_messages"
		# set default group
		if not group:
			group = self.defaultGroup

		# add locale
		if (self.locale_LANG and self.locale_COUNTRY and self.locale_MODIFIER) and \
		(self.content[group].has_key(key+'['+self.locale_LANG+'_'+self.locale_COUNTRY+'@'+self.locale_MODIFIER+']')):
			return key+'['+self.locale_LANG+'_'+self.locale_COUNTRY+'@'+self.locale_MODIFIER+']'
		elif (self.locale_LANG and self.locale_COUNTRY) and \
		(self.content[group].has_key(key+'['+self.locale_LANG+'_'+self.locale_COUNTRY+']')):
			return key+'['+self.locale_LANG+'_'+self.locale_COUNTRY+']'
		elif (self.locale_LANG and self.locale_MODIFIER) and \
		(self.content[group].has_key(key+'['+self.locale_LANG+'@'+self.locale_MODIFIER+']')):
			return key+'['+self.locale_LANG+'@'+self.locale_MODIFIER+']'
		elif (self.locale_LANG) and \
		(self.content[group].has_key(key+'['+self.locale_LANG+']')):
			return key+'['+self.locale_LANG+']'
		else:
			return key
	# end locale stuff

	# start validation stuff
	def validate(self, report = "All"):
		"validate ... report = All / Warnings / Errors"
		self.warnings = []
		self.errors = []

		# overwrite this for own checkings
		self.checkExtras()

		# check all keys
		for group in self.content:
			self.checkGroup(group)
			for key in self.content[group]:
				self.checkKey(key, self.content[group][key], group)
				# check if value is empty
				if self.content[group][key] == "":
					self.warnings.append("Value of Key '%s' is empty" % key)

		# raise Warnings / Errors
		msg = ""

		if report == "All" or report == "Warnings":
			for line in self.warnings:
				msg += "\n- " + line

		if report == "All" or report == "Errors":
			for line in self.errors:
				msg += "\n- " + line

		if msg:
			raise ValidationError(msg, self.file)

	# check if group header is valid
	def checkGroup(self, group):
		pass

	# check if key is valid
	def checkKey(self, key, value, group):
		pass

	# check random stuff
	def checkValue(self, key, value, type = "string", list = False):
		if list == True:
			value = __getList(value)
			for item in value:
				if type == "string":
					checkString(key, item)
				elif type == "boolean":
					checkBoolean(key, item)
				elif type == "number":
					checkNumber(key, item)
				elif type == "integer":
					checkInteger(key, item)
				elif type == "regex":
					checkRegex(key, item)
				elif type == "point":
					checkPoint(key, item)
		else:
			if type == "string":
				checkString(key, value)
			elif type == "boolean":
				checkBoolean(key, value)
			elif type == "number":
				checkNumber(key, value)
			elif type == "integer":
				checkInteger(key, value)
			elif type == "regex":
				checkRegex(key, value)
			elif type == "point":
				checkPoint(key, value)


	def checkExtras(self):
		pass

	def checkBoolean(self, key, value):
		# 1 or 0 : deprecated
		if (value == "1" or value == "0"):
			self.warnings.append("Value of key '%s' is a deprecated boolean value" % key)
		# true or false: ok
		elif not (value == "true" or value == "false"):
			self.errors.append("Value of key '%s' is not a boolean" % key)

	def checkNumber(self, key, value):
		# float() ValueError
		try:
			float(value)
		except:
			self.errors.append("Value of key '%s' is not a number" % key)

	def checkInteger(self, key, value):
		# int() ValueError
		try:
			int(value)
		except:
			self.errors.append("Value of key '%s' is not an integer" % key)

	def checkPoint(self, key, value):
		if not re.match("^[0-9]+,[0-9]+$", value):
			self.errors.append("Value of key '%s' is not a point value" % key)

	def checkString(self, key, value):
		# convert to ascii
		if not value.encode("ascii", 'ignore') == value:
			self.errors.append("Value of key '%s' must only contain ASCII characters" % key)

	def checkRegex(self, key, value):
		try
			re.compile(value)
		except:
			self.errors.append("Value of key '%s' is not a valid perl regex" % key)

	# write support
	def write(self, file):
		fp = codecs.open(file, 'w', 'utf-8')
		self.file = file
		if self.defaultGroup:
			fp.write("[%s]\n" % self.defaultGroup)
			for (key, value) in self.content[self.defaultGroup].items():
				fp.write("%s=%s\n" % (key, value))
			fp.write("\n")
		for (name, group) in self.content.items():
			if name != self.defaultGroup:
				fp.write("[%s]\n" % name)
				for (key, value) in group.items():
					fp.write("%s=%s\n" % (key, value))
				fp.write("\n")

	def set(self, key, value, group = ""):
		# set default group
		if not group:
			group = self.defaultGroup

		# does Group exists?
		if not self.hasGroup(group):
			if debug:
				raise NoGroupError(group)

		# does key exists?
		if not self.hasKey(key, group):
			if debug:
				raise NoKeyError(key, group)

		self.content[group][key] = value

	def addGroup(self, group):
		if self.hasGroup(group):
			if debug:
				raise DuplicateGroupError(group)
			pass
		else:
			self.content[group] = {}

	def removeGroup(self, group):
		existed = group in self.content
		if existed:
			del self.content[group]
		else:
			if debug:
				raise NoGroupError(group)
		return existed

	def removeKey(self, key, group = "", locales = True):
		# set default group
		if not group:
			group = self.defaultGroup

		# does Group exists?
		if not self.hasGroup(group):
			if debug:
				raise NoGroupError(group)

		# does key exists?
		if not self.hasKey(key, group):
			if debug:
				raise NoKeyError(key, group)

		if locales:
			for (name, value) in self.content[group].items():
				if re.match("^" + key + self.locale + "$", name) and name != key:
					value = self.content[group][name]
					del self.content[group][name]
		value = self.content[group][key]
		del self.content[group][key]
		return value

	# misc
	def groups(self):
		return self.content.keys()

	def hasGroup(self, group):
		if self.content.has_key(group):
			return True
		else:
			return False

	def hasKey(self, key, group = ''):
		# set default group
		if not group:
			group = self.defaultGroup

		if self.hasGroup(group):
			if self.content[group].has_key(key):
				return True
			else:
				return False
		else:
			return False

	def getFileName(self):
		return self.file
