import unittest
import test.test_core.helpers as helpers
import core.leaf_token as leaf_token
import core.block_token as block_token

class TestHeading(unittest.TestCase):
    def test_left_hashes(self):
        t = block_token.Heading([ '### heading 3\n' ])
        c = leaf_token.RawText('heading 3')
        helpers.check_equal(self, list(t.children)[0], c)

    def test_enclosing_hashes(self):
        t = block_token.Heading([ '### heading 3 #########  \n' ])
        c = leaf_token.RawText('heading 3')
        helpers.check_equal(self, list(t.children)[0], c)

    def test_setext_heading(self):
        t = block_token.Heading(['some\n', 'heading 2\n', '---\n'])
        c = leaf_token.RawText('some heading 2')
        helpers.check_equal(self, list(t.children)[0], c)

    def test_bold(self):
        t = block_token.Heading([ '## **heading** 2\n' ])
        c0 = leaf_token.Strong('heading')
        c1 = leaf_token.RawText(' 2')
        l = list(t.children)
        helpers.check_equal(self, l[0], c0)
        helpers.check_equal(self, l[1], c1)

class TestQuote(unittest.TestCase):
    def test_paragraph(self):
        t = block_token.Quote(['> line 1\n', '> line 2\n'])
        c = block_token.Paragraph(['line 1\n', 'line 2\n'])
        helpers.check_equal(self, list(t.children)[0], c)

    def test_heading(self):
        t = block_token.Quote(['> # heading 1\n', '> \n', '> line 1\n'])
        c0 = block_token.Heading([ '# heading 1\n' ])
        c1 = block_token.Paragraph(['line 1\n'])
        l = list(t.children)
        helpers.check_equal(self, l[0], c0)
        helpers.check_equal(self, l[1], c1)

class TestBlockCode(unittest.TestCase):
    def test_fenced_code(self):
        l = ['```sh\n', 'rm dir\n', 'mkdir test\n', '```\n']
        t = block_token.Document(l)
        c = block_token.BlockCode(l)
        helpers.check_equal(self, list(t.children)[0], c)

    def test_indented_code(self):
        l1 = ['    rm dir\n', '    mkdir test\n']
        l2 = ['```\n', 'rm dir\n', 'mkdir test\n', '```\n']
        t = block_token.Document(l1)
        c = block_token.BlockCode(l2)
        helpers.check_equal(self, list(t.children)[0], c)

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
        helpers.check_equal(self, list(t.children)[0], c)

    def test_inner(self):
        lines = ['some\n', '*continuous*\n', '**lines**\n']
        t = block_token.Paragraph(lines)
        c0 = leaf_token.RawText('some ')
        c1 = leaf_token.Emphasis('continuous')
        c2 = leaf_token.RawText(' ')
        c3 = leaf_token.Strong('lines')
        l = list(t.children)
        helpers.check_equal(self, l[0], c0)
        helpers.check_equal(self, l[1], c1)
        helpers.check_equal(self, l[2], c2)
        helpers.check_equal(self, l[3], c3)

class TestListItem(unittest.TestCase):
    def test_raw(self):
        t = block_token.ListItem('- some text\n')
        c = leaf_token.RawText('some text')
        helpers.check_equal(self, list(t.children)[0], c)

    def test_inline_code(self):
        t = block_token.ListItem('    - some `code`\n')
        c0 = leaf_token.RawText('some ')
        c1 = leaf_token.InlineCode('code')
        l = list(t.children)
        helpers.check_equal(self, l[0], c0)
        helpers.check_equal(self, l[1], c1)

class TestList(unittest.TestCase):
    def test_nested_list(self):
        lines = ['- item 1\n',
                 '- item 2\n',
                 '    * nested item 1\n',
                 '    * nested item 2\n',
                 '- item 3\n']
        t = block_token.List(lines)
        sublist = ['- nested item 1\n', '- nested item 2\n']
        c0 = block_token.ListItem(lines[0])
        c1 = block_token.ListItem(lines[1])
        c2 = block_token.List([ line.strip() for line in sublist ])
        c3 = block_token.ListItem(lines[4])
        l = list(t.children)
        helpers.check_equal(self, l[0], c0)
        helpers.check_equal(self, l[1], c1)
        helpers.check_equal(self, l[2], c2)
        helpers.check_equal(self, l[3], c3)

    def test_not_list(self):
        lines = ['-not a list\n',
                 '\n',
                 '- a list\n',
                 '- more item\n']
        t = block_token.Document(lines)
        c0 = block_token.Paragraph([ lines[0] ])
        c1 = block_token.List(lines[2:])
        l = list(t.children)
        helpers.check_equal(self, l[0], c0)
        helpers.check_equal(self, l[1], c1)

class TestSeparator(unittest.TestCase):
    def test_equal(self):
        t1 = block_token.Separator('---\n')
        t2 = block_token.Separator('---\n')
        helpers.check_equal(self, t1, t2)
