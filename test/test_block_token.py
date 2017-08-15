import unittest
import mistletoe.span_token as span_token
import mistletoe.block_token as block_token


class TestHeading(unittest.TestCase):
    def test_parse_atx(self):
        token = next(block_token.tokenize(['### heading 3\n']))
        self.assertIsInstance(token, block_token.Heading)
        self.assertEqual(token.level, 3)

    def test_parse_setext(self):
        token = next(block_token.tokenize(['some\n', 'heading\n', '---\n']))
        self.assertIsInstance(token, block_token.Heading)
        self.assertEqual(token.level, 2)

    def test_children_with_enclosing_hashes(self):
        token = next(block_token.tokenize(['### heading 3 #####  \n']))
        child = next(token.children)
        self.assertIsInstance(child, span_token.RawText)
        self.assertEqual(child.content, 'heading 3')


class TestQuote(unittest.TestCase):
    def test_parse(self):
        token = next(block_token.tokenize(['> line 1\n', '> line 2\n']))
        self.assertIsInstance(token, block_token.Quote)

    def test_children(self):
        token = next(block_token.tokenize(['> line 1\n', '> line 2\n']))

        child = next(token.children)
        self.assertIsInstance(child, block_token.Paragraph)

        grandchild = next(child.children)
        self.assertIsInstance(grandchild, span_token.RawText)
        self.assertEqual(grandchild.content, 'line 1 line 2')

    def test_lazy_continuation(self):
        token = next(block_token.tokenize(['> line 1\n', 'line 2\n']))

        child = next(token.children)
        self.assertIsInstance(child, block_token.Paragraph)

        grandchild = next(child.children)
        self.assertIsInstance(grandchild, span_token.RawText)
        self.assertEqual(grandchild.content, 'line 1 line 2')


class TestBlockCode(unittest.TestCase):
    def test_parse_fenced_code(self):
        lines = ['```sh\n', 'rm dir\n', 'mkdir test\n', '```\n']
        token = next(block_token.tokenize(lines))
        self.assertIsInstance(token, block_token.BlockCode)
        self.assertEqual(token.language, 'sh')

    def test_children_in_fenced_code(self):
        lines = ['```sh\n', 'rm dir\n', 'mkdir test\n', '```\n']
        token = next(block_token.tokenize(lines))
        child = next(token.children)
        self.assertIsInstance(child, span_token.RawText)
        self.assertEqual(child.content, 'rm dir\nmkdir test\n')

    def test_fence_code_lazy_continuation(self):
        lines = ['```sh\n', 'rm dir\n', '\n', 'mkdir test\n', '```\n']
        token = next(block_token.tokenize(lines))
        self.assertIsInstance(token, block_token.BlockCode)

        child = next(token.children)
        self.assertIsInstance(child, span_token.RawText)
        self.assertEqual(child.content, 'rm dir\n \nmkdir test\n')

    def test_hashes(self):
        lines = ['```python\n', '# comment\n', '```\n']
        token = next(block_token.tokenize(lines))
        child = next(token.children)
        self.assertIsInstance(child, span_token.RawText)
        self.assertEqual(child.content, '# comment\n')

    def test_parse_indented_code(self):
        lines = ['    rm dir\n', '    mkdir test\n']
        token = next(block_token.tokenize(lines))
        self.assertIsInstance(token, block_token.BlockCode)
        self.assertEqual(token.language, '')

    def test_children_in_indented_code(self):
        lines = ['    rm dir\n', '    mkdir test\n']
        token = next(block_token.tokenize(lines))
        child = next(token.children)
        self.assertIsInstance(child, span_token.RawText)
        self.assertEqual(child.content, 'rm dir\nmkdir test\n')


class TestParagraph(unittest.TestCase):
    def test_parse(self):
        lines = ['some\n', 'continuous\n', 'lines\n']
        token = next(block_token.tokenize(lines))
        self.assertIsInstance(token, block_token.Paragraph)

    def test_children(self):
        lines = ['some\n', 'continuous\n', 'lines\n']
        token = next(block_token.tokenize(lines))
        child = next(token.children)
        self.assertIsInstance(child, span_token.RawText)
        self.assertEqual(child.content, 'some continuous lines')


