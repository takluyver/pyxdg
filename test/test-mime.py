from xdg import Mime
import unittest
import os.path
import tempfile, shutil

import resources

class MimeTestBase(unittest.TestCase):
    def check_mimetype(self, mimetype, media, subtype):
        self.assertEqual(mimetype.media, media)
        self.assertEqual(mimetype.subtype, subtype)

class MimeTest(MimeTestBase):
    def test_get_type_by_name(self):
        appzip = Mime.get_type_by_name("foo.zip")
        self.check_mimetype(appzip, 'application', 'zip')
    
    def test_get_type_by_data(self):
        imgpng = Mime.get_type_by_data(resources.png_data)
        self.check_mimetype(imgpng, 'image', 'png')
    
    def test_get_type_by_contents(self):
        tmpdir = tempfile.mkdtemp()
        try:
            test_file = os.path.join(tmpdir, "test")
            with open(test_file, "wb") as f:
                f.write(resources.png_data)
            
            imgpng = Mime.get_type_by_contents(test_file)
            self.check_mimetype(imgpng, 'image', 'png')
        
        finally:
            shutil.rmtree(tmpdir)
    
    def test_get_type(self):
        tmpdir = tempfile.mkdtemp()
        try:
            # File that doesn't exist - get type by name
            path = os.path.join(tmpdir, "test.png")
            imgpng = Mime.get_type(path)
            self.check_mimetype(imgpng, 'image', 'png')
            
            # File that does exist - get type by contents
            path = os.path.join(tmpdir, "test")
            with open(path, "wb") as f:
                f.write(resources.png_data)
            imgpng = Mime.get_type(path)
            self.check_mimetype(imgpng, 'image', 'png')
        
            # Directory - special case
            path = os.path.join(tmpdir, "test2")
            os.mkdir(path)
            inodedir = Mime.get_type(path)
            self.check_mimetype(inodedir, 'inode', 'directory')
        
        finally:
            shutil.rmtree(tmpdir)
    
    def test_lookup(self):
        pdf1 = Mime.lookup("application/pdf")
        pdf2 = Mime.lookup("application", "pdf")
        self.assertEqual(pdf1, pdf2)
        self.check_mimetype(pdf1, 'application', 'pdf')
        
        pdf1.get_comment()

    def test_by_name(self):
        dot_c = Mime.get_type_by_name('foo.c')
        self.check_mimetype(dot_c, 'text', 'x-csrc')
        dot_C = Mime.get_type_by_name('foo.C')
        self.check_mimetype(dot_C, 'text', 'x-c++src')
    
    def test_canonical(self):
        text_xml = Mime.lookup('text/xml')
        self.check_mimetype(text_xml, 'text', 'xml')
        self.check_mimetype(text_xml.canonical(), 'application', 'xml')
    
    def test_inheritance(self):
        text_python = Mime.lookup('text/x-python')
        self.check_mimetype(text_python, 'text', 'x-python')
        text_plain = Mime.lookup('text/plain')
        app_executable = Mime.lookup('application/x-executable')
        self.assertEqual(text_python.inherits_from(), set([text_plain, app_executable]))

class MagicDBTest(MimeTestBase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.path = os.path.join(self.tmpdir, 'mimemagic')
        with open(self.path, 'wb') as f:
            f.write(resources.mime_magic_db)
        
        # Read the file
        self.magic = Mime.MagicDB()
        self.magic.mergeFile(self.path)
    
    def tearDown(self):
        shutil.rmtree(self.tmpdir)
    
    def test_parsing(self):
        self.assertEqual(len(self.magic.alltypes), 7)
        
        prio, png = self.magic.bytype[Mime.lookup('image', 'png')]
        self.assertEqual(prio, 50)
        assert isinstance(png, Mime.MagicRule), type(png)
        self.assertEqual(png.start, 0)
        self.assertEqual(png.value, b'\x89PNG')
        self.assertEqual(png.mask, None)
        self.assertEqual(png.also, None)
        
        prio, jpeg = self.magic.bytype[Mime.lookup('image', 'jpeg')]
        assert isinstance(jpeg, Mime.MagicMatchAny), type(jpeg)
        self.assertEqual(len(jpeg.rules), 2)
        self.assertEqual(jpeg.rules[0].value, b'\xff\xd8\xff')
        
        prio, ora = self.magic.bytype[Mime.lookup('image', 'openraster')]
        assert isinstance(ora, Mime.MagicRule), type(ora)
        self.assertEqual(ora.value, b'PK\x03\x04')
        ora1 = ora.also
        assert ora1 is not None
        self.assertEqual(ora1.start, 30)
        ora2 = ora1.also
        assert ora2 is not None
        self.assertEqual(ora2.start, 38)
        self.assertEqual(ora2.value, b'image/openraster')
        
        prio, svg = self.magic.bytype[Mime.lookup('image', 'svg+xml')]
        self.assertEqual(len(svg.rules), 2)
        self.assertEqual(svg.rules[0].value, b'<!DOCTYPE svg')
        self.assertEqual(svg.rules[0].range, 257)
        
        prio, psd = self.magic.bytype[Mime.lookup('image', 'vnd.adobe.photoshop')]
        self.assertEqual(psd.value, b'8BPS  \0\0\0\0')
        self.assertEqual(psd.mask, b'\xff\xff\xff\xff\0\0\xff\xff\xff\xff')
        
        prio, elf = self.magic.bytype[Mime.lookup('application', 'x-executable')]
        self.assertEqual(elf.value, b'\x01\x11')
        self.assertEqual(elf.word, 2)
        
        # Test that a newline within the value doesn't break parsing.
        prio, madeup = self.magic.bytype[Mime.lookup('application', 'madeup')]
        self.assertEqual(madeup.value, b'ab\ncd')
    
    def test_match_data(self):
        res = self.magic.match_data(resources.png_data)
        self.check_mimetype(res, 'image', 'png')
        
        # With list of options
        options = [Mime.lookup('image','png'), Mime.lookup('image', 'jpeg')]
        res = self.magic.match_data(resources.png_data, possible=options)
        self.check_mimetype(res, 'image', 'png')
        
        # Non matching
        res = self.magic.match_data(b'oiejgoethetrkjgnwefergoijekngjekg')
        assert res is None, res
    
    def test_match_file(self):
        png_file = os.path.join(self.tmpdir, 'image')
        with open(png_file, 'wb') as f:
            f.write(resources.png_data)
        
        res = self.magic.match(png_file)
        self.check_mimetype(res, 'image', 'png')
        
        # With list of options
        options = [Mime.lookup('image','png'), Mime.lookup('image', 'jpeg')]
        res = self.magic.match(png_file, possible=options)
        self.check_mimetype(res, 'image', 'png')
