from xdg import Mime
import unittest
import os.path
import tempfile, shutil

import resources

example_dir = os.path.join(os.path.dirname(__file__), 'example')
def example_file(filename):
    return os.path.join(example_dir, filename)

class MimeTestBase(unittest.TestCase):
    def check_mimetype(self, mimetype, media, subtype):
        self.assertEqual(mimetype.media, media)
        self.assertEqual(mimetype.subtype, subtype)

class MimeTest(MimeTestBase):
    def test_create_mimetype(self):
        mt1 = Mime.MIMEtype('application', 'pdf')
        mt2 = Mime.MIMEtype('application', 'pdf')
        self.assertEqual(id(mt1), id(mt2))  # Check caching
        
        amr = Mime.MIMEtype('audio', 'AMR')
        self.check_mimetype(amr, 'audio', 'amr')  # Check lowercase
        
        ogg = Mime.MIMEtype('audio/ogg')
        self.check_mimetype(ogg, 'audio', 'ogg')  # Check split on /
        
        self.assertRaises(Exception, Mime.MIMEtype, 'audio/foo/bar')

    def test_get_type_by_name(self):
        appzip = Mime.get_type_by_name("foo.zip")
        self.check_mimetype(appzip, 'application', 'zip')
    
    def test_get_type_by_data(self):
        imgpng = Mime.get_type_by_data(resources.png_data)
        self.check_mimetype(imgpng, 'image', 'png')
    
    def test_mimetype_repr(self):
        mt = Mime.lookup('application', 'zip')
        repr(mt)   # Just check that this doesn't throw an error.
    
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
        # File that doesn't exist - get type by name
        imgpng = Mime.get_type(example_file("test.gif"))
        self.check_mimetype(imgpng, 'image', 'gif')
        
        # File that does exist - get type by contents
        imgpng = Mime.get_type(example_file("png_file"))
        self.check_mimetype(imgpng, 'image', 'png')
    
        # Directory - special case
        inodedir = Mime.get_type(example_file("subdir"))
        self.check_mimetype(inodedir, 'inode', 'directory')
        
        # Mystery files
        mystery_text = Mime.get_type(example_file('mystery_text'))
        self.check_mimetype(mystery_text, 'text', 'plain')
        mystery_exe = Mime.get_type(example_file('mystery_exe'))
        self.check_mimetype(mystery_exe, 'application', 'executable')
        
        # Symlink
        self.check_mimetype(Mime.get_type(example_file("png_symlink")),
                                    'image', 'png')
        self.check_mimetype(Mime.get_type(example_file("png_symlink"), follow=False),
                                    'inode', 'symlink')

    def test_get_type2(self):
        # File that doesn't exist - use the name
        self.check_mimetype(Mime.get_type2(example_file('test.gif')), 'image', 'gif')
        
        # File that does exist - use the contents
        self.check_mimetype(Mime.get_type2(example_file('png_file')), 'image', 'png')
        
        # Does exist - use name before contents
        self.check_mimetype(Mime.get_type2(example_file('file.png')), 'image', 'png')
        self.check_mimetype(Mime.get_type2(example_file('word.doc')), 'application', 'msword')
        
        # Ambiguous file extension
        glade_mime = Mime.get_type2(example_file('glade.ui'))
        self.assertEqual(glade_mime.media, 'application')
        # Grumble, this is still ambiguous on some systems
        self.assertIn(glade_mime.subtype, {'x-gtk-builder', 'x-glade'})
        self.check_mimetype(Mime.get_type2(example_file('qtdesigner.ui')), 'application', 'x-designer')
        
        # text/x-python has greater weight than text/x-readme
        self.check_mimetype(Mime.get_type2(example_file('README.py')), 'text', 'x-python')
        
        # Directory - special filesystem object
        self.check_mimetype(Mime.get_type2(example_file('subdir')), 'inode', 'directory')
        
        # Mystery files:
        mystery_missing = Mime.get_type2(example_file('mystery_missing'))
        self.check_mimetype(mystery_missing, 'application', 'octet-stream')
        mystery_binary = Mime.get_type2(example_file('mystery_binary'))
        self.check_mimetype(mystery_binary, 'application', 'octet-stream')
        mystery_text = Mime.get_type2(example_file('mystery_text'))
        self.check_mimetype(mystery_text, 'text', 'plain')
        mystery_exe = Mime.get_type2(example_file('mystery_exe'))
        self.check_mimetype(mystery_exe, 'application', 'executable')
        
        # Symlink
        self.check_mimetype(Mime.get_type2(example_file("png_symlink")),
                                    'image', 'png')
        self.check_mimetype(Mime.get_type2(example_file("png_symlink"), follow=False),
                                    'inode', 'symlink')

    def test_get_type_by_filename_and_data(self):
        # File that doesn't exist - use the name
        self.check_mimetype(Mime.get_type_by_filename_and_data('test.gif'), 'image', 'gif')

        # File that does exist - use the contents
        with open(example_file('png_file'), 'rb') as png_data:
            self.check_mimetype(Mime.get_type_by_filename_and_data('png_file', png_data), 'image', 'png')

        # Does exist - use name before contents
        with open(example_file('file.png'), 'rb') as png_data:
            self.check_mimetype(Mime.get_type_by_filename_and_data('file.png', png_data), 'image', 'png')
        with open(example_file('word.doc'), 'rb') as word_data:
            self.check_mimetype(Mime.get_type_by_filename_and_data('word.doc', word_data), 'application', 'msword')

        # Ambiguous file extension
        with open(example_file('glade.ui'), 'rb') as glade_data:
            glade_mime = Mime.get_type_by_filename_and_data('glade.ui', glade_data)
        self.assertEqual(glade_mime.media, 'application')
        # Grumble, this is still ambiguous on some systems
        self.assertIn(glade_mime.subtype, {'x-gtk-builder', 'x-glade'})
        with open(example_file('qtdesigner.ui'), 'rb') as qtdesigner_data:
            self.check_mimetype(Mime.get_type_by_filename_and_data('qtdesigner.ui', qtdesigner_data), 'application', 'x-designer')

        # text/x-python has greater weight than text/x-readme
        with open(example_file('README.py'), 'rb') as python_data:
            self.check_mimetype(Mime.get_type_by_filename_and_data('README.py', png_data), 'text', 'x-python')

        # Mystery files:
        self.check_mimetype(Mime.get_type_by_filename_and_data('mystery_missing'), 'application', 'octet-stream')
        with open(example_file('mystery_binary'), 'rb') as mystery_data:
            self.check_mimetype(Mime.get_type_by_filename_and_data('mystery_binary', mystery_data), 'application', 'octet-stream')
        with open(example_file('mystery_text'), 'rb') as mystery_data:
            self.check_mimetype(Mime.get_type_by_filename_and_data('mystery_text', mystery_data), 'text', 'plain')

    def test_lookup(self):
        pdf1 = Mime.lookup("application/pdf")
        pdf2 = Mime.lookup("application", "pdf")
        self.assertEqual(pdf1, pdf2)
        self.check_mimetype(pdf1, 'application', 'pdf')
    
    def test_get_comment(self):
        # Check these don't throw an error. One that is likely to exist:
        Mime.MIMEtype("application", "pdf").get_comment()
        # And one that's unlikely to exist:
        Mime.MIMEtype("application", "ierjg").get_comment()

    def test_by_name(self):
        dot_c = Mime.get_type_by_name('foo.c')
        self.check_mimetype(dot_c, 'text', 'x-csrc')
        dot_C = Mime.get_type_by_name('foo.C')
        self.check_mimetype(dot_C, 'text', 'x-c++src')
        
        # But most names should be case insensitive
        dot_GIF = Mime.get_type_by_name('IMAGE.GIF')
        self.check_mimetype(dot_GIF, 'image', 'gif')
    
    def test_canonical(self):
        text_xml = Mime.lookup('text/xml')
        self.check_mimetype(text_xml, 'text', 'xml')
        self.check_mimetype(text_xml.canonical(), 'application', 'xml')
        
        # Already is canonical
        python = Mime.lookup('text/x-python')
        self.check_mimetype(python.canonical(), 'text', 'x-python')
    
    def test_inheritance(self):
        text_python = Mime.lookup('text/x-python')
        self.check_mimetype(text_python, 'text', 'x-python')
        text_plain = Mime.lookup('text/plain')
        app_executable = Mime.lookup('application/x-executable')
        self.assertEqual(text_python.inherits_from(), set([text_plain, app_executable]))
    
    def test_is_text(self):
        assert Mime._is_text(b'abcdef \n')
        assert not Mime._is_text(b'abcdef\x08')
        assert not Mime._is_text(b'abcdef\x0e')
        assert not Mime._is_text(b'abcdef\x1f')
        assert not Mime._is_text(b'abcdef\x7f')
        
        # Check nonexistant file.
        assert not Mime.is_text_file('/fwoijorij')

