import unittest
import test.test_core.helpers as helpers
import core.leaf_token as leaf_token
import core.block_token as block_token

class TestHeading(unittest.TestCase):
    def test_raw(self):
        t = block_token.Heading('### heading 3\n')
        c = leaf_token.RawText('heading 3')
        helpers.check_equal(self, t.children[0], c)

    def test_bold(self):
        t = block_token.Heading('## **heading** 2\n')
        c0 = leaf_token.Strong('**heading**')
        c1 = leaf_token.RawText(' 2')
        helpers.check_equal(self, t.children[0], c0)
        helpers.check_equal(self, t.children[1], c1)

class TestQuote(unittest.TestCase):
    def test_paragraph(self):
        t = block_token.Quote(['> line 1\n', '> line 2\n'])
        c = block_token.Paragraph(['line 1\n', 'line 2\n'])
        helpers.check_equal(self, t.children[0], c)

    def test_heading(self):
        t = block_token.Quote(['> # heading 1\n', '> line 1\n'])
        c0 = block_token.Heading('# heading 1\n')
        c1 = block_token.Paragraph(['line 1\n'])
        helpers.check_equal(self, t.children[0], c0)
        helpers.check_equal(self, t.children[1], c1)

class TestBlockCode(unittest.TestCase):
    def test_equal(self):
        l1 = ['```sh\n', 'rm dir\n', 'mkdir test\n', '```\n']
        l2 = ['```sh\n', 'rm dir\n', 'mkdir test\n', '```\n']
        t1 = block_token.BlockCode(l1)
        t2 = block_token.BlockCode(l2)
        helpers.check_equal(self, t1, t2)

    def test_unequal(self):
        l1 = ['```sh\n', 'rm dir\n', 'mkdir test\n', '```\n']
        l2 = ['```\n', 'rm dir\n', 'mkdir test\n', '```\n']
        t1 = block_token.BlockCode(l1)
        t2 = block_token.BlockCode(l2)
        helpers.check_unequal(self, t1, t2)

class TestParagraph(unittest.TestCase):
    def test_raw(self):
        l = ['some\n', 'continuous\n', 'lines\n']
        t = block_token.Paragraph(l)
        c = leaf_token.RawText('some continuous lines')
        helpers.check_equal(self, t.children[0], c)

    def test_italic(self):
        l = ['some\n', '*continuous*\n', 'lines\n']
        t = block_token.Paragraph(l)
        c0 = leaf_token.RawText('some ')
        c1 = leaf_token.Emphasis('*continuous*')
        c2 = leaf_token.RawText(' lines')
        helpers.check_equal(self, t.children[0], c0)
        helpers.check_equal(self, t.children[1], c1)
        helpers.check_equal(self, t.children[2], c2)

class TestListItem(unittest.TestCase):
    def test_raw(self):
        t = block_token.ListItem('- some text\n')
        c = leaf_token.RawText('some text')
        helpers.check_equal(self, t.children[0], c)

    def test_inline_code(self):
        t = block_token.ListItem('    - some `code`\n')
        c0 = leaf_token.RawText('some ')
        c1 = leaf_token.InlineCode('`code`')
        helpers.check_equal(self, t.children[0], c0)
        helpers.check_equal(self, t.children[1], c1)

class TestList(unittest.TestCase):
    def test_children(self):
        lines = ['- item 1\n',
                 '- item 2\n',
                 '    - nested item 1\n',
                 '    - nested item 2\n',
                 '- item 3\n']
        t = block_token.List(lines)
        sublist = ['- nested item 1\n', '- nested item 2\n']
        c0 = block_token.ListItem(lines[0])
        c2 = block_token.List([ line.strip() for line in sublist ])
        helpers.check_equal(self, t.children[0], c0)
        helpers.check_equal(self, t.children[2], c2)

class TestSeparator(unittest.TestCase):
    def test_equal(self):
        t1 = block_token.Separator('---\n')
        t2 = block_token.Separator('* * *\n')
        helpers.check_equal(self, t1, t2)
