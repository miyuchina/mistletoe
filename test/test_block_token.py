import unittest
from unittest.mock import call, patch

from parameterized import parameterized

from mistletoe import block_token, block_tokenizer, span_token


class TestToken(unittest.TestCase):
    def setUp(self):
        self.addCleanup(lambda: span_token._token_types.__setitem__(-1, span_token.RawText))
        patcher = patch('mistletoe.span_token.RawText')
        self.mock = patcher.start()
        span_token._token_types[-1] = self.mock
        self.addCleanup(patcher.stop)

    def _test_match(self, token_cls, lines, arg, **kwargs):
        token = next(iter(block_token.tokenize(lines)))
        self.assertIsInstance(token, token_cls)
        self._test_token(token, arg, **kwargs)

    def _test_token(self, token, arg, **kwargs):
        for attr, value in kwargs.items():
            self.assertEqual(getattr(token, attr), value)
        self.mock.assert_any_call(arg)


class TestAtxHeading(TestToken):
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
        lines = ['some heading\n', '---\n']
        arg = 'some heading'
        self._test_match(block_token.SetextHeading, lines, arg, level=2)

    def test_next(self):
        lines = ['some\n', 'heading\n', '---\n', '\n', 'foobar\n']
        tokens = iter(block_token.tokenize(lines))
        self.assertIsInstance(next(tokens), block_token.SetextHeading)
        self.assertIsInstance(next(tokens), block_token.Paragraph)
        self.mock.assert_has_calls([call('some'), call('heading'), call('foobar')])
        with self.assertRaises(StopIteration):
            next(tokens)


class TestQuote(unittest.TestCase):
    def test_match(self):
        with patch('mistletoe.block_token.Paragraph'):
            token = next(iter(block_token.tokenize(['> line 1\n', '> line 2\n'])))
            self.assertIsInstance(token, block_token.Quote)

    def test_lazy_continuation(self):
        with patch('mistletoe.block_token.Paragraph'):
            token = next(iter(block_token.tokenize(['> line 1\n', 'line 2\n'])))
            self.assertIsInstance(token, block_token.Quote)


class TestCodeFence(TestToken):
    def test_match_fenced_code(self):
        lines = ['```sh\n', 'rm dir\n', 'mkdir test\n', '```\n']
        arg = 'rm dir\nmkdir test\n'
        self._test_match(block_token.CodeFence, lines, arg, language='sh')

    def test_match_fenced_code_with_tilde(self):
        lines = ['~~~sh\n', 'rm dir\n', 'mkdir test\n', '~~~\n']
        arg = 'rm dir\nmkdir test\n'
        self._test_match(block_token.CodeFence, lines, arg, language='sh')

    def test_not_match_fenced_code_when_only_inline_code(self):
        lines = ['`~` is called tilde']
        token = next(iter(block_token.tokenize(lines)))
        self.assertIsInstance(token, block_token.Paragraph)
        token1 = token.children[0]
        self.assertIsInstance(token1, span_token.InlineCode)
        self.mock.assert_has_calls([call('~'), call(' is called tilde')])

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

    def test_code_fence_with_backticks_and_tildes_in_the_info_string(self):
        lines = ['~~~ aa ``` ~~~\n', 'foo\n', '~~~\n']
        arg = 'foo\n'
        self._test_match(block_token.CodeFence, lines, arg, language='aa')


class TestBlockCode(TestToken):
    def test_parse_indented_code(self):
        lines = ['    rm dir\n', '    mkdir test\n']
        arg = 'rm dir\nmkdir test\n'
        self._test_match(block_token.BlockCode, lines, arg, language='')

    def test_parse_indented_code_with_blank_lines(self):
        lines = ['    chunk1\n', '\n', '    chunk2\n', '  \n', ' \n', ' \n', '    chunk3\n']
        arg = 'chunk1\n\nchunk2\n\n\n\nchunk3\n'
        self._test_match(block_token.BlockCode, lines, arg, language='')


