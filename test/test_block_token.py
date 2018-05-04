import unittest
from unittest.mock import patch, call
from mistletoe import block_token, span_token
from mistletoe.block_tokenizer import FileWrapper


class TestToken(unittest.TestCase):
    def setUp(self):
        self.addCleanup(lambda: span_token._token_types.__setitem__(-1, span_token.RawText))
        patcher = patch('mistletoe.span_token.RawText')
        self.mock = patcher.start()
        span_token._token_types[-1] = self.mock
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


class TestATXHeading(TestToken):
    def test_match(self):
        lines = ['### heading 3\n']
        arg = 'heading 3'
        self._test_match(block_token.Heading, lines, arg, level=3)

    def test_children_with_enclosing_hashes(self):
        lines = ['# heading 3 #####  \n']
        arg = 'heading 3'
        self._test_match(block_token.Heading, lines, arg, level=1)

    def test_not_heading(self):
        lines = ['####### paragraph\n']
        arg = '####### paragraph'
        self._test_match(block_token.Paragraph, lines, arg)

    def test_heading_in_paragraph(self):
        lines = ['foo\n', '# heading\n', 'bar\n']
        token1, token2, token3 = block_token.tokenize(lines)
        self.assertIsInstance(token1, block_token.Paragraph)
        self.assertIsInstance(token2, block_token.Heading)
        self.assertIsInstance(token3, block_token.Paragraph)


class TestSetextHeading(TestToken):
    def test_match(self):
        lines = ['some\n', 'heading\n', '---\n']
        arg = 'some\nheading\n'
        self._test_match(block_token.SetextHeading, lines, arg, level=2)

    def test_next(self):
        lines = ['some\n', 'heading\n', '---\n', '\n', 'foobar\n']
        tokens = block_token.tokenize(lines)
        token = next(tokens)
        self.assertIsInstance(token, block_token.SetextHeading)
        token.children
        self.mock.assert_called_with('some\nheading\n')
        token = next(tokens)
        self.assertIsInstance(token, block_token.Paragraph)
        token.children
        self.mock.assert_called_with('foobar')
        with self.assertRaises(StopIteration) as e:
            token = next(tokens)


class TestQuote(unittest.TestCase):
    def test_match(self):
        with patch('mistletoe.block_token.Paragraph') as mock:
            token = next(block_token.tokenize(['> line 1\n', '> line 2\n']))
            self.assertIsInstance(token, block_token.Quote)

    def test_lazy_continuation(self):
        with patch('mistletoe.block_token.Paragraph') as mock:
            token = next(block_token.tokenize(['> line 1\n', 'line 2\n']))
            self.assertIsInstance(token, block_token.Quote)


class TestCodeFence(TestToken):
    def test_match_fenced_code(self):
        lines = ['```sh\n', 'rm dir\n', 'mkdir test\n', '```\n']
        arg = 'rm dir\nmkdir test\n'
        self._test_match(block_token.CodeFence, lines, arg, language='sh')

    def test_match_fenced_code_with_tilda(self):
        lines = ['~~~sh\n', 'rm dir\n', 'mkdir test\n', '~~~\n']
        arg = 'rm dir\nmkdir test\n'
        self._test_match(block_token.CodeFence, lines, arg, language='sh')

    def test_mixed_code_fence(self):
        lines = ['~~~markdown\n', '```sh\n', 'some code\n', '```\n', '~~~\n']
        arg = '```sh\nsome code\n```\n'
        self._test_match(block_token.CodeFence, lines, arg, language='markdown')

    def test_fence_code_lazy_continuation(self):
        lines = ['```sh\n', 'rm dir\n', '\n', 'mkdir test\n', '```\n']
        arg = 'rm dir\n\nmkdir test\n'
        self._test_match(block_token.CodeFence, lines, arg, language='sh')

    def test_no_wrapping_newlines_code_fence(self):
        lines = ['```\n', 'hey', '```\n', 'paragraph\n']
        arg = 'hey'
        self._test_match(block_token.CodeFence, lines, arg, language='')

    def test_unclosed_code_fence(self):
        lines = ['```\n', 'hey']
        arg = 'hey'
        self._test_match(block_token.CodeFence, lines, arg, language='')


class TestBlockCode(TestToken):
    def test_parse_indented_code(self):
        lines = ['    rm dir\n', '    mkdir test\n']
        arg = 'rm dir\nmkdir test\n'
        self._test_match(block_token.BlockCode, lines, arg, language='')


class TestParagraph(TestToken):
    def test_parse(self):
        lines = ['some\n', 'continuous\n', 'lines\n']
        arg = 'some\ncontinuous\nlines'
        self._test_match(block_token.Paragraph, lines, arg)

    def test_read(self):
        lines = ['this\n', '```\n', 'is some\n', '```\n', 'code\n']
        try:
            token1, token2, token3 = block_token.tokenize(lines)
        except ValueError as e:
            raise AssertionError("Token number mismatch.") from e
        self.assertIsInstance(token1, block_token.Paragraph)
        self.assertIsInstance(token2, block_token.CodeFence)
        self.assertIsInstance(token3, block_token.Paragraph)


