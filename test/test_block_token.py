import unittest
from unittest.mock import patch
import mistletoe.block_token as block_token


class TestToken(unittest.TestCase):
    def setUp(self):
        patcher = patch('mistletoe.span_token.RawText')
        self.mock = patcher.start()
        self.addCleanup(patcher.stop)

    def _test_match(self, token_cls, lines, arg, **kwargs):
        token = next(block_token.tokenize(lines))
        self.assertIsInstance(token, token_cls)
        self._test_token(token, arg, **kwargs)

    def _test_token(self, token, arg, **kwargs):
        for attr, value in kwargs.items():
            self.assertEqual(getattr(token, attr), value)
        next(iter(token.children))
        self.mock.assert_called_with(arg)


class TestHeading(TestToken):
    def test_match_atx(self):
        lines = ['### heading 3\n']
        arg = 'heading 3'
        self._test_match(block_token.Heading, lines, arg, level=3)

    def test_match_setext(self):
        lines = ['some\n', 'heading\n', '---\n']
        arg = 'some heading'
        self._test_match(block_token.Heading, lines, arg, level=2)

    def test_children_with_enclosing_hashes(self):
        lines = ['# heading 3 #####  \n']
        arg = 'heading 3'
        self._test_match(block_token.Heading, lines, arg, level=1)


class TestQuote(unittest.TestCase):
    def test_match(self):
        with patch('mistletoe.block_token.Paragraph') as mock:
            token = next(block_token.tokenize(['> line 1\n', '> line 2\n']))
            self.assertIsInstance(token, block_token.Quote)
            next(token.children)
            mock.assert_called_with(['line 1\n', 'line 2\n'])

    def test_lazy_continuation(self):
        with patch('mistletoe.block_token.Paragraph') as mock:
            token = next(block_token.tokenize(['> line 1\n', 'line 2\n']))
            self.assertIsInstance(token, block_token.Quote)
            next(token.children)
            mock.assert_called_with(['line 1\n', 'line 2\n'])


class TestBlockCode(TestToken):
    def test_match_fenced_code(self):
        lines = ['```sh\n', 'rm dir\n', 'mkdir test\n', '```\n']
        arg = 'rm dir\nmkdir test\n'
        self._test_match(block_token.BlockCode, lines, arg, language='sh')

    def test_fence_code_lazy_continuation(self):
        lines = ['```sh\n', 'rm dir\n', '\n', 'mkdir test\n', '```\n']
        arg = 'rm dir\n\nmkdir test\n'
        self._test_match(block_token.BlockCode, lines, arg, language='sh')

    def test_hashes(self):
        lines = ['```ruby\n', '# comment\n', '```\n']
        arg = '# comment\n'
        self._test_match(block_token.BlockCode, lines, arg, language='ruby')

    def test_parse_indented_code(self):
        lines = ['    rm dir\n', '    mkdir test\n']
        arg = 'rm dir\nmkdir test\n'
        self._test_match(block_token.BlockCode, lines, arg, language='')


class TestParagraph(TestToken):
    def test_parse(self):
        lines = ['some\n', 'continuous\n', 'lines\n']
        arg = 'some continuous lines'
        self._test_match(block_token.Paragraph, lines, arg)


class TestListItem(TestToken):
    def test_children(self):
        token = block_token.ListItem(['- some text\n'])
        self._test_token(token, 'some text')

    def test_lazy_continuation(self):
        token = block_token.ListItem(['- list\n', 'content\n'])
        self._test_token(token, 'list content')

    def test_whitespace(self):
        token = block_token.ListItem(['-   text  \n'])
        self._test_token(token, 'text')

    def test_empty_item(self):
        token = block_token.ListItem(['-   \n'])
        self.assertEqual(list(token.children), [])


