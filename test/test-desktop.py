#!/usr/bin/python
from xdg.DesktopEntry import *

import os, sys
import re
import tempfile
import unittest

class DesktopEntryTest(unittest.TestCase):
    def test_write_file(self):
        de = DesktopEntry()
        de.parse("/usr/share/applications/gedit.desktop")
        de.removeKey("Name")
        de.addGroup("Hallo")
        de.set("key", "value", "Hallo")
        
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, "test.desktop")
        de.write(path)
        
        with open(path) as f:
            contents = f.read()
        
        assert "[Hallo]" in contents, contents
        assert re.search("key\s*=\s*value", contents), contents
    
    def test_validate(self):
        entry = DesktopEntry("/usr/share/applications/gedit.desktop")
        self.assertEqual(entry.getName(), 'gedit')
        entry.validate()
