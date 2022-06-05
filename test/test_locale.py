from xdg import Locale
import unittest

class LocaleTest(unittest.TestCase):
    def test_expand_languages(self):
        langs = Locale.expand_languages()
        assert isinstance(langs, list)