class TestParagraph(TestToken):
    def setUp(self):
        super().setUp()
        block_token.add_token(block_token.HtmlBlock)
        self.addCleanup(block_token.reset_tokens)

    def test_parse(self):
        lines = ['some\n', 'continuous\n', 'lines\n']
        arg = 'some'
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

    def test_parse_interrupting_block_tokens(self):
        interrupting_blocks = [
            '***\n',  # thematic break
            '## atx\n',  # ATX heading
            '<div>\n',  # HTML block type 6
            '> block quote\n',
            '1. list\n',
            '``` fenced code block\n',
            ('| table |\n', '| ----- |\n', '| row   |\n'),
        ]
        for block in interrupting_blocks:
            lines = ['Paragraph 1\n', *block]
        try:
            token1, token2 = block_token.tokenize(lines)
        except ValueError as e:
            raise AssertionError("Token number mismatch. Lines: '{}'".format(lines)) from e
        self.assertIsInstance(token1, block_token.Paragraph)
        self.assertNotIsInstance(token2, block_token.Paragraph)

    def test_parse_non_interrupting_block_tokens(self):
        lines = [
            'Paragraph 1\n',
            '2. list\n',  # list doesn't start from 1
            '    indented text\n',  # code block
            '<custom>\n',  # HTML block type 7
            '\n',
            'Paragraph 2\n'
        ]
        try:
            token1, token2 = block_token.tokenize(lines)
        except ValueError as e:
            raise AssertionError("Token number mismatch.") from e
        self.assertIsInstance(token1, block_token.Paragraph)
        self.assertIsInstance(token2, block_token.Paragraph)

    def test_parse_setext_heading(self):
        lines = [
            'Two line\n',
            'heading\n',
            '---\n'
        ]
        try:
            token1, = block_token.tokenize(lines)
        except ValueError as e:
            raise AssertionError("Token number mismatch.") from e
        self.assertIsInstance(token1, block_token.SetextHeading)


