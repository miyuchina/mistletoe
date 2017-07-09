import unittest
import core.leaf_token as leaf_token
import core.block_token as block_token

class TestHeading(unittest.TestCase):
    def test_raw(self):
        t = block_token.Heading('### heading 3\n')
        c = leaf_token.RawText('heading 3')
        self.assertEqual(t.children[0], c)

    def test_bold(self):
        t = block_token.Heading('## **heading** 2\n')
        c0 = leaf_token.Bold('**heading**')
        c1 = leaf_token.RawText(' 2')
        self.assertEqual(t.children[0], c0)
        self.assertEqual(t.children[1], c1)

class TestQuote(unittest.TestCase):
    def test_paragraph(self):
        t = block_token.Quote(['> line 1\n', '> line 2\n'])
        c = block_token.Paragraph(['line 1\n', 'line 2\n'])
        self.assertEqual(t.children[0], c)

    def test_heading(self):
        t = block_token.Quote(['> # heading 1\n', '> line 1\n'])
        c0 = block_token.Heading('# heading 1\n')
        c1 = block_token.Paragraph(['line 1\n'])

class TestBlockCode(unittest.TestCase):
    def test_equal(self):
        l = ['```sh\n', 'rm dir\n', 'mkdir test\n', '```\n']
        t1 = block_token.BlockCode(l)
        t2 = block_token.BlockCode(l)
        self.assertEqual(t1, t2)

    def test_unequal(self):
        l1 = ['```sh\n', 'rm dir\n', 'mkdir test\n', '```\n']
        l2 = ['```\n', 'rm dir\n', 'mkdir test\n', '```\n']
        t1 = block_token.BlockCode(l1)
        t2 = block_token.BlockCode(l2)
        self.assertNotEqual(t1, t2)

class TestParagraph(unittest.TestCase):
    def test_raw(self):
        l = ['some\n', 'continuous\n', 'lines\n']
        t = block_token.Paragraph(l)
        c = leaf_token.RawText('some continuous lines')
        self.assertEqual(t.children[0], c)

    def test_italic(self):
        l = ['some\n', '*continuous*\n', 'lines\n']
        t = block_token.Paragraph(l)
        c0 = leaf_token.RawText('some ')
        c1 = leaf_token.Italic('*continuous*')
        c2 = leaf_token.RawText(' lines')
        self.assertEqual(t.children[0], c0)
        self.assertEqual(t.children[1], c1)
        self.assertEqual(t.children[2], c2)

class TestListItem(unittest.TestCase):
    def test_raw(self):
        t = block_token.ListItem('- some text\n')
        c = leaf_token.RawText('some text')
        self.assertEqual(t.children[0], c)

    def test_inline_code(self):
        t = block_token.ListItem('    - some `code`\n')
        c0 = leaf_token.RawText('some ')
        c1 = leaf_token.InlineCode('`code`')
        self.assertEqual(t.children[0], c0)
        self.assertEqual(t.children[1], c1)

@unittest.skip('pending')
class TestList(unittest.TestCase):
    def test(self):
        pass

class TestSeparator(unittest.TestCase):
    def test_equal(self):
        t1 = block_token.Separator('---\n')
        t2 = block_token.Separator('* * *\n')
        self.assertEqual(t1, t2)

    def test_unequal(self):
        t1 = block_token.Separator('---\n')
        t2 = block_token.Heading('#### heading 4\n')
        self.assertNotEqual(t1, t2)
