import unittest
import mistletoe.block_token as block_token
import mistletoe.span_token as span_token
import mistletoe.html_token as html_token
import mistletoe.html_renderer as renderer

class TestHTMLRenderer(unittest.TestCase):
    def _test_token(self, token_type, raw, target):
        output = renderer.render(token_type(raw))
        self.assertEqual(output, target)

    def test_strong(self):
        raw, target = 'some text', '<strong>some text</strong>'
        self._test_token(span_token.Strong, raw, target)

    def test_emphasis(self):
        raw, target = 'some text', '<em>some text</em>'
        self._test_token(span_token.Emphasis, raw, target)

    def test_inline_code(self):
        raw, target = 'some code', '<code>some code</code>'
        self._test_token(span_token.InlineCode, raw, target)

    def test_strikethrough(self):
        raw, target = 'some text', '<del>some text</del>'
        self._test_token(span_token.Strikethrough, raw, target)

    def test_image(self):
        raw = '![alt](src "title")'
        target = '<img src="src" title="title" alt="alt">'
        self._test_token(span_token.Image, raw, target)

    def test_footnote_image(self):
        raw = ['![alt] [foo]\n', '\n', '[foo]: bar "title"\n']
        target = ('<html>\n<body>\n'
                  '<p><img src="bar" title="title" alt="alt"></p>\n'
                  '</body>\n</html>\n')
        self._test_token(block_token.Document, raw, target)

    def test_link(self):
        raw, target = '[name](target)', '<a href="target">name</a>'
        self._test_token(span_token.Link, raw, target)

    def test_footnote_link(self):
        raw = ['[name] [key]\n', '\n', '[key]: target\n']
        target = ('<html>\n<body>\n'
                  '<p><a href="target">name</a></p>\n'
                  '</body>\n</html>\n')
        self._test_token(block_token.Document, raw, target)

    def test_autolink(self):
        raw, target = 'link', '<a href="link">link</a>'
        self._test_token(span_token.AutoLink, raw, target)

    def test_escape_sequence(self):
        raw, target = '\*', '\*'
        self._test_token(span_token.EscapeSequence, raw, target)

    def test_raw_text(self):
        raw, target = 'john & jane', 'john &amp; jane'
        self._test_token(span_token.RawText, raw, target)

    def test_html_span(self):
        raw = target = '<some>text</some>'
        with html_token.Context():
            self._test_token(span_token.HTMLSpan, raw, target)

    def test_heading(self):
        raw, target = [ '### heading 3\n' ], '<h3>heading 3</h3>\n'
        self._test_token(block_token.Heading, raw, target)

    def test_quote(self):
        raw = ['> ## heading 2\n', '> a paragraph\n', '> continued\n']
        target = ('<blockquote>\n<h2>heading 2</h2>\n'
                  '<p>a paragraph continued</p>\n</blockquote>\n')
        self._test_token(block_token.Quote, raw, target)

    def test_paragraph(self):
        raw = ['a paragraph\n', 'continued\n']
        target = '<p>a paragraph continued</p>\n'
        self._test_token(block_token.Paragraph, raw, target)

    def test_block_code(self):
        raw = ['```sh\n', 'mkdir temp\n', 'rmdir temp\n', '```\n']
        target = ('<pre>\n<code class="lang-sh">\nmkdir temp\n'
                  'rmdir temp\n</code>\n</pre>\n')
        self._test_token(block_token.BlockCode, raw, target)

    def test_list(self):
        raw = ['- item 1\n',
               '- item 2\n',
               '    2. nested item 1\n',
               '    3. nested item 2\n',
               '        * further nested\n',
               '- item 3\n']
        target = ('<html>\n<body>\n'
                  '<ul>\n'
                    '<li>item 1</li>\n'
                    '<li>item 2</li>\n'
                    '<ol start="2">\n'
                      '<li>nested item 1</li>\n'
                      '<li>nested item 2</li>\n'
                      '<ul>\n<li>further nested</li>\n</ul>\n'
                    '</ol>\n'
                    '<li>item 3</li>\n'
                  '</ul>\n'
                  '</body>\n</html>\n')
        self._test_token(block_token.Document, raw, target)

    def test_list_item(self):
        raw = ['    - some **bold** text\n']
        target = '<li>some <strong>bold</strong> text</li>\n'
        self._test_token(block_token.ListItem, raw, target)

    def test_table_with_heading(self):
        raw = ['| header 1 | header 2 | header 3 |\n',
                 '| :--- | :---: | ---: |\n',
                 '| cell 1 | cell 2 | cell 3 |\n',
                 '| more 1 | more 2 | more 3 |\n']
        target = ('<table>\n'
                    '<thead>\n'
                      '<tr>\n'
                        '<th align="left">header 1</th>\n'
                        '<th align="center">header 2</th>\n'
                        '<th align="right">header 3</th>\n'
                      '</tr>\n'
                    '</thead>\n'
                    '<tbody>\n'
                       '<tr>\n'
                         '<td align="left">cell 1</td>\n'
                         '<td align="center">cell 2</td>\n'
                         '<td align="right">cell 3</td>\n'
                       '</tr>\n'
                       '<tr>\n'
                         '<td align="left">more 1</td>\n'
                         '<td align="center">more 2</td>\n'
                         '<td align="right">more 3</td>\n'
                       '</tr>\n'
                    '</tbody>\n'
                  '</table>\n')
        self._test_token(block_token.Table, raw, target)

    def test_table_without_heading(self):
        raw = ['| cell 1 | cell 2 | cell 3 |\n',
                 '| more 1 | more 2 | more 3 |\n']
        target = ('<table>\n'
                    '<tbody>\n'
                      '<tr>\n'
                        '<td align="left">cell 1</td>\n'
                        '<td align="left">cell 2</td>\n'
                        '<td align="left">cell 3</td>\n'
                      '</tr>\n'
                      '<tr>\n'
                        '<td align="left">more 1</td>\n'
                        '<td align="left">more 2</td>\n'
                        '<td align="left">more 3</td>\n'
                        '</tr>\n'
                    '</tbody>\n'
                  '</table>\n')
        self._test_token(block_token.Table, raw, target)

    def test_table_row(self):
        raw = '| cell 1 | cell 2 | cell 3 |\n'
        target = ('<tr>\n'
                    '<td align="left">cell 1</td>\n'
                    '<td align="left">cell 2</td>\n'
                    '<td align="left">cell 3</td>\n'
                  '</tr>\n')
        self._test_token(block_token.TableRow, raw, target)

    def test_table_cell(self):
        raw, target= 'cell', '<td align="left">cell</td>\n'
        self._test_token(block_token.TableCell, raw, target)

    def test_separator(self):
        raw, target = '***\n', '<hr>\n'
        self._test_token(block_token.Separator, raw, target)

    def test_html_block(self):
        raw = ['# hello\n',
               '<p>this is\n',
               'a paragraph</p>\n']
        target = ('<html>\n<body>\n'
                  '<h1>hello</h1>\n'
                  '<p>this is\na paragraph</p>\n'
                  '</body>\n</html>\n')
        with html_token.Context():
            self._test_token(block_token.Document, raw, target)

    def test_document(self):
        raw = ['a paragraph\n']
        target = '<html>\n<body>\n<p>a paragraph</p>\n</body>\n</html>\n'
        self._test_token(block_token.Document, raw, target)