class TestListItem(unittest.TestCase):
    def test_parse_marker(self):
        lines = ['- foo\n',
                 '   *    bar\n',
                 ' + baz\n',
                 '1. item 1\n',
                 '2) item 2\n',
                 '123456789. item x\n',
                 '*\n']
        for line in lines:
            self.assertTrue(block_token.ListItem.parse_marker(line))
        bad_lines = ['> foo\n',
                     '1item 1\n',
                     '2| item 2\n',
                     '1234567890. item x\n',
                     '    * too many spaces\n']
        for line in bad_lines:
            self.assertFalse(block_token.ListItem.parse_marker(line))

    def test_tokenize(self):
        lines = [' -    foo\n',
                 '   bar\n',
                 '\n',
                 '          baz\n']
        token1, token2 = next(iter(block_token.tokenize(lines))).children[0].children
        self.assertIsInstance(token1, block_token.Paragraph)
        self.assertTrue('foo' in token1)
        self.assertIsInstance(token2, block_token.BlockCode)

    def test_sublist(self):
        lines = ['- foo\n',
                 '  - bar\n']
        token1, token2 = block_token.tokenize(lines)[0].children[0].children
        self.assertIsInstance(token1, block_token.Paragraph)
        self.assertIsInstance(token2, block_token.List)

    def test_deep_list(self):
        lines = ['- foo\n',
                 '  - bar\n',
                 '    - baz\n']
        ptoken, ltoken = block_token.tokenize(lines)[0].children[0].children
        self.assertIsInstance(ptoken, block_token.Paragraph)
        self.assertIsInstance(ltoken, block_token.List)
        self.assertTrue('foo' in ptoken)
        ptoken, ltoken = ltoken.children[0].children
        self.assertIsInstance(ptoken, block_token.Paragraph)
        self.assertTrue('bar' in ptoken)
        self.assertIsInstance(ltoken, block_token.List)
        self.assertTrue('baz' in ltoken)

    def test_loose_list(self):
        lines = ['- foo\n',
                 '  ~~~\n',
                 '  bar\n',
                 '  \n',
                 '  baz\n'
                 '  ~~~\n']
        list_item = block_token.tokenize(lines)[0].children[0]
        self.assertEqual(list_item.loose, False)

    def test_tight_list(self):
        lines = ['- foo\n',
                 '\n',
                 '# bar\n']
        list_item = block_token.tokenize(lines)[0].children[0]
        self.assertEqual(list_item.loose, False)

    def test_tabbed_list_items(self):
        # according to the CommonMark spec:
        # in contexts where spaces help to define block structure, tabs behave as if they
        # were replaced by spaces with a tab stop of 4 characters.
        lines = ['title\n',
                 '*\ttabbed item long line\n',
                 '\n',  # break lazy continuation
                 '    continuation 1\n',
                 '*   second list item\n',
                 '\n',  # break lazy continuation
                 '\tcontinuation 2\n']
        tokens = block_token.tokenize(lines)
        self.assertEqual(len(tokens), 2)
        self.assertIsInstance(tokens[0], block_token.Paragraph)
        self.assertIsInstance(tokens[1], block_token.List)
        self.assertTrue('tabbed item long line' in tokens[1].children[0])
        self.assertTrue('continuation 1' in tokens[1].children[0])
        self.assertTrue('second list item' in tokens[1].children[1])
        self.assertTrue('continuation 2' in tokens[1].children[1])

    def test_list_items_starting_with_blank_line(self):
        lines = ['-\n',
                 '  foo\n',
                 '-\n',
                 '  ```\n',
                 '  bar\n',
                 '  ```\n',
                 '-\n',
                 '      baz\n']
        tokens = block_token.tokenize(lines)
        self.assertEqual(len(tokens), 1)
        self.assertIsInstance(tokens[0], block_token.List)
        self.assertIsInstance(tokens[0].children[0].children[0], block_token.Paragraph)
        self.assertIsInstance(tokens[0].children[1].children[0], block_token.CodeFence)
        self.assertIsInstance(tokens[0].children[2].children[0], block_token.BlockCode)
        self.assertTrue('foo' in tokens[0].children[0].children[0])
        self.assertEqual('bar\n', tokens[0].children[1].children[0].children[0].content)
        self.assertEqual('baz\n', tokens[0].children[2].children[0].children[0].content)

    def test_a_list_item_may_begin_with_at_most_one_blank_line(self):
        lines = ['-\n',
                 '\n',
                 '  foo\n']
        tokens = block_token.tokenize(lines)
        self.assertEqual(len(tokens), 2)
        self.assertIsInstance(tokens[0], block_token.List)
        self.assertIsInstance(tokens[1], block_token.Paragraph)
        self.assertTrue('foo' in tokens[1].children[0])

    def test_empty_list_item_in_the_middle(self):
        lines = ['* a\n',
                 '*\n',
                 '\n',
                 '* c\n']
        tokens = block_token.tokenize(lines)
        self.assertEqual(len(tokens), 1)
        self.assertIsInstance(tokens[0], block_token.List)
        self.assertEqual(len(tokens[0].children), 3)
        self.assertTrue(tokens[0].loose)

    def test_list_with_code_block(self):
        lines = ['1.      indented code\n',
                 '\n',
                 '   paragraph\n',
                 '\n',
                 '       more code\n']
        tokens = block_token.tokenize(lines)
        self.assertEqual(len(tokens), 1)
        self.assertIsInstance(tokens[0], block_token.List)
        self.assertEqual(len(tokens[0].children), 1)
        self.assertIsInstance(tokens[0].children[0].children[0], block_token.BlockCode)
        self.assertEqual(' indented code\n', tokens[0].children[0].children[0].children[0].content)
        self.assertIsInstance(tokens[0].children[0].children[1], block_token.Paragraph)
        self.assertIsInstance(tokens[0].children[0].children[2], block_token.BlockCode)


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
        def test_func(s):
            return block_token.Table.split_delimiter(s)
        self.assertEqual(list(test_func('|-| :--- | :---: | ---:|\n')),
                ['-', ':---', ':---:', '---:'])

    @parameterized.expand([
        ('| --- | --- | --- |\n'),
        ('| - | - | - |\n'),
        ('|-|-|-- \n'),
    ])
    def test_match(self, delimiter_line):
        lines = ['| header 1 | header 2 | header 3 |\n',
                delimiter_line,
                 '| cell 1 | cell 2 | cell 3 |\n',
                 '| more 1 | more 2 | more 3 |\n']
        with patch('mistletoe.block_token.TableRow') as mock:
            token, = block_token.tokenize(lines)
            self.assertIsInstance(token, block_token.Table)
            self.assertTrue(hasattr(token, 'header'))
            self.assertEqual(token.column_align, [None, None, None])
            token.children
            calls = [call(line, [None, None, None], line_number) for line_number, line in enumerate(lines, start=1) if line_number != 2]
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
            calls = [call(line, [1, None], line_number) for line_number, line in enumerate(lines, start=1) if line_number != 2]
            mock.assert_has_calls(calls)

    def test_not_easy_table(self):
        lines = ['not header 1 | not header 2\n',
                 'foo | bar\n']
        token, = block_token.tokenize(lines)
        self.assertIsInstance(token, block_token.Paragraph)

    def test_interrupt_paragraph_option(self):
        lines = [
            'Paragraph 1\n',
            '| table |\n',
            '| ----- |\n',
            '| row   |\n',
        ]
        try:
            block_token.Table.interrupt_paragraph = False
            token, = block_token.tokenize(lines)
        except ValueError as e:
            raise AssertionError("Token number mismatch.") from e
        finally:
            block_token.Table.interrupt_paragraph = True
        self.assertIsInstance(token, block_token.Paragraph)


