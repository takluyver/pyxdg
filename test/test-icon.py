#!/usr/bin/python
from xdg.IconTheme import *
import tempfile, shutil
import unittest

import resources

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

class IconDataTest(unittest.TestCase):
    def test_read_icon_data(self):
        tmpdir = tempfile.mkdtemp()
        png_file = os.path.join(tmpdir, "test.png")
        with open(png_file, "wb") as f:
            f.write(resources.png_data)
        
        icon_file = os.path.join(tmpdir, "test.icon")
        with open(icon_file, "w") as f:
            f.write(resources.icon_data)
        
        icondata = getIconData(png_file)
        
        self.assertEqual(icondata.getDisplayName(), 'Mime text/plain')
        self.assertEqual(icondata.getAttachPoints(), [(200,200), (800,200), (500,500), (200,800), (800,800)])
        self.assertEqual(icondata.getEmbeddedTextRectangle(), [100,100,900,900])
        