class TestListItem(unittest.TestCase):
    def test_parse_marker(self):
        lines = ['- foo\n',
                 '*    bar\n',
                 ' + baz\n',
                 '1. item 1\n',
                 '2) item 2\n',
                 '123456789. item x\n']
        for line in lines:
            self.assertTrue(block_token.ListItem.parse_marker(line))
        bad_lines = ['> foo\n',
                 '1.item 1\n',
                 '2| item 2\n',
                 '1234567890. item x\n']
        for line in bad_lines:
            self.assertFalse(block_token.ListItem.parse_marker(line))

    def test_read(self):
        lines = ['- foo\n',
                 'foo\n',
                 '- bar\n',
                 '\n',
                 '  bar\n',
                 ' -    baz\n',
                 '\n',
                 '      baz\n',
                 'baz\n']
        f = FileWrapper(lines)
        result = []
        while True:
            item_lines = block_token.ListItem.read(f)
            if item_lines is None:
                break
            result.append(item_lines)
        expected = [(['- foo\n', 'foo\n'], 2, '-'),
                    (['- bar\n', '\n', 'bar\n'], 2, '-'),
                    ([' -    baz\n', '\n', 'baz\n', 'baz\n'], 6, '-'),]
        self.assertEqual(result, expected)

    def test_tokenize(self):
        lines = [' -    foo\n',
                 '   bar\n',
                 '\n',
                 '          baz\n']
        token1, token2 = next(block_token.tokenize(lines)).children[0].children
        self.assertIsInstance(token1, block_token.Paragraph)
        self.assertTrue('foo\nbar' in token1)
        self.assertIsInstance(token2, block_token.BlockCode)

    def test_sublist(self):
        lines = ['- foo\n',
                 '  - bar\n']
        f = FileWrapper(lines)
        token1, token2 = block_token.ListItem(*block_token.ListItem.read(f)).children
        self.assertIsInstance(token1, block_token.Paragraph)
        self.assertIsInstance(token2, block_token.List)

    def test_tight_list(self):
        lines = ['- foo\n']
        f = FileWrapper(lines)
        list_item = block_token.ListItem(*block_token.ListItem.read(f))
        self.assertEqual(list_item.loose, False)
        token, = list_item.children
        self.assertIsInstance(token, span_token.RawText)
        self.assertEqual(token.content, 'foo')


class TestList(unittest.TestCase):
    def test_different_markers(self):
        lines = ['- foo\n',
                 '* bar\n',
                 '1. baz\n',
                 '2) spam\n']
        l1, l2, l3, l4 = block_token.tokenize(lines)
        self.assertIsInstance(l1, block_token.List)
        self.assertTrue('foo' in l1)
        self.assertIsInstance(l2, block_token.List)
        self.assertTrue('bar' in l2)
        self.assertIsInstance(l3, block_token.List)
        self.assertTrue('baz' in l3)
        self.assertIsInstance(l4, block_token.List)
        self.assertTrue('spam' in l4)

    def test_sublist(self):
        lines = ['- foo\n',
                 '  + bar\n']
        token, = block_token.tokenize(lines)
        self.assertIsInstance(token, block_token.List)


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
        with patch('mistletoe.block_token.TableRow') as mock:
            token = next(block_token.tokenize(lines))
            self.assertIsInstance(token, block_token.Table)
            self.assertTrue(hasattr(token, 'header'))
            self.assertEqual(token.column_align, [None, None, None])
            token.children
            calls = [call(line, [None, None, None]) for line in lines[:1]+lines[2:]]
            mock.assert_has_calls(calls)

    def test_easy_table(self):
        lines = ['header 1 | header 2\n',
                 '    ---: | :---\n',
                 '  cell 1 | cell 2\n']
        with patch('mistletoe.block_token.TableRow') as mock:
            token, = block_token.tokenize(lines)
            self.assertIsInstance(token, block_token.Table)
            self.assertTrue(hasattr(token, 'header'))
            self.assertEqual(token.column_align, [1, None])
            token.children
            calls = [call(line, [1, None]) for line in lines[:1] + lines[2:]]
            mock.assert_has_calls(calls)

    def test_not_easy_table(self):
        lines = ['not header 1 | not header 2\n',
                 'foo | bar\n']
        token, = block_token.tokenize(lines)
        self.assertIsInstance(token, block_token.Paragraph)


class TestTableRow(unittest.TestCase):
    def test_match(self):
        with patch('mistletoe.block_token.TableCell') as mock:
            line = '| cell 1 | cell 2 |\n'
            token = block_token.TableRow(line)
            self.assertEqual(token.row_align, [None])
            token.children
            mock.assert_has_calls([call('cell 1', None), call('cell 2', None)])

    def test_easy_table_row(self):
        with patch('mistletoe.block_token.TableCell') as mock:
            line = 'cell 1 | cell 2\n'
            token = block_token.TableRow(line)
            self.assertEqual(token.row_align, [None])
            token.children
            mock.assert_has_calls([call('cell 1', None), call('cell 2', None)])


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

    def test_auto_splitlines(self):
        lines = "some\ncontinual\nlines\n"
        document = block_token.Document(lines)
        self.assertIsInstance(document.children[0], block_token.Paragraph)
        self.assertEqual(len(document.children), 1)


class TestSeparator(unittest.TestCase):
    def test_match(self):
        def test_case(line):
            token = next(block_token.tokenize([line]))
            self.assertIsInstance(token, block_token.Separator)
        cases = ['---\n', '* * *\n', '_    _    _\n']
        for case in cases:
            test_case(case)


class TestContains(unittest.TestCase):
    def test_contains(self):
        lines = ['# heading\n', '\n', 'paragraph\n', 'with\n', '`code`\n']
        token = block_token.Document(lines)
        self.assertTrue('heading' in token)
        self.assertTrue('code' in token)
        self.assertFalse('foo' in token)
