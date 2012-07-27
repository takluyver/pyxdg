#!/usr/bin/python
# coding: utf-8
from __future__ import print_function

import io
import os
import shutil
import sys
import tempfile
import unittest
import warnings

import xdg.Menu
import xdg.DesktopEntry
import xdg.BaseDirectory
from xdg.util import u
import resources

try:
    reload
except NameError:
    from imp import reload

def show_menu(menu, depth = 0):
    print(depth*"-" + "\x1b[01m" + menu.getName() + "\x1b[0m")
    depth += 1
    for entry in menu.getEntries():
        if isinstance(entry, xdg.Menu.Menu):
            show_menu(entry, depth)
        elif isinstance(entry, xdg.Menu.MenuEntry):
            print(depth*"-" + entry.DesktopEntry.getName())
            print(depth*" " + menu.getPath(), entry.DesktopFileID, entry.DesktopEntry.getFileName())
        elif isinstance(entry, xdg.Menu.Separator):
            print(depth*"-" + "|||")
        elif isinstance(entry, xdg.Menu.Header):
            print(depth*"-" + "\x1b[01m" + entry.Name + "\x1b[0m")
    depth -= 1

class MenuTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.tmpdir, "applications.menu")
        with open(self.test_file, "w") as f:
            f.write(resources.applications_menu)
    
    def tearDown(self):
        shutil.rmtree(self.tmpdir)
    
    def test_parse_menu(self):
        menu = xdg.Menu.parse(self.test_file)
        show_menu(menu)
        
        # Check these don't throw an error
        menu.getName()
        menu.getGenericName()
        menu.getComment()
        menu.getIcon()
    
    def test_unicode_menuentry(self):
        test_file = os.path.join(self.tmpdir, "unicode.desktop")
        with io.open(test_file, 'w', encoding='utf-8') as f:
            f.write(resources.unicode_desktop)
        
        entry = xdg.Menu.MenuEntry(test_file)
        assert entry == entry
        assert not entry < entry
    
    def test_unicode_filename(self):
        # https://bugs.freedesktop.org/show_bug.cgi?id=52516
        with open(self.test_file, "w") as f:
            f.write("<Menu> <DefaultMergeDirs/> </Menu>")
        mergedir = os.path.join(self.tmpdir, "menus", "applications-merged")
        os.makedirs(mergedir)
        unicode_file = os.path.join(mergedir, u("ab€.menu"))
        # Create file (empty)
        with open(unicode_file, "w"): pass
        with open(os.path.join(mergedir, "ab.desktop"), "w"): pass
        
        
        os.environ['XDG_CONFIG_HOME'] = self.tmpdir
        reload(xdg.BaseDirectory)
        reload(xdg.DesktopEntry)
        reload(xdg.Menu)
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            xdg.Menu.parse(self.test_file)
            assert len(w)==0, w
