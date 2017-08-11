import unittest
import test.helpers as helpers
import mistletoe.span_token as span_token
import mistletoe.block_token as block_token

class TestHeading(unittest.TestCase):
    def test_left_hashes(self):
        t = block_token.Heading([ '### heading 3\n' ])
        c = span_token.RawText('heading 3')
        helpers.check_equal(self, list(t.children)[0], c)

    def test_enclosing_hashes(self):
        t = block_token.Heading([ '### heading 3 #########  \n' ])
        c = span_token.RawText('heading 3')
        helpers.check_equal(self, list(t.children)[0], c)

    def test_setext_heading(self):
        t = block_token.Heading(['some\n', 'heading 2\n', '---\n'])
        c = span_token.RawText('some heading 2')
        helpers.check_equal(self, list(t.children)[0], c)

    def test_bold(self):
        t = block_token.Heading([ '## **heading** 2\n' ])
        c0 = span_token.Strong('heading')
        c1 = span_token.RawText(' 2')
        l = list(t.children)
        helpers.check_equal(self, l[0], c0)
        helpers.check_equal(self, l[1], c1)

class TestQuote(unittest.TestCase):
    def test_paragraph(self):
        t = block_token.Quote(['> line 1\n', '> line 2\n'])
        c = block_token.Paragraph(['line 1\n', 'line 2\n'])
        helpers.check_equal(self, list(t.children)[0], c)

    def test_only_first_leader(self):
        t = block_token.Quote(['> line 1\n', 'line 2\n'])
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
        l1 = ['```sh\n', 'rm dir\n', '\n', 'mkdir test\n', '```\n']
        # space is added at l2[2] to escape tokenizing by newlines
        l2 = ['```sh\n', 'rm dir\n', ' \n', 'mkdir test\n', '```\n']
        t = block_token.Document(l1)
        c = block_token.BlockCode(l2)
        helpers.check_equal(self, list(t.children)[0], c)

    def test_hash_in_code(self):
        l = ['```python\n', '# comment\n', '```\n']
        t = block_token.Document(l)
        c = span_token.RawText('# comment\n')
        helpers.check_equal(self, list(list(t.children)[0].children)[0], c)

    def test_indented_code(self):
        l1 = ['    rm dir\n', '    mkdir test\n']
        l2 = ['```\n', 'rm dir\n', 'mkdir test\n', '```\n']
        t = block_token.Document(l1)
        c = block_token.BlockCode(l2)
        helpers.check_equal(self, list(t.children)[0], c)

class TestParagraph(unittest.TestCase):
    def test_raw(self):
        l = ['some\n', 'continuous\n', 'lines\n']
        t = block_token.Paragraph(l)
        c = span_token.RawText('some continuous lines')
        helpers.check_equal(self, list(t.children)[0], c)

    def test_inner(self):
        lines = ['some\n', '*continuous*\n', '**lines**\n']
        t = block_token.Paragraph(lines)
        c0 = span_token.RawText('some ')
        c1 = span_token.Emphasis('continuous')
        c2 = span_token.RawText(' ')
        c3 = span_token.Strong('lines')
        l = list(t.children)
        helpers.check_equal(self, l[0], c0)
        helpers.check_equal(self, l[1], c1)
        helpers.check_equal(self, l[2], c2)
        helpers.check_equal(self, l[3], c3)

class TestListItem(unittest.TestCase):
    def test_raw(self):
        t = block_token.ListItem(['- some text\n'])
        c = span_token.RawText('some text')
        helpers.check_equal(self, list(t.children)[0], c)

    def test_inline_code(self):
        t = block_token.ListItem(['    - some `code`\n'])
        c0 = span_token.RawText('some ')
        c1 = span_token.InlineCode('code')
        l = list(t.children)
        helpers.check_equal(self, l[0], c0)
        helpers.check_equal(self, l[1], c1)

    def test_whitespace(self):
        t = block_token.ListItem(['-    list\n', '   content\n'])
        c = span_token.RawText('list content')
        helpers.check_equal(self, list(t.children)[0], c)

