import xml.dom.minidom
import unittest

from xdg.Menu import Rule
from xdg.Menu import __parseRule as parseRule


_tests = [
    {
        'doc': """
<Include>
    <And>
        <Category>Accessibility</Category>
        <Not>
            <Category>Settings</Category>
        </Not>
    </And>
    <Filename>screenreader.desktop</Filename>
</Include>
        """,
        'data': [
            ('app1.desktop', ['Accessibility'], True),
            ('app2.desktop', ['Accessibility', 'Settings'], False),
            ('app3.desktop', ['Accessibility', 'Preferences'], True),
            ('app4.desktop', ['Graphics', 'Settings'], False),
            ('screenreader.desktop', ['Utility', 'Other'], True)
        ]
    },
    {
        'doc': """
<Include>
    <And>
        <Category>Settings</Category>
        <Not>
            <Or>
                <Category>System</Category>
                <Category>X-GNOME-Settings-Panel</Category>
                <Filename>foobar.desktop</Filename>
            </Or>
        </Not>
    </And>
</Include>
        """,
        'data': [
            ('app0.desktop', [], False),
            ('app1.desktop', ['Settings'], True),
            ('app2.desktop', ['System', 'Settings'], False),
            ('app3.desktop', ['Games', 'Preferences'], False),
            ('app4.desktop', ['Graphics', 'Settings'], True),
            ('app5.desktop', ['X-GNOME-Settings-Panel', 'Settings'], False),
            ('foobar.desktop', ['Settings', 'Other'], False)
        ]
    },
    # Empty conditions
    {
        'doc': "<Include></Include>",
        'data': [
            ('app0.desktop', ['Graphics', 'Settings'], False),
            ('screenreader.desktop', [], False)
        ]
    },
    {
        'doc': "<Include><Or></Or></Include>",
        'data': [
            ('app0.desktop', ['Graphics', 'Settings'], False),
            ('screenreader.desktop', [], False)
        ]
    },
    {
        'doc': "<Include><And></And></Include>",
        'data': [
            ('app0.desktop', ['Graphics', 'Settings'], False),
            ('screenreader.desktop', [], False)
        ]
    },
    {
        'doc': "<Include><Not></Not></Include>",
        'data': [
            ('app0.desktop', ['Graphics', 'Settings'], False),
            ('screenreader.desktop', [], False)
        ]
    },
    {
        'doc': """
<Include>
    <Filename>screenreader.desktop</Filename>
    <Not></Not>
</Include>
        """,
        'data': [
            ('app0.desktop', ['Graphics', 'Settings'], False),
            ('screenreader.desktop', [], True)
        ]
    },
    {
        'doc': """
<Include>
    <And>
        <Filename>screenreader.desktop</Filename>
        <Not></Not>
    </And>
</Include>
        """,
        'data': [
            ('app0.desktop', ['Graphics', 'Settings'], False),
            ('screenreader.desktop', [], True)
        ]
    },
    # Single condition
    {
        'doc': "<Include><Or><Filename>foobar.desktop</Filename></Or></Include>",
        'data': [
            ('app0.desktop', ['Graphics', 'Settings'], False),
            ('foobar.desktop', [], True)
        ]
    },
    # All
    {
        'doc': "<Include><Or><All/></Or></Include>",
        'data': [
            ('app0.desktop', ['Graphics', 'Settings'], True),
            ('foobar.desktop', [], True)
        ]
    },
    {
        'doc': "<Include><Filename>foobar.desktop</Filename><All/></Include>",
        'data': [
            ('app0.desktop', ['Graphics', 'Settings'], True),
            ('foobar.desktop', [], True)
        ]
    },
    {
        'doc': """
<Include>
    <Filename>foobar.desktop</Filename>
    <Category>Graphics</Category>
    <Not><All/></Not>
</Include>
        """,
        'data': [
            ('app0.desktop', ['Graphics', 'Settings'], True),
            ('app1.desktop', ['Accessibility'], False),
            ('app2.desktop', ['Accessibility', 'Settings'], False),
            ('foobar.desktop', [], True),
        ]
    }
]


class MockMenuEntry(object):

    def __init__(self, id, categories):
        self.DesktopFileID = id
        self.Categories = categories

    def __str__(self):
        return "<%s: %s>" % (self.DesktopFileID, self.Categories)


class RulesTest(unittest.TestCase):
    """Basic rule matching tests"""

    def test_rule_from_node(self):
        for i, test in enumerate(_tests):
            root = xml.dom.minidom.parseString(test['doc']).childNodes[0]
            rule = parseRule(root)
            for j, data in enumerate(test['data']):
                menuentry = MockMenuEntry(data[0], data[1])
                result = eval(rule.code)
                message = "Error in test %s with result set %s: got %s, expected %s"
                assert result == data[2], message % (i, j, result, data[2])

    def test_rule_from_filename(self):
        tests = [
            ('foobar.desktop', 'foobar.desktop', True),
            ('barfoo.desktop', 'foobar.desktop', False)
        ]
        for i, test in enumerate(tests):
            rule = Rule.fromFilename(Rule.TYPE_INCLUDE, test[0])
            menuentry = MockMenuEntry(test[1], [])
            result = eval(rule.code)
            message = "Error with result set %s: got %s, expected %s"
            assert result == test[2], message % (i, result, test[2])