class TestTableRow(unittest.TestCase):
    def test_match(self):
        with patch('mistletoe.block_token.TableCell') as mock:
            line = '| cell 1 | cell 2 |\n'
            token = block_token.TableRow(line, line_number=10)
            self.assertEqual(token.row_align, [None])
            mock.assert_has_calls([call('cell 1', None, 10), call('cell 2', None, 10)])

    def test_easy_table_row(self):
        with patch('mistletoe.block_token.TableCell') as mock:
            line = 'cell 1 | cell 2\n'
            token = block_token.TableRow(line, line_number=10)
            self.assertEqual(token.row_align, [None])
            mock.assert_has_calls([call('cell 1', None, 10), call('cell 2', None, 10)])

    def test_short_row(self):
        with patch('mistletoe.block_token.TableCell') as mock:
            line = '| cell 1 |\n'
            token = block_token.TableRow(line, [None, None], 10)
            self.assertEqual(token.row_align, [None, None])
            mock.assert_has_calls([call('cell 1', None, 10), call('', None, 10)])

    def test_escaped_pipe_in_cell(self):
        with patch('mistletoe.block_token.TableCell') as mock:
            line = '| pipe: `\\|` | cell 2\n'
            token = block_token.TableRow(line, line_number=10, row_align=[None, None])
            self.assertEqual(token.row_align, [None, None])
            mock.assert_has_calls([call('pipe: `|`', None, 10), call('cell 2', None, 10)])

    @unittest.skip('Even GitHub fails in here, workaround: always put a space before `|`')
    def test_not_really_escaped_pipe_in_cell(self):
        with patch('mistletoe.block_token.TableCell') as mock:
            line = '|ending with a \\\\|cell 2\n'
            token = block_token.TableRow(line, [None, None], 10)
            self.assertEqual(token.row_align, [None, None])
            mock.assert_has_calls([call('ending with a \\\\', None, 10), call('cell 2', None, 10)])


class TestTableCell(TestToken):
    def test_match(self):
        token = block_token.TableCell('cell 2', line_number=13)
        self._test_token(token, 'cell 2', line_number=13, align=None)


