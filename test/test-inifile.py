#!/usr/bin/python
# coding: utf-8
from xdg import IniFile
from xdg.util import u

import unittest

class IniFileTest(unittest.TestCase):
    def test_check_string(self):
        i = IniFile.IniFile()
        self.assertEqual(i.checkString(u('abc')), 0)
        self.assertEqual(i.checkString('abc'), 0)
        self.assertEqual(i.checkString(u('abcö')), 1)
        self.assertEqual(i.checkString('abcö'), 1)
    
    def test_modify(self):
        i = IniFile.IniFile()
        i.addGroup('foo')
        i.set('bar', u('wallöby'), group='foo')
        self.assertEqual(i.get('bar', group='foo'), u('wallöby'))
        
        i.removeKey('bar', group='foo')
        i.removeGroup('foo')