class TestListItem(unittest.TestCase):
    def test_children(self):
        token = block_token.ListItem(['- some text\n'])
        child = next(token.children)
        self.assertIsInstance(child, span_token.RawText)
        self.assertEqual(child.content, 'some text')

    def test_lazy_continuation(self):
        token = block_token.ListItem(['- list\n', 'content\n'])
        child = next(token.children)
        self.assertIsInstance(child, span_token.RawText)
        self.assertEqual(child.content, 'list content')

    def test_whitespace(self):
        token = block_token.ListItem(['-   text  \n'])
        child = next(token.children)
        self.assertEqual(child.content, 'text')


class TestList(unittest.TestCase):
    def test_parse_unordered_list(self):
        token = next(block_token.tokenize(['- a list\n', 'continued\n']))
        self.assertIsInstance(token, block_token.List)
        self.assertIsNone(token.start)

    def test_parse_ordered_list(self):
        lines = ['1) item 1\n',
                 '2) item 2\n',
                 '    * nested item 1\n',
                 '    * nested item 2\n',
                 '3) item 3\n']
        token = next(block_token.tokenize(lines))
        self.assertIsInstance(token, block_token.List)
        self.assertEqual(token.start, 1)

    def test_children(self):
        token = next(block_token.tokenize(['- a list\n', 'continued\n']))
        child = next(token.children)
        self.assertIsInstance(child, block_token.ListItem)

    def test_parse_nested_lists(self):
        lines = ['- item 1\n',
                 '- item 2\n',
                 '    * nested item 1\n',
                 '    * nested item 2\n',
                 '- item 3\n']
        tokens = next(block_token.tokenize(lines)).children

        token1 = next(tokens)
        self.assertIsInstance(token1, block_token.ListItem)

        token2 = next(tokens)
        self.assertIsInstance(token2, block_token.ListItem)

        token3 = next(tokens)
        self.assertIsInstance(token3, block_token.List)

        token4 = next(tokens)
        self.assertIsInstance(token4, block_token.ListItem)

    def test_lazy_continuation(self):
        lines = ['* item 1\n',
                 '* item 2\n',
                 '  continued with indent\n',
                 '* item 3\n',
                 'with lazy continuation\n',
                 '    + nested item 1\n',
                 '    continued\n']
        tokens = next(block_token.tokenize(lines)).children
        
        token1 = next(tokens)
        self.assertIsInstance(token1, block_token.ListItem)

        token2 = next(tokens)
        self.assertIsInstance(token2, block_token.ListItem)

        token3 = next(tokens)
        self.assertIsInstance(token3, block_token.ListItem)

        token4 = next(tokens)
        self.assertIsInstance(token4, block_token.List)


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

    def test_parse(self):
        lines = ['| header 1 | header 2 | header 3 |\n',
                 '| --- | --- | --- |\n',
                 '| cell 1 | cell 2 | cell 3 |\n',
                 '| more 1 | more 2 | more 3 |\n']
        token = next(block_token.tokenize(lines))
        self.assertIsInstance(token, block_token.Table)
        self.assertEqual(token.has_header, True)
        self.assertEqual(token.column_align, [None, None, None])


class TestTableRow(unittest.TestCase):
    def test_parse(self):
        lines = ['| cell 1 | cell 2 |\n',
                 '| more 1 | more 2 |\n']
        token = next(block_token.Table(lines).children)
        self.assertIsInstance(token, block_token.TableRow)
        self.assertEqual(token.row_align, [None])


class TestTableCell(unittest.TestCase):
    def test_parse(self):
        token = next(block_token.TableRow('| cell 2 |\n').children)
        self.assertIsInstance(token, block_token.TableCell)
        self.assertEqual(token.align, None)

    def test_children(self):
        token = next(block_token.TableRow('| cell 2 |\n').children)
        child = next(token.children)
        self.assertIsInstance(child, span_token.RawText)
        self.assertEqual(child.content, 'cell 2')


class TestFootnoteBlock(unittest.TestCase):
    def test_parse(self):
        lines = ['[key 1]: value 1\n',
                 '[key 2]: value 2\n']
        token = next(block_token.tokenize(lines))
        self.assertIsInstance(token, block_token.FootnoteBlock)


class TestFootnoteEntry(unittest.TestCase):
    def test_parse(self):
        lines = ['[key]: value\n']
        token = next(block_token.FootnoteBlock(lines).children)
        self.assertIsInstance(token, block_token.FootnoteEntry)
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
    def test_parse(self):
        token = next(block_token.tokenize(['---\n']))
        self.assertIsInstance(token, block_token.Separator)