class TestFootnote(unittest.TestCase):
    def test_parse_simple(self):
        lines = ['[key 1]: value1\n',
                 '[key 2]: value2\n']
        token = block_token.Document(lines)
        self.assertEqual(token.footnotes, {"key 1": ("value1", ""),
                                           "key 2": ("value2", "")})

    def test_parse_with_title(self):
        lines = ['[key 1]: value1 "title1"\n',
                 '[key 2]: value2\n',
                 '"title2"\n']
        token = block_token.Document(lines)
        self.assertEqual(token.footnotes, {"key 1": ("value1", "title1"),
                                           "key 2": ("value2", "title2")})

    def test_parse_with_space_in_every_part(self):
        lines = ['[Foo bar]:\n',
                 '<my url>\n',
                 '\'my title\'\n']
        token = block_token.Document(lines)
        self.assertEqual(set(token.footnotes.values()), set({("my url", "my title")}))

    def test_parse_title_must_be_separated_from_link_destination(self):
        lines = ['[foo]: <bar> (baz)\n']
        token = block_token.Document(lines)
        self.assertEqual(set(token.footnotes.values()), set({("bar", "baz")}))

        lines = ['[foo]: <bar>(baz)\n']
        token = block_token.Document(lines)
        self.assertEqual(len(token.footnotes), 0)

    # this tests an edge case, it shouldn't occur in normal documents:
    # "[key 2]" is part of the paragraph above it, because a link reference definitions cannot interrupt a paragraph.
    def test_footnote_followed_by_paragraph(self):
        lines = ['[key 1]: value1\n',
                 'something1\n',
                 '[key 2]: value2\n',
                 'something2\n',
                 '\n',
                 '[key 3]: value3\r\n',  # '\r', or any other whitespace may follow on the same line
                 'something3\n']
        token = block_token.Document(lines)
        self.assertEqual(token.footnotes, {"key 1": ("value1", ""),
                                           "key 3": ("value3", "")})
        self.assertEqual(len(token.children), 2)
        self.assertIsInstance(token.children[0], block_token.Paragraph)
        # children: something1, <line break>, [key 2]: value2, <line break>, something2
        self.assertEqual(len(token.children[0].children), 5)
        self.assertEqual(token.children[0].children[2].content, "[key 2]: value2")
        self.assertEqual(token.children[1].children[0].content, "something3")

    def test_content_after_title_not_allowed(self):
        lines = ['[foo]: /url\n',
                 '"title" ok\n']
        token = block_token.Document(lines)
        self.assertEqual(token.footnotes, {"foo": ("/url", "")})
        self.assertEqual(len(token.children), 1)
        self.assertIsInstance(token.children[0], block_token.Paragraph)
        self.assertEqual(token.children[0].children[0].content, "\"title\" ok")

    def test_footnotes_may_not_have_too_much_leading_space(self):
        lines = ['   [link]: /bla\n',
                 '    [i-am-block-actually]: /foo\n',
                 'paragraph\n',
                 '\n',
                 '\t[i-am-block-too]: /foo\n']
        token = block_token.Document(lines)
        self.assertEqual(token.footnotes, {"link": ("/bla", "")})
        self.assertEqual(len(token.children), 3)
        self.assertIsInstance(token.children[0], block_token.BlockCode)
        self.assertEqual(token.children[0].children[0].content, "[i-am-block-actually]: /foo\n")
        self.assertIsInstance(token.children[1], block_token.Paragraph)
        self.assertEqual(token.children[1].children[0].content, "paragraph")
        self.assertIsInstance(token.children[2], block_token.BlockCode)
        self.assertEqual(token.children[2].children[0].content, "[i-am-block-too]: /foo\n")

    def test_parse_opening_bracket_as_paragraph(self):  # ... and no error is raised
        lines = ['[\n']
        token = block_token.Document(lines)
        self.assertEqual(len(token.footnotes), 0)
        self.assertEqual(len(token.children), 1)

        self.assertIsInstance(token.children[0], block_token.Paragraph)
        self.assertEqual(token.children[0].children[0].content, '[')

    def test_parse_opening_brackets_as_paragraph(self):  # ... and no lines are skipped
        lines = ['[\n',
                 '[ \n',
                 ']\n']
        token = block_token.Document(lines)
        self.assertEqual(len(token.footnotes), 0)
        self.assertEqual(len(token.children), 1)

        para = token.children[0]
        self.assertIsInstance(para, block_token.Paragraph)
        self.assertEqual(len(para.children), 5,
                'expected: RawText, LineBreak, RawText, LineBreak, RawText')
        self.assertEqual(para.children[0].content, '[')


