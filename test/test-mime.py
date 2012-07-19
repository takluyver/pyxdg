from xdg import Mime
import unittest
import os.path
import tempfile, shutil

import resources

class MimeTest(unittest.TestCase):
    def test_get_type_by_name(self):
        appzip = Mime.get_type_by_name("foo.zip")
        self.assertEqual(appzip.media, "application")
        self.assertEqual(appzip.subtype, "zip")
    
    def test_get_type_by_data(self):
        imgpng = Mime.get_type_by_data(resources.png_data)
        self.assertEqual(imgpng.media, "image")
        self.assertEqual(imgpng.subtype, "png")
    
    def test_get_type_by_contents(self):
        tmpdir = tempfile.mkdtemp()
        try:
            test_file = os.path.join(tmpdir, "test")
            with open(test_file, "wb") as f:
                f.write(resources.png_data)
            
            imgpng = Mime.get_type_by_contents(test_file)
            self.assertEqual(imgpng.media, "image")
            self.assertEqual(imgpng.subtype, "png")
        
        finally:
            shutil.rmtree(tmpdir)
    
    def test_lookup(self):
        pdf1 = Mime.lookup("application/pdf")
        pdf2 = Mime.lookup("application", "pdf")
        self.assertEqual(pdf1, pdf2)
        self.assertEqual(pdf1.media, "application")
        self.assertEqual(pdf1.subtype, "pdf")
