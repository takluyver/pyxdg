from xdg import Mime
import unittest

class MimeTest(unittest.TestCase):
    def test_get_type_by_name(self):
        appzip = Mime.get_type_by_name("foo.zip")
        self.assertEqual(appzip.media, "application")
        self.assertEqual(appzip.subtype, "zip")