class MagicDBTest(MimeTestBase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.path = os.path.join(self.tmpdir, 'mimemagic')
        with open(self.path, 'wb') as f:
            f.write(resources.mime_magic_db)
        
        self.path2 = os.path.join(self.tmpdir, 'mimemagic2')
        with open(self.path2, 'wb') as f:
            f.write(resources.mime_magic_db2)
        
        # Read the files
        self.magic = Mime.MagicDB()
        self.magic.merge_file(self.path)
        self.magic.merge_file(self.path2)
        self.magic.finalise()
    
    def tearDown(self):
        shutil.rmtree(self.tmpdir)
    
    def test_parsing(self):
        self.assertEqual(len(self.magic.bytype), 9)
        
        # Check repr() doesn't throw an error
        repr(self.magic)
        
        prio, png = self.magic.bytype[Mime.lookup('image', 'png')][0]
        self.assertEqual(prio, 50)
        assert isinstance(png, Mime.MagicRule), type(png)
        repr(png)    # Check this doesn't throw an error.
        self.assertEqual(png.start, 0)
        self.assertEqual(png.value, b'\x89PNG')
        self.assertEqual(png.mask, None)
        self.assertEqual(png.also, None)
        
        prio, jpeg = self.magic.bytype[Mime.lookup('image', 'jpeg')][0]
        assert isinstance(jpeg, Mime.MagicMatchAny), type(jpeg)
        self.assertEqual(len(jpeg.rules), 2)
        self.assertEqual(jpeg.rules[0].value, b'\xff\xd8\xff')
        
        prio, ora = self.magic.bytype[Mime.lookup('image', 'openraster')][0]
        assert isinstance(ora, Mime.MagicRule), type(ora)
        self.assertEqual(ora.value, b'PK\x03\x04')
        ora1 = ora.also
        assert ora1 is not None
        self.assertEqual(ora1.start, 30)
        ora2 = ora1.also
        assert ora2 is not None
        self.assertEqual(ora2.start, 38)
        self.assertEqual(ora2.value, b'image/openraster')
        
        prio, svg = self.magic.bytype[Mime.lookup('image', 'svg+xml')][0]
        self.assertEqual(len(svg.rules), 2)
        self.assertEqual(svg.rules[0].value, b'<!DOCTYPE svg')
        self.assertEqual(svg.rules[0].range, 257)
        
        prio, psd = self.magic.bytype[Mime.lookup('image', 'vnd.adobe.photoshop')][0]
        self.assertEqual(psd.value, b'8BPS  \0\0\0\0')
        self.assertEqual(psd.mask, b'\xff\xff\xff\xff\0\0\xff\xff\xff\xff')
        
        prio, elf = self.magic.bytype[Mime.lookup('application', 'x-executable')][0]
        self.assertEqual(elf.value, b'\x01\x11')
        self.assertEqual(elf.word, 2)
        
        # Test that a newline within the value doesn't break parsing.
        prio, madeup = self.magic.bytype[Mime.lookup('application', 'madeup')][0]
        self.assertEqual(madeup.rules[0].value, b'ab\ncd')
        self.assertEqual(madeup.rules[1].mask, b'\xff\xff\n\xff\xff')
        
        prio, replaced = self.magic.bytype[Mime.lookup('application', 'tobereplaced')][0]
        self.assertEqual(replaced.value, b'jkl')
        
        addedrules = self.magic.bytype[Mime.lookup('application', 'tobeaddedto')]
        self.assertEqual(len(addedrules), 2)
        self.assertEqual(addedrules[1][1].value, b'pqr')
    
    def test_match_data(self):
        res = self.magic.match_data(resources.png_data)
        self.check_mimetype(res, 'image', 'png')
        
        # Denied by min or max priority
        notpng_max40 = self.magic.match_data(resources.png_data, max_pri=40)
        assert notpng_max40 is None, notpng_max40
        notpng_min60 = self.magic.match_data(resources.png_data, min_pri=60)
        assert notpng_min60 is None, notpng_min60
        
        # With list of options
        options = [Mime.lookup('image', 'nonexistant'), # Missing MIMEtype should be dropped
                   Mime.lookup('image','png'), Mime.lookup('image', 'jpeg')]
        res = self.magic.match_data(resources.png_data, possible=options)
        self.check_mimetype(res, 'image', 'png')
        
        # Non matching
        res = self.magic.match_data(b'oiejgoethetrkjgnwefergoijekngjekg')
        assert res is None, res
    
    def test_match_nested(self):
        data = b'PK\x03\x04' + (b' ' * 26) + b'mimetype' + b'image/openraster'
        res = self.magic.match_data(data)
        self.check_mimetype(res, 'image', 'openraster')
    
    def test_match_file(self):
        png_file = os.path.join(self.tmpdir, 'image')
        with open(png_file, 'wb') as f:
            f.write(resources.png_data)
        
        res = self.magic.match(png_file)
        self.check_mimetype(res, 'image', 'png')
        
        # With list of options
        options = [Mime.lookup('image','png'), Mime.lookup('image', 'jpeg'),
                   Mime.lookup('image', 'nonexistant')]  # Missing MIMEtype should be dropped
        res = self.magic.match(png_file, possible=options)
        self.check_mimetype(res, 'image', 'png')
        
        # Nonexistant file
        path = os.path.join(self.tmpdir, 'nonexistant')
        self.assertRaises(IOError, self.magic.match, path)

_l = Mime.lookup

class GlobDBTest(MimeTestBase):
    allglobs = {_l('text/x-makefile'): [(50, 'makefile', [])],
                _l('application/x-core'): [(50, 'core', ['cs']), (50, 'core', [])],
                _l('text/x-c++src'): [(50, '*.C', ['cs'])],
                _l('text/x-csrc'): [(50, '*.c', ['cs'])],
                _l('text/x-python'): [(50, '*.py', [])],
                _l('text/x-python'): [(50, '*.py', [])],    # Check not added 2x
                _l('video/x-anim'): [(50, '*.anim[1-9j]', [])],
                _l('text/x-readme'): [(10, 'readme*', [])],
                _l('text/x-readme2'): [(20, 'readme2*', [])],
                _l('image/jpeg'): [(50, '*.jpg', []), (50, '*.jpeg', [])],
               }
    
    def setUp(self):
        self.globs = Mime.GlobDB()
        self.globs.allglobs = self.allglobs
        self.globs.finalise()

    def test_build_globdb(self):
        globs = self.globs
        
        self.assertEqual(len(globs.cased_literals), 1)
        assert 'core' in globs.cased_literals, globs.cased_literals
        
        literals = globs.literals
        self.assertEqual(len(literals), 2)
        assert 'core' in literals, literals
        assert 'makefile' in literals, literals
        
        cexts = globs.cased_exts
        self.assertEqual(len(cexts), 2)
        assert 'C' in cexts, cexts
        assert 'c' in cexts, cexts
        
        exts = globs.exts
        self.assertEqual(len(exts), 3)
        assert 'py' in exts, exts
        self.assertEqual(exts['py'], [(_l('text/x-python'), 50)] )
        assert 'jpeg' in exts, exts
        assert 'jpg' in exts, exts
        
        pats = globs.globs
        self.assertEqual(len(pats), 3)
        self.assertEqual(pats[0][1], _l('video', 'x-anim'))
        self.assertEqual(pats[1][1], _l('text', 'x-readme2'))

    def test_first_match(self):
        g = self.globs
        
        self.check_mimetype(g.first_match('Makefile'), 'text', 'x-makefile')
        self.check_mimetype(g.first_match('core'), 'application', 'x-core')
        self.check_mimetype(g.first_match('foo.C'), 'text', 'x-c++src')
        self.check_mimetype(g.first_match('foo.c'), 'text', 'x-csrc')
        self.check_mimetype(g.first_match('foo.py'), 'text', 'x-python')
        self.check_mimetype(g.first_match('foo.Anim4'), 'video', 'x-anim')
        self.check_mimetype(g.first_match('README.txt'), 'text', 'x-readme')
        self.check_mimetype(g.first_match('README2.txt'), 'text', 'x-readme2')
        self.check_mimetype(g.first_match('README'), 'text', 'x-readme')
        
        qrte = g.first_match('qrte')
        assert qrte is None, qrte
    
    def test_all_matches(self):
        g = self.globs
        
        self.assertEqual(g.all_matches('qrte'), [])
        
        self.assertEqual(g.all_matches('Makefile'), 
                                    [(_l('text', 'x-makefile'), 50)])
        
        self.assertEqual(g.all_matches('readme2.rst'),
                                [(_l('text', 'x-readme2'), 20),
                                 (_l('text', 'x-readme'), 10)]
                                 )
    
    def test_get_extensions(self):
        Mime.globs = self.globs
        Mime._cache_uptodate = True
        
        try:
            get_ext = Mime.get_extensions
            self.assertEqual(get_ext(_l('text/x-python')), set(['py']))
            self.assertEqual(get_ext(_l('image/jpeg')), set(['jpg', 'jpeg']))
            self.assertEqual(get_ext(_l('image/inary')), set())
        finally:
            # Ensure that future tests will re-cache the database.
            Mime._cache_uptodate = False


class GlobsParsingTest(MimeTestBase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.tmpdir)
    
    def test_parsing(self):
        p1 = os.path.join(self.tmpdir, 'globs2a')
        with open(p1, 'w') as f:
            f.write(resources.mime_globs2_a)
        
        p2 = os.path.join(self.tmpdir, 'globs2b')
        with open(p2, 'w') as f:
            f.write(resources.mime_globs2_b)
        
        globs = Mime.GlobDB()
        globs.merge_file(p1)
        globs.merge_file(p2)
        
        ag = globs.allglobs
        self.assertEqual(ag[_l('text', 'x-diff')],
                                set([(55, '*.patch', ()), (50, '*.diff', ())]) )
        self.assertEqual(ag[_l('text', 'x-c++src')], set([(50, '*.C', ('cs',))]) )
        self.assertEqual(ag[_l('text', 'x-readme')], set([(20, 'RDME', ('cs',))]) )
        assert _l('text', 'x-python') not in ag, ag
