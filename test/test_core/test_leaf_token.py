import unittest
import core.leaf_token as leaf_token

class TestRawText(unittest.TestCase):
    def test_equal(self):
        t1 = leaf_token.RawText('some text')
        t2 = leaf_token.RawText('some text')
        self.assertEqual(t1, t2)

    def test_unequal(self):
        t1 = leaf_token.RawText('some text')
        t2 = leaf_token.RawText('other text')
        self.assertNotEqual(t1, t2)

class TestLink(unittest.TestCase):
    def test_equal(self):
        t1 = leaf_token.Link('[name 1](target 1)')
        t2 = leaf_token.Link('[name 1](target 1)')
        self.assertEqual(t1, t2)

    def test_unequal(self):
        t1 = leaf_token.Link('[name 1](target 1)')
        t2 = leaf_token.Link('[name 2](target 1)')
        t3 = leaf_token.Link('[name 1](target 2)')
        self.assertNotEqual(t1, t2)
        self.assertNotEqual(t1, t3)

class TestStrong(unittest.TestCase):
    def test_raw(self):
        t = leaf_token.Strong('**some text**')
        c = leaf_token.RawText('some text')
        self.assertEqual(t.children[0], c)

class TestEmphasis(unittest.TestCase):
    def test_raw(self):
        t = leaf_token.Emphasis('*some text*')
        c = leaf_token.RawText('some text')
        self.assertEqual(t.children[0], c)

class TestInlineCode(unittest.TestCase):
    def test_raw(self):
        t = leaf_token.InlineCode('`some code`')
        c = leaf_token.RawText('some code')
        self.assertEqual(t.children[0], c)

class TestStrikethrough(unittest.TestCase):
    def test_raw(self):
        t = leaf_token.Strikethrough('~~some text~~')
        c = leaf_token.RawText('some text')
        self.assertEqual(t.children[0], c)
