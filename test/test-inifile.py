#!/usr/bin/env python3
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
        
        self.assertEqual(list(i.groups()), ['foo'])
        
        i.removeKey('bar', group='foo')
        i.removeGroup('foo')
    
    def test_value_types(self):
        i = IniFile.IniFile()
        i.addGroup('foo')
        i.defaultGroup = 'foo'
        
        # Numeric
        i.errors = []
        i.set('num', '12.3')
        i.checkValue('num', '12.3', type='numeric')
        self.assertEqual(i.errors, [])
        i.checkValue('num', '12.a', type='numeric')
        self.assertEqual(len(i.errors), 1)
        self.assertEqual(i.get('num', type='numeric'), 12.3)
        
        # Regex
        i.errors = []
        i.set('re', '[1-9]+')
        i.checkValue('re', '[1-9]+', type='regex')
        self.assertEqual(i.errors, [])
        i.checkValue('re', '[1-9+', type='regex')
        self.assertEqual(len(i.errors), 1)
        r = i.get('re', type='regex')
        assert r.match('123')
        
        # Point
        i.errors = []
        i.set('pt', '3,12')
        i.checkValue('pt', '3,12', type='point')
        self.assertEqual(i.errors, [])
        i.checkValue('pt', '3,12,5', type='point')
        self.assertEqual(len(i.errors), 1)
        x,y = i.get('pt', type='point')
        
        # Boolean
        i.errors = []
        i.warnings = []
        i.set('boo', 'true')
        i.checkValue('boo', 'true', type='boolean')
        self.assertEqual(i.errors, [])
        i.checkValue('boo', '1', type='boolean')
        self.assertEqual(len(i.warnings), 1)
        self.assertEqual(i.errors, [])
        i.checkValue('boo', 'verily', type='boolean')
        self.assertEqual(len(i.errors), 1)
        boo = i.get('boo', type='boolean')
        assert boo is True, boo
        
        # Integer
        i.errors = []
        i.set('int', '44')
        i.checkValue('int', '44', type='integer')
        self.assertEqual(i.errors, [])
        i.checkValue('int', 'A4', type='integer')
        self.assertEqual(len(i.errors), 1)
        self.assertEqual(i.get('int', type='integer'), 44)
