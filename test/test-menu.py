#!/usr/bin/python
from __future__ import print_function

import io
import os
import os.path
import shutil
import tempfile
import unittest

import xdg.Menu
import xdg.DesktopEntry
import resources

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

def entry_names(entries):
    names = []
    for entry in entries:
        if isinstance(entry, xdg.Menu.Menu):
            names.append(entry.getName())
        elif isinstance(entry, xdg.Menu.MenuEntry):
            names.append(entry.DesktopEntry.getName())
        elif isinstance(entry, xdg.Menu.Separator):
            names.append("---")
        elif isinstance(entry, xdg.Menu.Header):
            names.append(entry.Name)
    return names

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

    def test_parse_layout(self):
        test_file = os.path.join(self.tmpdir, "layout.menu")
        with io.open(test_file, "w") as f:
            f.write(resources.layout_menu)
        menu = xdg.Menu.parse(test_file)
        show_menu(menu)

        assert len(menu.Entries) == 4
        assert entry_names(menu.Entries) == ["Accessories", "Games", "---", "More"]

        games_menu = menu.getMenu("Games")
        assert len(games_menu.Entries) == 4
        assert entry_names(games_menu.Entries) == ["Steam", "---", "Action", "Arcade"]

    def test_unicode_menuentry(self):
        test_file = os.path.join(self.tmpdir, "unicode.desktop")
        with io.open(test_file, 'w', encoding='utf-8') as f:
            f.write(resources.unicode_desktop)

        entry = xdg.Menu.MenuEntry(test_file)
        assert entry == entry
        assert not entry < entry

    def test_empty_legacy_dirs(self):
        legacy_dir = os.path.join(self.tmpdir, "applnk")
        os.mkdir(legacy_dir)
        os.mkdir(os.path.join(legacy_dir, "Toys"))
        os.mkdir(os.path.join(legacy_dir, "Utilities"))
        test_file = os.path.join(self.tmpdir, "legacy.menu")
        with open(test_file, "w") as f:
            f.write(resources.legacy_menu.replace("legacy_dir", legacy_dir))

        menu = xdg.Menu.parse(test_file)

        # The menu should be empty besides the root named "Legacy"
        show_menu(menu)

        assert len(menu.Entries) == 0

    def test_kde_legacy_dirs(self):
        """This was failing on systems which didn't have kde-config installed.
        We just check that parsing doesn't throw an error.

        See fd.o bug #56426.
        """
        test_file = os.path.join(self.tmpdir, "kde_legacy.menu")
        with open(test_file, "w") as f:
            f.write(resources.kde_legacy_menu)

        menu = xdg.Menu.parse(test_file)


if __name__ == '__main__':
    unittest.main()