class TestDocument(unittest.TestCase):
    def test_store_footnote(self):
        lines = ['[key 1]: value1\n',
                 '[key 2]: value2\n']
        document = block_token.Document(lines)
        self.assertEqual(document.footnotes['key 1'], ('value1', ''))
        self.assertEqual(document.footnotes['key 2'], ('value2', ''))

    def test_auto_splitlines(self):
        lines = "some\ncontinual\nlines\n"
        document = block_token.Document(lines)
        self.assertIsInstance(document.children[0], block_token.Paragraph)
        self.assertEqual(len(document.children), 1)


class TestThematicBreak(unittest.TestCase):
    def test_match(self):
        def test_case(line):
            token = next(iter(block_token.tokenize([line])))
            self.assertIsInstance(token, block_token.ThematicBreak)
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


class TestHtmlBlock(unittest.TestCase):
    def setUp(self):
        block_token.add_token(block_token.HtmlBlock)
        self.addCleanup(block_token.reset_tokens)

    def test_textarea_block_may_contain_blank_lines(self):
        lines = ['<textarea>\n',
                 '\n',
                 '*foo*\n',
                 '\n',
                 '_bar_\n',
                 '\n',
                 '</textarea>\n']
        document = block_token.Document(lines)
        tokens = document.children
        self.assertEqual(1, len(tokens))
        self.assertIsInstance(tokens[0], block_token.HtmlBlock)


class TestLeafBlockTokenContentProperty(unittest.TestCase):
    def setUp(self):
        block_token.add_token(block_token.HtmlBlock)
        self.addCleanup(block_token.reset_tokens)

    def test_code_fence(self):
        lines = ['```\n',
                 'line 1\n',
                 'line 2\n',
                 '```\n']
        document = block_token.Document(lines)
        tokens = document.children
        self.assertEqual(1, len(tokens))
        self.assertIsInstance(tokens[0], block_token.CodeFence)

        # option 1: direct access to the content
        self.assertEqual('line 1\nline 2\n', tokens[0].children[0].content)

        # option 2: using property getter to access the content
        self.assertEqual('line 1\nline 2\n', tokens[0].content)

    def test_block_code(self):
        lines = ['    line 1\n',
                 '    line 2\n']
        document = block_token.Document(lines)
        tokens = document.children
        self.assertEqual(1, len(tokens))
        self.assertIsInstance(tokens[0], block_token.BlockCode)

        # option 1: direct access to the content
        self.assertEqual('line 1\nline 2\n', tokens[0].children[0].content)

        # option 2: using property getter to access the content
        self.assertEqual('line 1\nline 2\n', tokens[0].content)

    def test_html_block(self):
        lines = ['<div>\n',
                 'text\n'
                 '</div>\n']
        document = block_token.Document(lines)
        tokens = document.children
        self.assertEqual(1, len(tokens))
        self.assertIsInstance(tokens[0], block_token.HtmlBlock)

        # option 1: direct access to the content
        self.assertEqual(''.join(lines).strip(), tokens[0].children[0].content)

        # option 2: using property getter to access the content
        self.assertEqual(''.join(lines).strip(), tokens[0].content)


class TestFileWrapper(unittest.TestCase):
    def test_get_set_pos(self):
        lines = [
            "# heading\n",
            "somewhat interesting\n",
            "content\n",
        ]
        wrapper = block_tokenizer.FileWrapper(lines)
        assert next(wrapper) == "# heading\n"
        anchor = wrapper.get_pos()
        assert next(wrapper) == "somewhat interesting\n"
        wrapper.set_pos(anchor)
        assert next(wrapper) == "somewhat interesting\n"

    def test_anchor_reset(self):
        lines = [
            "# heading\n",
            "somewhat interesting\n",
            "content\n",
        ]
        wrapper = block_tokenizer.FileWrapper(lines)
        assert next(wrapper) == "# heading\n"
        wrapper.anchor()
        assert next(wrapper) == "somewhat interesting\n"
        wrapper.reset()
        assert next(wrapper) == "somewhat interesting\n"
