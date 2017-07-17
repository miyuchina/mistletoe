import unittest
import test.test_core.helpers as helpers
import core.leaf_token as leaf_token

class TestEscapeSequence(unittest.TestCase):
    def test_escape(self):
        t = leaf_token.Strong('some \*text*')
        c0 = leaf_token.RawText('some ')
        c1 = leaf_token.EscapeSequence('*')
        c2 = leaf_token.RawText('text*')
        l = list(t.children)
        helpers.check_equal(self, l[0], c0)
        helpers.check_equal(self, l[1], c1)
        helpers.check_equal(self, l[2], c2)

class TestRawText(unittest.TestCase):
    def test_equal(self):
        t1 = leaf_token.RawText('some text')
        t2 = leaf_token.RawText('some text')
        helpers.check_equal(self, t1, t2)

class TestLink(unittest.TestCase):
    def test_equal(self):
        t1 = leaf_token.Link('[name 1](target 1)')
        t2 = leaf_token.Link('[name 1](target 1)')
        helpers.check_equal(self, t1, t2)

    def test_multi_links(self):
        t = leaf_token.Emphasis('[name 1](target 1) and [name 2](target 2)')
        c0 = leaf_token.Link('[name 1](target 1)')
        c1 = leaf_token.RawText(' and ')
        c2 = leaf_token.Link('[name 2](target 2)')
        l = list(t.children)
        helpers.check_equal(self, l[0], c0)
        helpers.check_equal(self, l[1], c1)
        helpers.check_equal(self, l[2], c2)

    def test_link_with_children(self):
        t = leaf_token.Link('[![alt](src)](target)')
        c = leaf_token.Image('![alt](src)')
        target = 'target'
        helpers.check_equal(self, list(t.children)[0], c)
        self.assertEqual(t.target, target)

class TestImage(unittest.TestCase):
    def test_equal(self):
        t1 = leaf_token.Image('![alt](link)')
        t2 = leaf_token.Image('![alt](link)')
        helpers.check_equal(self, t1, t2)

class TestStrong(unittest.TestCase):
    def test_raw(self):
        t = leaf_token.Strong('some text')
        c = leaf_token.RawText('some text')
        helpers.check_equal(self, list(t.children)[0], c)

class TestEmphasis(unittest.TestCase):
    def test_raw(self):
        t = leaf_token.Emphasis('some text')
        c = leaf_token.RawText('some text')
        helpers.check_equal(self, list(t.children)[0], c)

class TestInlineCode(unittest.TestCase):
    def test_raw(self):
        t = leaf_token.InlineCode('some code')
        c = leaf_token.RawText('some code')
        helpers.check_equal(self, list(t.children)[0], c)

class TestStrikethrough(unittest.TestCase):
    def test_raw(self):
        t = leaf_token.Strikethrough('some text')
        c = leaf_token.RawText('some text')
        helpers.check_equal(self, list(t.children)[0], c)
