from unittest import TestCase, mock
from mistletoe.html_renderer import HTMLRenderer


class TestRenderer(TestCase):
    def setUp(self):
        self.renderer = HTMLRenderer()
        self.renderer.render_inner = mock.Mock(return_value='inner')
        self.renderer.__enter__()
        self.addCleanup(self.renderer.__exit__, None, None, None)

    def _test_token(self, token_name, output, children=True,
                    without_attrs=None, **kwargs):
        render_func = self.renderer.render_map[token_name]
        children = mock.MagicMock(spec=list) if children else None
        mock_token = mock.Mock(children=children, **kwargs)
        without_attrs = without_attrs or []
        for attr in without_attrs:
            delattr(mock_token, attr)
        self.assertEqual(render_func(mock_token), output)


class TestHTMLRenderer(TestRenderer):
    def test_strong(self):
        self._test_token('Strong', '<strong>inner</strong>')

    def test_emphasis(self):
        self._test_token('Emphasis', '<em>inner</em>')

    def test_inline_code(self):
        from mistletoe.span_token import tokenize_inner
        rendered = self.renderer.render(tokenize_inner('`foo`')[0])
        self.assertEqual(rendered, '<code>foo</code>')

    def test_strikethrough(self):
        self._test_token('Strikethrough', '<del>inner</del>')

    def test_image(self):
        output = '<img src="src" alt="" title="title" />'
        self._test_token('Image', output, src='src', title='title')

    def test_link(self):
        output = '<a href="target" title="title">inner</a>'
        self._test_token('Link', output, target='target', title='title')

    def test_autolink(self):
        output = '<a href="link">inner</a>'
        self._test_token('AutoLink', output, target='link', mailto=False)

    def test_escape_sequence(self):
        self._test_token('EscapeSequence', 'inner')

    def test_raw_text(self):
        self._test_token('RawText', 'john &amp; jane',
                         children=False, content='john & jane')

    def test_html_span(self):
        self._test_token('HTMLSpan', '<some>text</some>',
                         children=False, content='<some>text</some>')

    def test_heading(self):
        output = '<h3>inner</h3>'
        self._test_token('Heading', output, level=3)

    def test_quote(self):
        output = '<blockquote>\n</blockquote>'
        self._test_token('Quote', output)

    def test_paragraph(self):
        self._test_token('Paragraph', '<p>inner</p>')

    def test_block_code(self):
        from mistletoe.block_token import tokenize
        rendered = self.renderer.render(tokenize(['```sh\n', 'foo\n', '```\n'])[0])
        output = '<pre><code class="language-sh">foo\n</code></pre>'
        self.assertEqual(rendered, output)

    def test_block_code_no_language(self):
        from mistletoe.block_token import tokenize
        rendered = self.renderer.render(tokenize(['```\n', 'foo\n', '```\n'])[0])
        output = '<pre><code>foo\n</code></pre>'
        self.assertEqual(rendered, output)

    def test_list(self):
        output = '<ul>\n\n</ul>'
        self._test_token('List', output, start=None)

    def test_list_item(self):
        output = '<li></li>'
        self._test_token('ListItem', output)

    def test_table_with_header(self):
        func_path = 'mistletoe.html_renderer.HTMLRenderer.render_table_row'
        with mock.patch(func_path, autospec=True) as mock_func:
            mock_func.return_value = 'row'
            output = ('<table>\n'
                        '<thead>\nrow</thead>\n'
                        '<tbody>\ninner</tbody>\n'
                      '</table>')
            self._test_token('Table', output)

    def test_table_without_header(self):
        func_path = 'mistletoe.html_renderer.HTMLRenderer.render_table_row'
        with mock.patch(func_path, autospec=True) as mock_func:
            mock_func.return_value = 'row'
            output = '<table>\n<tbody>\ninner</tbody>\n</table>'
            self._test_token('Table', output, without_attrs=['header',])

    def test_table_row(self):
        self._test_token('TableRow', '<tr>\n</tr>\n')

    def test_table_cell(self):
        output = '<td align="left">inner</td>\n'
        self._test_token('TableCell', output, align=None)
        
    def test_table_cell0(self):
        output = '<td align="center">inner</td>\n'
        self._test_token('TableCell', output, align=0)
        
    def test_table_cell1(self):
        output = '<td align="right">inner</td>\n'
        self._test_token('TableCell', output, align=1)

    def test_thematic_break(self):
        self._test_token('ThematicBreak', '<hr />', children=False)

    def test_html_block(self):
        content = output = '<h1>hello</h1>\n<p>this is\na paragraph</p>\n'
        self._test_token('HTMLBlock', output,
                         children=False, content=content)

    def test_line_break(self):
        self._test_token('LineBreak', '<br />\n', children=False, soft=False)

    def test_document(self):
        self._test_token('Document', '', footnotes={})


class TestHTMLRendererFootnotes(TestCase):
    def setUp(self):
        self.renderer = HTMLRenderer()
        self.renderer.__enter__()
        self.addCleanup(self.renderer.__exit__, None, None, None)

    def test_footnote_image(self):
        from mistletoe import Document
        token = Document(['![alt][foo]\n', '\n', '[foo]: bar "title"\n'])
        output = '<p><img src="bar" alt="alt" title="title" /></p>\n'
        self.assertEqual(self.renderer.render(token), output)

    def test_footnote_link(self):
        from mistletoe import Document
        token = Document(['[name][foo]\n', '\n', '[foo]: target\n'])
        output = '<p><a href="target">name</a></p>\n' 
        self.assertEqual(self.renderer.render(token), output)
