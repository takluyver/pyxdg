"""
Base Class for DesktopEntry, IconTheme and IconData
"""

import re, os, stat, io
from xdg.Exceptions import (ParsingError, DuplicateGroupError, NoGroupError,
                            NoKeyError, DuplicateKeyError, ValidationError,
                            debug)
import xdg.Locale
from xdg.util import u


def is_ascii(s):
    """Return True if a string consists entirely of ASCII characters."""
    try:
        s.encode('ascii', 'strict')
        return True
    except UnicodeError:
        return False


class IniFile:
    defaultGroup = ''
    fileExtension = ''

    filename = ''

    tainted = False

    def __init__(self, filename=None):
        self.content = dict()
        if filename:
            self.parse(filename)

    def __cmp__(self, other):
        return cmp(self.content, other.content)

    def parse(self, filename, headers=None):
        '''Parse an INI file.

        headers -- list of headers the parser will try to select as a default header
        '''
        if not os.path.isfile(filename):
            raise ParsingError("File not found", filename)

        try:
            # The content should be UTF-8, but legacy files can have other
            # encodings, including mixed encodings in one file. We don't attempt
            # to decode them, but we silence the errors.
            fd = io.open(filename, 'r', encoding='utf-8', errors='replace')
        except IOError as e:
            fd.close()
            if debug:
                raise e
            else:
                return

        # for performance reasons
        self.content = {}
        content = self.content
        #
        current_group = None
        current_comment = []
        group_index = 0
        key_index = 0

        # parse file
        for line in fd:
            line = line.strip()
            # empty line
            if not line:
                continue
            # comment
            elif line[0] == '#':
                current_comment.append(line[1:].lstrip())
            # new group
            elif line[0] == '[':
                current_group = line.lstrip("[").rstrip("]")
                if debug and self.hasGroup(current_group):
                    raise DuplicateGroupError(current_group, filename)
                else:
                    content[current_group] = {
                        'pos': group_index,
                        'comment': '\n'.join(current_comment),
                        'keys': {}
                    }
                    group_index += 1
                    key_index = 0
                    current_comment = []
            # key
            else:
                try:
                    key, value = line.split("=", 1)
                except ValueError:
                    raise ParsingError("Invalid line: " + line, filename)

                # Spaces before/after '=' should be ignored
                key = key.rstrip()
                try:
                    if debug and self.hasKey(key, current_group):
                        raise DuplicateKeyError(key, current_group, filename)
                    else:
                        content[current_group]['keys'][key] = {
                            'pos': key_index,
                            'value': value.lstrip(),
                            'comment': '\n'.join(current_comment),
                        }
                        key_index += 1
                        current_comment = []
                except (IndexError, UnboundLocalError):
                    raise ParsingError("Parsing error on key, group missing", filename)

        fd.close()

        self.filename = filename
        self.tainted = False

        # check header
        if headers:
            for header in headers:
                if header in content:
                    self.defaultGroup = header
                    break
            else:
                raise ParsingError("[%s]-Header missing" % headers[0], filename)

    # start stuff to access the keys
    def get(self, key, group=None, locale=False, type="string", list=False, strict=False):
        # set default group
        if not group:
            group = self.defaultGroup

        value = ''
        # return key (with locale)
        if (group in self.content) and (key in self.content[group]['keys']):
            keys = self.content[group]['keys']
            if locale:
                value = keys[self.__addLocale(key, group)]['value']
            else:
                value = keys[key]['value']
        else:
            if strict or debug:
                if group not in self.content:
                    raise NoGroupError(group, self.filename)
                elif key not in self.content[group]:
                    raise NoKeyError(key, group, self.filename)

        if list:
            values = self.getList(value)
            result = []
        else:
            values = [value]

        for value in values:
            if type == "boolean":
                value = self.__getBoolean(value)
            elif type == "integer":
                try:
                    value = int(value)
                except ValueError:
                    value = 0
            elif type == "numeric":
                try:
                    value = float(value)
                except ValueError:
                    value = 0.0
            elif type == "regex":
                value = re.compile(value)
            elif type == "point":
                x, y = value.split(",")
                value = int(x), int(y)

            if list:
                result.append(value)
            else:
                result = value

        return result
    # end stuff to access the keys

    # stuff for accessing comments
    def getGroupComment(self, group):
        if group in self.content:
            return self.content[group]['comment']

    def setGroupComment(self, comment, group=None):
        if not group:
            group = self.defaultGroup
        self.content[group]['comment'] = comment

    def getKeyComment(self, key, group=None):
        if not group:
            group = self.defaultGroup
        return self.content[group]['keys'][key]['comment']

    def setKeyComment(self, comment, key, group=None):
        if not group:
            group = self.defaultGroup
        self.content[group]['keys'][key]['comment'] = comment
    # end stuff for comments

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
        if boolean == 1 or boolean == "true" or boolean == "True":
            return True
        elif boolean == 0 or boolean == "false" or boolean == "False":
            return False
        return False
    # end subget

    def __addLocale(self, key, group=None):
        "add locale to key according the current lc_messages"
        # set default group
        if not group:
            group = self.defaultGroup

        for lang in xdg.Locale.langs:
            langkey = "%s[%s]" % (key, lang)
            if langkey in self.content[group]['keys']:
                return langkey

        return key

    # start validation stuff
    def validate(self, report="All"):
        """Validate the contents, raising :class:`~xdg.Exceptions.ValidationError`
        if there is anything amiss.

        report can be 'All' / 'Warnings' / 'Errors'
        """

        self.warnings = []
        self.errors = []

        # get file extension
        self.fileExtension = os.path.splitext(self.filename)[1]

        # overwrite this for own checkings
        self.checkExtras()

        # check all keys
        for group in self.groups():
            self.checkGroup(group)
            for key in self.keys(group):
                value = self.content[group]['keys'][key]['value']
                self.checkKey(key, value, group)
                # check if value is empty
                if value == "":
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
            raise ValidationError(msg, self.filename)

    # check if group header is valid
    def checkGroup(self, group):
        pass

    # check if key is valid
    def checkKey(self, key, value, group):
        pass

    # check random stuff
    def checkValue(self, key, value, type="string", list=False):
        if list:
            values = self.getList(value)
        else:
            values = [value]

        for value in values:
            if type == "string":
                code = self.checkString(value)
            if type == "localestring":
                continue
            elif type == "boolean":
                code = self.checkBoolean(value)
            elif type == "numeric":
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
        return 0 if is_ascii(value) else 1

    def checkRegex(self, value):
        try:
            re.compile(value)
        except:
            return 1

    # write support
    def write(self, filename=None, trusted=False):
        if not filename and not self.filename:
            raise ParsingError("File not found", "")

        if filename:
            self.filename = filename
        else:
            filename = self.filename

        if os.path.dirname(filename) and not os.path.isdir(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

        with io.open(filename, 'w', encoding='utf-8') as fp:

            # An executable bit signifies that the desktop file is
            # trusted, but then the file can be executed. Add hashbang to
            # make sure that the file is opened by something that
            # understands desktop files.
            if trusted:
                fp.write(u("#!/usr/bin/env xdg-open\n"))

            if self.defaultGroup:
                self._write_group(fp, self.defaultGroup)
            for name in self.groups():
                if name == self.defaultGroup:
                    continue
                self._write_group(fp, name)

        # Add executable bits to the file to show that it's trusted.
        if trusted:
            oldmode = os.stat(filename).st_mode
            mode = oldmode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
            os.chmod(filename, mode)

        self.tainted = False

    def _write_group(self, fp, group_name):
        group_data = self.content[group_name]
        comment = group_data.get('comment', '')
        if comment:
            self._write_comment(fp, comment)
        fp.write(u('[%s]\n') % group_name)
        for key in self.keys(group_name):
            self._write_key(fp, key, group_name)
        fp.write(u('\n'))

    def _write_key(self, fp, key, group_name):
        data = self.content[group_name]['keys'][key]
        comment, value = data['comment'], data['value']
        if comment:
            self._write_comment(fp, comment)
        fp.write(u('%s=%s\n') % (key, value))

    def _write_comment(self, fp, comment):
        for line in comment.strip().split('\n'):
            fp.write(u('# %s\n') % line.strip())

    def set(self, key, value, group=None, locale=False):
        # set default group
        if not group:
            group = self.defaultGroup
        if group not in self.content:
            raise NoGroupError(group, self.filename)

        if locale and len(xdg.Locale.langs) > 0:
            key = key + "[" + xdg.Locale.langs[0] + "]"

        keys = self.content[group]['keys']
        if key not in keys:
            keys[key] = {
                'pos': len(keys),
                'value': u(''),
                'comment': u('')
            }
        keys[key]['value'] = u(value)

        self.tainted = (value == self.get(key, group))

    def addGroup(self, group, comment=''):
        if self.hasGroup(group):
            if debug:
                raise DuplicateGroupError(group, self.filename)
        else:
            self.content[group] = {
                'pos': len(self.content),
                'comment': comment,
                'keys': {}
            }
            self.tainted = True

    def removeGroup(self, group):
        existed = group in self.content
        if existed:
            del self.content[group]
            self.tainted = True
        else:
            if debug:
                raise NoGroupError(group, self.filename)
        return existed

    def removeKey(self, key, group=None, locales=True):
        # set default group
        if not group:
            group = self.defaultGroup

        try:
            if locales:
                for name in list(self.content[group]['keys']):
                    if re.match("^" + key + xdg.Locale.regex + "$", name) and name != key:
                        del self.content[group]['keys'][name]
            value = self.content[group]['keys'].pop(key)
            self.tainted = True
            return value
        except KeyError as e:
            if debug:
                if e == group:
                    raise NoGroupError(group, self.filename)
                else:
                    raise NoKeyError(key, group, self.filename)
            else:
                return ""

    # misc
    def groups(self):
        for name, data in sorted(self.content.items(), key=lambda g: g[1]['pos']):
            yield name

    def keys(self, group=None):
        if not group:
            group = self.defaultGroup
        keys = self.content[group]['keys']
        for key, data in sorted(keys.items(), key=lambda k: k[1]['pos']):
            yield key

    def hasGroup(self, group):
        return group in self.content

    def hasKey(self, key, group=None):
        # set default group
        if not group:
            group = self.defaultGroup

        return key in self.content[group]['keys']

    def getFileName(self):
        return self.filename
