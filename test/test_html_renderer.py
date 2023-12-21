from unittest import TestCase, mock
from mistletoe import Document
from mistletoe.html_renderer import HtmlRenderer
from parameterized import parameterized


class TestRenderer(TestCase):
    def setUp(self):
        self.renderer = HtmlRenderer()
        self.renderer.render_inner = mock.Mock(return_value='inner')
        self.renderer.__enter__()
        self.addCleanup(self.renderer.__exit__, None, None, None)

    def _test_token(self, token_name, expected_output, children=True,
                    without_attrs=None, **kwargs):
        render_func = self.renderer.render_map[token_name]
        children = mock.MagicMock(spec=list) if children else None
        mock_token = mock.Mock(children=children, **kwargs)
        without_attrs = without_attrs or []
        for attr in without_attrs:
            delattr(mock_token, attr)
        self.assertEqual(render_func(mock_token), expected_output)


class TestHtmlRenderer(TestRenderer):
    def test_strong(self):
        self._test_token('Strong', '<strong>inner</strong>')

    def test_emphasis(self):
        self._test_token('Emphasis', '<em>inner</em>')

    def test_inline_code(self):
        from mistletoe.span_token import tokenize_inner
        output = self.renderer.render(tokenize_inner('`foo`')[0])
        self.assertEqual(output, '<code>foo</code>')
        output = self.renderer.render(tokenize_inner('`` \\[\\` ``')[0])
        self.assertEqual(output, '<code>\\[\\`</code>')

    def test_strikethrough(self):
        self._test_token('Strikethrough', '<del>inner</del>')

    def test_image(self):
        expected = '<img src="src" alt="" title="title" />'
        self._test_token('Image', expected, src='src', title='title')

    def test_link(self):
        expected = '<a href="target" title="title">inner</a>'
        self._test_token('Link', expected, target='target', title='title')

    def test_autolink(self):
        expected = '<a href="link">inner</a>'
        self._test_token('AutoLink', expected, target='link', mailto=False)

    def test_escape_sequence(self):
        self._test_token('EscapeSequence', 'inner')

    def test_raw_text(self):
        self._test_token('RawText', 'john &amp; jane',
                         children=False, content='john & jane')

    def test_html_span(self):
        self._test_token('HtmlSpan', '<some>text</some>',
                         children=False, content='<some>text</some>')

    def test_heading(self):
        expected = '<h3>inner</h3>'
        self._test_token('Heading', expected, level=3)

    def test_quote(self):
        expected = '<blockquote>\n</blockquote>'
        self._test_token('Quote', expected)

    def test_paragraph(self):
        self._test_token('Paragraph', '<p>inner</p>')

    def test_block_code(self):
        from mistletoe.block_token import tokenize
        output = self.renderer.render(tokenize(['```sh\n', 'foo\n', '```\n'])[0])
        expected = '<pre><code class="language-sh">foo\n</code></pre>'
        self.assertEqual(output, expected)

    def test_block_code_no_language(self):
        from mistletoe.block_token import tokenize
        output = self.renderer.render(tokenize(['```\n', 'foo\n', '```\n'])[0])
        expected = '<pre><code>foo\n</code></pre>'
        self.assertEqual(output, expected)

    def test_list(self):
        expected = '<ul>\n\n</ul>'
        self._test_token('List', expected, start=None)

    def test_list_item(self):
        expected = '<li></li>'
        self._test_token('ListItem', expected)

    def test_table_with_header(self):
        func_path = 'mistletoe.html_renderer.HtmlRenderer.render_table_row'
        with mock.patch(func_path, autospec=True) as mock_func:
            mock_func.return_value = 'row'
            expected = ('<table>\n'
                        '<thead>\nrow</thead>\n'
                        '<tbody>\ninner</tbody>\n'
                      '</table>')
            self._test_token('Table', expected)

    def test_table_without_header(self):
        func_path = 'mistletoe.html_renderer.HtmlRenderer.render_table_row'
        with mock.patch(func_path, autospec=True) as mock_func:
            mock_func.return_value = 'row'
            expected = '<table>\n<tbody>\ninner</tbody>\n</table>'
            self._test_token('Table', expected, without_attrs=['header',])

    def test_table_row(self):
        self._test_token('TableRow', '<tr>\n</tr>\n')

    def test_table_cell(self):
        expected = '<td align="left">inner</td>\n'
        self._test_token('TableCell', expected, align=None)

    def test_table_cell0(self):
        expected = '<td align="center">inner</td>\n'
        self._test_token('TableCell', expected, align=0)

    def test_table_cell1(self):
        expected = '<td align="right">inner</td>\n'
        self._test_token('TableCell', expected, align=1)

    def test_thematic_break(self):
        self._test_token('ThematicBreak', '<hr />', children=False)

    def test_html_block(self):
        content = expected = '<h1>hello</h1>\n<p>this is\na paragraph</p>\n'
        self._test_token('HtmlBlock', expected,
                         children=False, content=content)

    def test_line_break(self):
        self._test_token('LineBreak', '<br />\n', children=False, soft=False)

    def test_document(self):
        self._test_token('Document', '', footnotes={})


class TestHtmlRendererEscaping(TestCase):
    @parameterized.expand([
        (False, False, '" and \''),
        (False, True, '" and &#x27;'),
        (True, False, '&quot; and \''),
        (True, True, '&quot; and &#x27;'),
    ])
    def test_escape_html_text(self, escape_double, escape_single, expected):
        with HtmlRenderer(html_escape_double_quotes=escape_double,
                          html_escape_single_quotes=escape_single) as renderer:
            self.assertEqual(renderer.escape_html_text('" and \''), expected)

    def test_unprocessed_html_tokens_escaped(self):
        with HtmlRenderer(process_html_tokens=False) as renderer:
            token = Document(['<div><br> as plain text</div>\n'])
            expected = '<p>&lt;div&gt;&lt;br&gt; as plain text&lt;/div&gt;</p>\n'
            self.assertEqual(renderer.render(token), expected)


class TestHtmlRendererFootnotes(TestCase):
    def setUp(self):
        self.renderer = HtmlRenderer()
        self.renderer.__enter__()
        self.addCleanup(self.renderer.__exit__, None, None, None)

    def test_footnote_image(self):
        token = Document(['![alt][foo]\n', '\n', '[foo]: bar "title"\n'])
        expected = '<p><img src="bar" alt="alt" title="title" /></p>\n'
        self.assertEqual(self.renderer.render(token), expected)

    def test_footnote_link(self):
        token = Document(['[name][foo]\n', '\n', '[foo]: target\n'])
        expected = '<p><a href="target">name</a></p>\n'
        self.assertEqual(self.renderer.render(token), expected)
