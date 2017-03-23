#!/usr/bin/python
# coding: utf-8
from xdg.DesktopEntry import DesktopEntry
from xdg.Exceptions import ValidationError, ParsingError, NoKeyError
from xdg.util import u

import resources

import io
import os
import shutil
import re
import tempfile
import unittest

class DesktopEntryTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.tmpdir, "gedit.desktop")
        with io.open(self.test_file, "w", encoding='utf-8') as f:
            f.write(resources.gedit_desktop)
    
    def tearDown(self):
        shutil.rmtree(self.tmpdir)
    
    def test_write_file(self):
        de = DesktopEntry()
        de.parse(self.test_file)
        de.removeKey("Name")
        de.addGroup("Hallo")
        de.set("key", "value", "Hallo")
        
        new_file = os.path.join(self.tmpdir, "test.desktop")
        de.write(new_file, trusted=True)
        
        with io.open(new_file, encoding='utf-8') as f:
            contents = f.read()
        
        assert "[Hallo]" in contents, contents
        assert re.search(r"key\s*=\s*value", contents), contents
        
        # This is missing the Name key, and has an unknown Hallo group, so it
        # shouldn't validate.
        new_entry = DesktopEntry(new_file)
        self.assertRaises(ValidationError, new_entry.validate)
    
    def test_validate(self):
        entry = DesktopEntry(self.test_file)
        entry.validate()
    
    def test_values(self):
        entry = DesktopEntry(self.test_file)
        self.assertEqual(entry.getName(), 'gedit')
        self.assertEqual(entry.getGenericName(), 'Text Editor')
        self.assertEqual(entry.getNoDisplay(), False)
        self.assertEqual(entry.getComment(), 'Edit text files')
        self.assertEqual(entry.getIcon(), 'accessories-text-editor')
        self.assertEqual(entry.getHidden(), False)
        self.assertEqual(entry.getOnlyShowIn(), [])
        self.assertEqual(entry.getExec(), 'gedit %U')
        self.assertEqual(entry.getTerminal(), False)
        self.assertEqual(entry.getMimeTypes(), ['text/plain'])
        self.assertEqual(entry.getCategories(), ['GNOME', 'GTK', 'Utility', 'TextEditor'])
        self.assertEqual(entry.getTerminal(), False)
    
    def test_basic(self):
        entry = DesktopEntry(self.test_file)
        assert entry.hasKey("Categories")
        assert not entry.hasKey("TryExec")
        
        assert entry.hasGroup("Desktop Action Window")
        assert not entry.hasGroup("Desktop Action Door")
    
    def test_unicode_name(self):
        with io.open(self.test_file, "w", encoding='utf-8') as f:
            f.write(resources.unicode_desktop)
        
        entry = DesktopEntry(self.test_file)
        self.assertEqual(entry.getName(), u('Abc€þ'))
    
    def test_invalid(self):
        test_file = os.path.join(self.tmpdir, "spout.desktop")
        with io.open(test_file, "w", encoding='utf-8') as f:
            f.write(resources.spout_desktop)
        
        self.assertRaises(ParsingError, DesktopEntry, test_file)

    def test_invalid_unicode(self):
        test_file = os.path.join(self.tmpdir, "gnome-alsamixer.desktop")
        with io.open(test_file, "w", encoding='latin-1') as f:
            f.write(resources.gnome_alsamixer_desktop)
        
        # Just check this doesn't throw a UnicodeError.
        DesktopEntry(test_file)

class TestTryExec(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.tmpdir, "foo.desktop")

    def test_present(self):
        with io.open(self.test_file, "w", encoding='utf-8') as f:
            f.write(resources.python_desktop)
        
        entry = DesktopEntry(self.test_file)
        res = entry.findTryExec()
        assert res, repr(res)

    def test_absent(self):
        with io.open(self.test_file, "w", encoding='utf-8') as f:
            f.write(resources.unicode_desktop)
        
        entry = DesktopEntry(self.test_file)
        res = entry.findTryExec()
        assert res is None, repr(res)
        
    def test_no_TryExec(self):
        with io.open(self.test_file, "w", encoding='utf-8') as f:
            f.write(resources.gedit_desktop)
        
        entry = DesktopEntry(self.test_file)
        self.assertRaises(NoKeyError, entry.findTryExec)
