import sys
import os
import xml.dom.minidom
import unittest

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..'))

from xdg.Menu import Rule


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
    }
]


class MockMenuEntry(object):

    def __init__(self, id, categories):
        self.DesktopFileID = id
        self.Categories = categories

    def __str__(self):
        return "<%s: %s>" % (self.DesktopFileID, self.Categories)


def evaluate(rule, entry):
    rule.visitRule(rule.Rule, entry)
    return rule.Rule.evaluate()


class RulesTest(unittest.TestCase):
    """Basic rule matching tests"""

    def test_rules(self):
        for test in _tests:
            root = xml.dom.minidom.parseString(test['doc']).childNodes[0]
            type = root.tagName
            rule = Rule(type, root)
            for i, data in enumerate(test['data']):
                menuentry = MockMenuEntry(data[0], data[1])
                result = evaluate(rule, menuentry)
                message = "Error with result set %s: got %s, expected %s"
                assert result == data[2], message % (i, result, data[2])
