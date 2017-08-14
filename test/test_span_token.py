import unittest
import test.helpers as helpers
import mistletoe.span_token as span_token

class TestEscapeSequence(unittest.TestCase):
    def test_escape(self):
        t = span_token.Strong('some \*text*')
        c0 = span_token.RawText('some ')
        c1 = span_token.EscapeSequence('*')
        c2 = span_token.RawText('text*')
        l = list(t.children)
        helpers.check_equal(self, l[0], c0)
        helpers.check_equal(self, l[1], c1)
        helpers.check_equal(self, l[2], c2)

class TestRawText(unittest.TestCase):
    def test_equal(self):
        t1 = span_token.RawText('some text')
        t2 = span_token.RawText('some text')
        helpers.check_equal(self, t1, t2)

class TestLink(unittest.TestCase):
    def test_equal(self):
        t1 = span_token.Link('[name 1](target 1)')
        t2 = span_token.Link('[name 1](target 1)')
        helpers.check_equal(self, t1, t2)

    def test_multi_links(self):
        t = span_token.Emphasis('[name 1](target 1) and [name 2](target 2)')
        c0 = span_token.Link('[name 1](target 1)')
        c1 = span_token.RawText(' and ')
        c2 = span_token.Link('[name 2](target 2)')
        l = list(t.children)
        helpers.check_equal(self, l[0], c0)
        helpers.check_equal(self, l[1], c1)
        helpers.check_equal(self, l[2], c2)

    def test_link_with_children(self):
        t = span_token.Link('[![alt](src)](target)')
        c = span_token.Image('![alt](src)')
        target = 'target'
        helpers.check_equal(self, list(t.children)[0], c)
        self.assertEqual(t.target, target)

class TestFootnoteLink(unittest.TestCase):
    def test_raw(self):
        t = span_token.FootnoteLink('[alt] [key]')
        c = span_token.RawText('alt')
        helpers.check_equal(self, list(t.children)[0], c)
        helpers.check_equal(self, t.target, span_token.FootnoteAnchor('key'))

class TestAutoLink(unittest.TestCase):
    def test(self):
        t = span_token.Strong('some <link> in strong text')
        c0 = span_token.RawText('some ')
        c1 = span_token.AutoLink('link')
        c2 = span_token.RawText(' in strong text')
        l = list(t.children)
        helpers.check_equal(self, l[0], c0)
        helpers.check_equal(self, l[1], c1)
        helpers.check_equal(self, l[2], c2)

class TestImage(unittest.TestCase):
    def test_equal(self):
        t1 = span_token.Image('![alt](link)')
        t2 = span_token.Image('![alt](link)')
        helpers.check_equal(self, t1, t2)

class TestFootnoteImage(unittest.TestCase):
    def test_raw(self):
        t = span_token.FootnoteImage('![alt] [key]')
        c = span_token.FootnoteAnchor('key')
        self.assertEqual(t.alt, 'alt')
        helpers.check_equal(self, t.src, c)

class TestStrong(unittest.TestCase):
    def test_raw(self):
        t = span_token.Strong('some text')
        c = span_token.RawText('some text')
        helpers.check_equal(self, list(t.children)[0], c)

class TestEmphasis(unittest.TestCase):
    def test_raw(self):
        t = span_token.Emphasis('some text')
        c = span_token.RawText('some text')
        helpers.check_equal(self, list(t.children)[0], c)

    def test_parse(self):
        t = span_token.Strong('_some text_')
        c = span_token.Emphasis('some text')
        helpers.check_equal(self, list(t.children)[0], c)

class TestInlineCode(unittest.TestCase):
    def test_raw(self):
        t = span_token.InlineCode('some code')
        c = span_token.RawText('some code')
        helpers.check_equal(self, list(t.children)[0], c)

class TestStrikethrough(unittest.TestCase):
    def test_raw(self):
        t = span_token.Strikethrough('some text')
        c = span_token.RawText('some text')
        helpers.check_equal(self, list(t.children)[0], c)
