"""
Base Class for DesktopEntry, IconTheme and IconData
"""

import re, os.path, codecs
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

	cache = {}

	def __init__(self):
		# reset content
		self.content = dict()

	def parse(self, filename, headers):
		# for performance reasons
		content = self.content

		# parse file
		try:
			lines = file(filename, 'r').readlines()
			self.file = filename
		except IOError:
			raise ParsingError("File not found", filename)

		for line in lines:
			line = line.strip()
			# empty line
			if not line:
				continue
			# comment
			elif line[0] == '#':
				continue
			# new group
			elif line[0] == '[':
				currentGroup = line.lstrip("[").rstrip("]")
				if debug and self.hasGroup(currentGroup):
					raise DuplicateGroupError(currentGroup, self.filename)
				else:
					content[currentGroup] = {}
			# key
			else:
				try:
					tmp = line.split('=',1)
					key = tmp[0].strip()
					value = tmp[1].strip()
				except IndexError:
					raise ParsingError("Invalid Key=Value pair: %s" % line, filename)
				try:
					if debug and self.hasKey(key, currentGroup):
						raise DuplicateKeyError(key, currentGroup, filename)
					else:
						content[currentGroup][key] = value
				except IndexError:
					raise ParsingError("[%s]-Header missing" % headers[0], filename)

		# check header
		for header in headers:
			if content.has_key(header):
				self.defaultGroup = header
				break
		else:
			raise ParsingError("[%s]-Header missing" % headers[0], filename)

	# start stuff to access the keys
	def get(self, key, group = "", locale = False, type = "string", list = False):
		# set default group
		if not group:
			group = self.defaultGroup

		cache_name = "".join([self.file,key,group,str(locale),type,str(list)])

		try:
			return self.cache[cache_name]
		except KeyError:
			pass

		# return key (with locale)
		try:
			if locale:
				value = self.content[group][self.__addLocale(key, group)]
			else:
				value = self.content[group][key]
		except KeyError, e:
			if debug:
				if e == group:
					raise NoGroupError(group, self.file)
				else:
					raise NoKeyError(key, group, self.file)
			else:
				if list == True:
					return []
				else:
					return ""
				
		if list == True:
			values = self.getList(value)
			result = []
		else:
			values = [value]

		for value in values:
			if type == "string" and locale == True:
				value = value.decode("utf-8", "ignore")
			elif type == "boolean":
				value = self.__getBoolean(value)
			elif type == "integer":
				value = int(value)
			elif type == "numeric":
				value = float(value)
			elif type == "regex":
				value = re.compile(value)
			elif type == "point":
				value = value.split(",")

			if list == True:
				result.append(value)
			else:
				result = value

		self.cache[cache_name] = result

		return result
	# end stuff to access the keys

	# start subget
	def getList(self, string):
		if re.search(r"(?<!\\)\;", string):
			list = re.split(r"(?<!\\);", string)
		elif re.search(r"(?<!\\)\|", string):
			list = re.split(r"(?<!\\)\|", string)
		elif re.search(r"(?<!\\),", string):
			list = re.split(r"(?<!\\),", string)
		else:
			list = [string]
		if list[-1] == "":
			list.pop()
		return list

	def __getBoolean(self, boolean):
		if boolean == 1:
			return True
		elif boolean == 0:
			return False
		else:
			return boolean.capitalize()
	# end subget

	def resetCache(self):
		# delete cache
		self.cache = {}

	# start locale [] stuff
	def setLocale(self, lc_messages):
		"set locale for current desktop entry"
		# valid lc_messages format?
		try:
			p = re.compile('^([a-zA-Z]+)(_([a-zA-Z]+))?(\.([a-zA-Z\-0-9]+))?(@([a-zA-Z]+))?$')
			m = p.match(lc_messages)
		except TypeError:
			m = ""

		if not m:
			if debug:
				raise ValueError('Invalid LC_MESSAGES value')
			else:
				return

		# set lc_messages
		else:
			self.locale_LANG     = m.group(1)
			self.locale_COUNTRY  = m.group(3) or ''
			self.locale_ENCODING = m.group(5) or ''
			self.locale_MODIFIER = m.group(7) or ''
			self.resetCache()

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

		# get file extension
		self.fileExtension = os.path.splitext(self.file)[1]

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
			values = self.getList(value)
		else:
			values = [value]

		for value in values:
			if type == "string":
				code = self.checkString(value)
			elif type == "boolean":
				code = self.checkBoolean(value)
			elif type == "number":
				code = self.checkNumber(value)
			elif type == "integer":
				code = self.checkInteger(value)
			elif type == "regex":
				code = self.checkRegex(value)
			elif type == "point":
				code = self.checkPoint(value)
			if code == 1:
				self.errors.append("'%s' is not a valid %s" % (value, type))
			elif code == 2:
				self.warnings.append("Value of key '%s' is deprecated" % key)

	def checkExtras(self):
		pass

	def checkBoolean(self, value):
		# 1 or 0 : deprecated
		if (value == "1" or value == "0"):
			return 2
		# true or false: ok
		elif not (value == "true" or value == "false"):
			return 1

	def checkNumber(self, value):
		# float() ValueError
		try:
			float(value)
		except:
			return 1

	def checkInteger(self, value):
		# int() ValueError
		try:
			int(value)
		except:
			return 1

	def checkPoint(self, value):
		if not re.match("^[0-9]+,[0-9]+$", value):
			return 1

	def checkString(self, value):
		# convert to ascii
		if not value.decode("utf-8", "ignore").encode("ascii", 'ignore') == value:
			return 1

	def checkRegex(self, value):
		try:
			re.compile(value)
		except:
			return 1

	# write support
	def write(self, file):
		fp = codecs.open(file, 'w')
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

		try:
			if isinstance(value, unicode):
				self.content[group][key] = value.encode("utf-8", "ignore")
			else:
				self.content[group][key] = value
			self.resetCache()
		except KeyError:
			raise NoGroupError(group, self.file)

	def addGroup(self, group):
		if self.hasGroup(group):
			if debug:
				raise DuplicateGroupError(group, self.file)
			else:
				pass
		else:
			self.content[group] = {}

	def removeGroup(self, group):
		existed = group in self.content
		if existed:
			del self.content[group]
		else:
			if debug:
				raise NoGroupError(group, self.file)
		return existed

	def removeKey(self, key, group = "", locales = True):
		# set default group
		if not group:
			group = self.defaultGroup

		try:
			if locales:
				for (name, value) in self.content[group].items():
					if re.match("^" + key + self.locale + "$", name) and name != key:
						value = self.content[group][name]
						del self.content[group][name]
			value = self.content[group][key]
			del self.content[group][key]
			return value
		except KeyError:
			if debug:
				if e == group:
					raise NoGroupError(group, self.file)
				else:
					raise NoKeyError(key, group, self.file)
			else:
				return ""

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

		if self.content[group].has_key(key):
			return True
		else:
			return False

	def getFileName(self):
		return self.file
