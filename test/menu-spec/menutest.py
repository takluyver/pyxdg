#! /usr/bin/python
# coding=utf8
"""
Script to run the xdg menu-spec tests:
$ git clone git://anongit.freedesktop.org/xdg/xdg-specs
$ cd xdg-specs/menu/tests
$ MENUTEST="/path/to/pyxdg/test/menu-spec/menutest.py" ./menutest
"""

from __future__ import print_function
import os
import sys


__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, '{}/../../'.format(__dir__))


from xdg.Menu import XMLMenuBuilder, Menu, MenuEntry


def print_directory(directory):
    for entry in directory.getEntries():
        if isinstance(entry, Menu):
            print_directory(entry)
        elif isinstance(entry, MenuEntry):
            print_entry(entry, directory.getPath())


def print_entry(entry, menupath):
    filepath = entry.DesktopEntry.getFileName().encode('utf8')
    id = entry.DesktopFileID.encode('utf8')
    menupath = menupath.encode('utf8')
    print('{}/\t{}\t{}'.format(menupath, id, filepath))


if __name__ == "__main__":
    builder = XMLMenuBuilder()
    root = builder.parse()
    print_directory(root)
    sys.exit(0)
