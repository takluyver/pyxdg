from xdg import RecentFiles
import unittest

class RecentFilesTest(unittest.TestCase):
    def test_get_files(self):
        rf = RecentFiles.RecentFiles()
        rf.parse()
        print(rf.getFiles()[0])
