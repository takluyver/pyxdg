#!/usr/bin/python
from xdg.IconTheme import *
import unittest

class IconThemeTest(unittest.TestCase):
    def test_find_icon_exists(self):
        print("Finding an icon that probably exists:")
        print (getIconPath("firefox"))

    def test_find_icon_nonexistant(self):
        icon = getIconPath("oijeorjewrjkngjhbqefew")
        assert icon is None, "%r is not None" % icon
    
    def test_validate_icon_theme(self):
        theme = IconTheme()
        theme.parse("/usr/share/icons/hicolor/index.theme")
        theme.validate()