class TestList(unittest.TestCase):
    def test_is_list(self):
        lines = ['-not a list\n',
                 '\n',
                 '- a list\n',
                 '-continued\n']
        t = block_token.Document(lines)
        c0 = block_token.Paragraph([ lines[0] ])
        c1 = block_token.List(lines[2:])
        l = list(t.children)
        helpers.check_equal(self, l[0], c0)
        helpers.check_equal(self, l[1], c1)

    def test_tokenize_unordered_list(self):
        lines = ['- item 1\n',
                 '- item 2\n',
                 '    * nested item 1\n',
                 '    * nested item 2\n',
                 '- item 3\n']
        t = block_token.Document(lines)
        c = block_token.List(lines)
        helpers.check_equal(self, list(t.children)[0], c)

    def test_tokenize_ordered_list(self):
        lines = ['1) item 1\n',
                 '2) item 2\n',
                 '    * nested item 1\n',
                 '    * nested item 2\n',
                 '3) item 3\n']
        t = block_token.Document(lines)
        c = block_token.List(lines)
        helpers.check_equal(self, list(t.children)[0], c)

    def test_nested_list(self):
        lines = ['- item 1\n',
                 '- item 2\n',
                 '    * nested item 1\n',
                 '    * nested item 2\n',
                 '- item 3\n']
        t = block_token.List(lines)
        sublist = ['- nested item 1\n', '- nested item 2\n']
        c0 = block_token.ListItem(lines[0:1])
        c1 = block_token.ListItem(lines[1:2])
        c2 = block_token.List([ line.strip() for line in sublist ])
        c3 = block_token.ListItem(lines[4:5])
        l = list(t.children)
        helpers.check_equal(self, l[0], c0)
        helpers.check_equal(self, l[1], c1)
        helpers.check_equal(self, l[2], c2)
        helpers.check_equal(self, l[3], c3)

    def test_lazy_list_match(self):
        lines = ['* item 1\n',
                 '*    item 2\n',
                 '* item 3\n',
                 '  continued with indent\n',
                 '* item 4\n',
                 'with lazy continuation\n',
                 '    + nested item 1\n',
                 '    continued\n',
                 '- item 5\n'
                 'cont\'d\n']
        t = block_token.List(lines)
        c0 = block_token.ListItem(lines[0:1])
        c1 = block_token.ListItem(lines[1:2])
        c2 = block_token.ListItem(lines[2:4])
        c3 = block_token.ListItem(lines[4:6])
        c4 = block_token.List([line.strip() for line in lines[6:8]])
        c5 = block_token.ListItem(lines[8:])
        l = list(t.children)
        helpers.check_equal(self, l[0], c0)
        helpers.check_equal(self, l[1], c1)
        helpers.check_equal(self, l[2], c2)
        helpers.check_equal(self, l[3], c3)
        helpers.check_equal(self, l[4], c4)
        helpers.check_equal(self, l[5], c5)

class TestTable(unittest.TestCase):
    def test_row(self):
        lines = ['| header 1 | header 2 | header 3 |\n',
                 '| --- | --- | --- |\n',
                 '| cell 1 | cell 2 | cell 3 |\n',
                 '| more 1 | more 2 | more 3 |\n']
        lines_c = ['| header 1 | header 2 | header 3 |\n',
                   '| cell 1 | cell 2 | cell 3 |\n',
                   '| more 1 | more 2 | more 3 |\n']
        t = block_token.Table(lines)
        c0 = block_token.TableRow(lines_c[0])
        c1 = block_token.TableRow(lines_c[1])
        c2 = block_token.TableRow(lines_c[2])
        l = list(t.children)
        helpers.check_equal(self, l[0], c0)
        helpers.check_equal(self, l[1], c1)
        helpers.check_equal(self, l[2], c2)

class TestTableRow(unittest.TestCase):
    def test_cell(self):
        t = block_token.TableRow('| **cell** 1 | cell 2 |\n')
        c0 = block_token.TableCell('**cell** 1')
        c1 = block_token.TableCell('cell 2')
        l = list(t.children)
        helpers.check_equal(self, l[0], c0)
        helpers.check_equal(self, l[1], c1)

class TestFootnoteBlock(unittest.TestCase):
    def test_footnote_block(self):
        lines = ['[key 1]: value 1\n',
                 '[key 2]: value 2\n']
        t = block_token.FootnoteBlock(lines)
        c0 = block_token.FootnoteEntry('[key 1]: value 1\n')
        c1 = block_token.FootnoteEntry('[key 2]: value 2\n')
        l = list(t.children)
        helpers.check_equal(self, l[0], c0)
        helpers.check_equal(self, l[1], c1)

    def test_match(self):
        lines = ['[key 1]: value 1\n',
                 '[key 2]: value 2\n']
        t = block_token.Document(lines)
        list(t.children)  # kick off generator
        c = block_token.FootnoteBlock(lines)
        d = {entry.key: entry.value for entry in c.children}
        self.assertEqual(t.footnotes, d)

class TestSeparator(unittest.TestCase):
    def test_equal(self):
        t1 = block_token.Separator('---\n')
        t2 = block_token.Separator('---\n')
        helpers.check_equal(self, t1, t2)
