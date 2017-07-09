import unittest
import core.leaf_token as leaf_token

class TestBold(unittest.TestCase):
    def test_render(self):
        self.assertEqual(leaf_token.Bold('**a str**').render(), '<b>a str</b>')

    def test_escape(self):
        self.assertEqual(leaf_token.Bold('**an &**').render(), '<b>an &amp;</b>')

class TestItalic(unittest.TestCase):
    def test_render(self):
        self.assertEqual(leaf_token.Italic('*a str*').render(), '<em>a str</em>')

    def test_escape(self):
        self.assertEqual(leaf_token.Italic('*an &*').render(), '<em>an &amp;</em>')

class TestInlineCode(unittest.TestCase):
    def test_render(self):
        token = leaf_token.InlineCode('`rm dir`')
        self.assertEqual(token.render(), '<code>rm dir</code>')

    def test_escape(self):
        token = leaf_token.InlineCode('`<html></html>`')
        output = '<code>&lt;html&gt;&lt;/html&gt;</code>'
        self.assertEqual(token.render(), output)

class TestStrikethrough(unittest.TestCase):
    def test_render(self):
        token = leaf_token.Strikethrough('~~deleted text~~')
        self.assertEqual(token.render(), '<del>deleted text</del>')

    def test_escape(self):
        token = leaf_token.Strikethrough('~~deleted &~~')
        output = '<del>deleted &amp;</del>'
        self.assertEqual(token.render(), output)

class TestLink(unittest.TestCase):
    def test_render(self):
        token = leaf_token.Link('[link name](link target)')
        output = '<a href="link target">link name</a>'
        self.assertEqual(token.render(), output)

class TestRawText(unittest.TestCase):
    def test_render(self):
        self.assertEqual(leaf_token.RawText('some text').render(), 'some text')

    def test_escape(self):
        self.assertEqual(leaf_token.RawText('an &').render(), 'an &amp;')