class TestList(TestToken):
    def setUp(self):
        patcher = patch('mistletoe.block_token.ListItem')
        self.mock = patcher.start()
        self.addCleanup(patcher.stop)

    def _test_token(self, token, call_count, **kwargs):
        for attr, value in kwargs.items():
            self.assertEqual(getattr(token, attr), value)
        self.assertEqual(self.mock.call_count, call_count)

    def test_match_unordered_list(self):
        lines = ['- item 1\n', '- item 2\n']
        self._test_match(block_token.List, lines, 2, start=None)

    def test_match_ordered_list(self):
        lines = ['1) item 1\n',
                 '2) item 2\n',
                 '    * nested item 1\n',
                 '    * nested item 2\n',
                 '3) item 3\n']
        self._test_match(block_token.List, lines, 5, start=1)

    def test_match_nested_lists(self):
        lines = ['- item 1\n',
                 '- item 2\n',
                 '    * nested item 1\n',
                 '    * nested item 2\n',
                 '- item 3\n']
        token = next(block_token.tokenize(lines))
        self._test_token(token, 5)

    def test_lazy_continuation(self):
        lines = ['* item 1\n',
                 '* item 2\n',
                 '  w/ indent\n',
                 '* item 3\n',
                 'w/o indent\n']
        token = next(block_token.tokenize(lines))
        self._test_token(token, 3)


class TestTable(unittest.TestCase):
    def test_parse_align(self):
        test_func = block_token.Table.parse_align
        self.assertEqual(test_func(':------'), None)
        self.assertEqual(test_func(':-----:'), 0)
        self.assertEqual(test_func('------:'), 1)

    def test_parse_delimiter(self):
        test_func = block_token.Table.split_delimiter
        self.assertEqual(list(test_func('| :--- | :---: | ---:|\n')),
                [':---', ':---:', '---:'])

    def test_match(self):
        lines = ['| header 1 | header 2 | header 3 |\n',
                 '| --- | --- | --- |\n',
                 '| cell 1 | cell 2 | cell 3 |\n',
                 '| more 1 | more 2 | more 3 |\n']
        arg = '| header 1 | header 2 | header 3 |\n', [None, None, None]
        with patch('mistletoe.block_token.TableRow') as mock:
            token = next(block_token.tokenize(lines))
            self.assertIsInstance(token, block_token.Table)
            self.assertEqual(token.has_header, True)
            self.assertEqual(token.column_align, [None, None, None])
            next(token.children)
            mock.assert_called_with(*arg)


class TestTableRow(unittest.TestCase):
    def test_match(self):
        with patch('mistletoe.block_token.TableCell') as mock:
            line = '| cell 1 | cell 2 |\n'
            token = block_token.TableRow(line)
            self.assertEqual(token.row_align, [None])
            next(token.children)
            mock.assert_called_with('cell 1', None)


class TestTableCell(TestToken):
    def test_match(self):
        token = block_token.TableCell('cell 2')
        self._test_token(token, 'cell 2', align=None)


class TestFootnoteBlock(TestToken):
    def setUp(self):
        patcher = patch('mistletoe.block_token.FootnoteEntry')
        self.mock = patcher.start()
        self.addCleanup(patcher.stop)

    def test_match(self):
        lines = ['[key 1]: value 1\n',
                 '[key 2]: value 2\n']
        arg = '[key 2]: value 2\n'  # the last item should be called
        self._test_match(block_token.FootnoteBlock, lines, arg)


class TestFootnoteEntry(unittest.TestCase):
    def test_match(self):
        line = '[key]: value\n'
        token = block_token.FootnoteEntry(line)
        self.assertEqual(token.key, 'key')
        self.assertEqual(token.value, 'value')


class TestDocument(unittest.TestCase):
    def test_store_footnote(self):
        lines = ['[key 1]: value 1\n',
                 '[key 2]: value 2\n']
        document = block_token.Document(lines)
        self.assertEqual(document.footnotes['key 1'], 'value 1')
        self.assertEqual(document.footnotes['key 2'], 'value 2')


class TestSeparator(unittest.TestCase):
    def test_match(self):
        token = next(block_token.tokenize(['---\n']))
        self.assertIsInstance(token, block_token.Separator)
