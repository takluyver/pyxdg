from xdg import RecentFiles
import resources

import unittest
import os.path
import tempfile, shutil

class RecentFilesTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.tmpdir, ".recently-used")
        with open(self.test_file, "w") as f:
            f.write(resources.recently_used)
    
    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_get_files(self):
        rf = RecentFiles.RecentFiles()
        rf.parse(self.test_file)
        last_file = rf.getFiles()[0]
        self.assertEqual(last_file.URI, "file:///home/thomas/foo/bar.ods")
        self.assertEqual(last_file.MimeType, "application/vnd.oasis.opendocument.spreadsheet")
    
    def test_modify(self):
        rf = RecentFiles.RecentFiles()
        rf.parse(self.test_file)
        
        rf.deleteFile("file:///home/thomas/foo/bar.ods")
        self.assertEqual(len(rf.RecentFiles), 1)
        
        rf.addFile("file:///home/thomas/foo/baz.png", "image/png")
        self.assertEqual(len(rf.RecentFiles), 2)
        
        new_file = os.path.join(self.tmpdir, ".new-recently-used")
        rf.write(new_file)
        
        rf2 = RecentFiles.RecentFiles()
        rf2.parse(new_file)
        
        last_file = rf.getFiles()[0]
        self.assertEqual(last_file.URI, "file:///home/thomas/foo/baz.png")
        self.assertEqual(last_file.MimeType, "image/png")
        
