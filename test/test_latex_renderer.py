from unittest import TestCase, mock
from parameterized import parameterized
import mistletoe.latex_renderer
from mistletoe.latex_renderer import LaTeXRenderer
from mistletoe import markdown


class TestLaTeXRenderer(TestCase):
    def setUp(self):
        self.renderer = LaTeXRenderer()
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

    def test_strong(self):
        self._test_token('Strong', '\\textbf{inner}')

    def test_emphasis(self):
        self._test_token('Emphasis', '\\textit{inner}')

    def test_inline_code(self):
        func_path = 'mistletoe.latex_renderer.LaTeXRenderer.render_raw_text'

        for content, expected in {'inner': '\\verb|inner|',
                                'a + b': '\\verb|a + b|',
                                'a | b': '\\verb!a | b!',
                                '|ab!|': '\\verb"|ab!|"',
                               }.items():
            with mock.patch(func_path, return_value=content):
                self._test_token('InlineCode', expected, content=content)

        content = mistletoe.latex_renderer.verb_delimiters
        with self.assertRaises(RuntimeError):
            with mock.patch(func_path, return_value=content):
                self._test_token('InlineCode', None, content=content)

    def test_strikethrough(self):
        self._test_token('Strikethrough', '\\sout{inner}')

    def test_image(self):
        expected = '\n\\includegraphics{src}\n'
        self._test_token('Image', expected, src='src')

    @parameterized.expand([
        ('page', '\\href{page}{inner}'),
        ('page%3A+with%3A+escape', '\\href{page\\%3A+with\\%3A+escape}{inner}'),
        ('page#target', '\\href{page\\#target}{inner}')
    ])
    def test_link(self, target, expected):
        self._test_token('Link', expected, target=target)

    @parameterized.expand([
        ('page', '\\url{page}'),
        ('page%3A+with%3A+escape', '\\url{page\\%3A+with\\%3A+escape}'),
        ('page#target', '\\url{page\\#target}')
    ])
    def test_autolink(self, target, expected):
        self._test_token('AutoLink', expected, target=target)

    def test_math(self):
        expected = '$ 1 + 2 = 3 $'
        self._test_token('Math', expected,
                         children=False, content='$ 1 + 2 = 3 $')

    def test_raw_text(self):
        expected = '\\$\\&\\#\\{\\}'
        self._test_token('RawText', expected,
                         children=False, content='$&#{}')

    def test_heading(self):
        expected = '\n\\section{inner}\n'
        self._test_token('Heading', expected, level=1)

    def test_quote(self):
        expected = '\\begin{displayquote}\ninner\\end{displayquote}\n'
        self._test_token('Quote', expected)

    def test_paragraph(self):
        expected = '\ninner\n'
        self._test_token('Paragraph', expected)

    def test_block_code(self):
        func_path = 'mistletoe.latex_renderer.LaTeXRenderer.render_raw_text'
        with mock.patch(func_path, return_value='inner'):
            expected = '\n\\begin{lstlisting}[language=sh]\ninner\\end{lstlisting}\n'
            self._test_token('BlockCode', expected, language='sh')

    def test_list(self):
        expected = '\\begin{itemize}\ninner\\end{itemize}\n'
        self._test_token('List', expected, start=None)

    def test_list_item(self):
        self._test_token('ListItem', '\\item inner\n')

    def test_table_with_header(self):
        func_path = 'mistletoe.latex_renderer.LaTeXRenderer.render_table_row'
        with mock.patch(func_path, autospec=True, return_value='row\n'):
            expected = '\\begin{tabular}{l c r}\nrow\n\\hline\ninner\\end{tabular}\n'
            self._test_token('Table', expected, column_align=[None, 0, 1])

    def test_table_without_header(self):
        expected = ('\\begin{tabular}\ninner\\end{tabular}\n')
        self._test_token('Table', expected, without_attrs=['header'],
                         column_align=[None])

    def test_table_row(self):
        self._test_token('TableRow', ' \\\\\n')

    def test_table_cell(self):
        self._test_token('TableCell', 'inner')

    def test_thematic_break(self):
        self._test_token('ThematicBreak', '\\hrulefill\n')

    def test_line_break(self):
        self._test_token('LineBreak', '\\newline\n', soft=False)

    def test_document(self):
        expected = ('\\documentclass{article}\n'
                  '\\begin{document}\n'
                  'inner'
                  '\\end{document}\n')
        self._test_token('Document', expected, footnotes={})


class TestHtmlEntity(TestCase):
    def test_html_entity(self):
        self.assertIn('hello \\& goodbye', markdown('hello &amp; goodbye', LaTeXRenderer))

    def test_html_entity_in_link_target(self):
        self.assertIn('\\href{foo}{hello}', markdown('[hello](f&#111;&#111;)', LaTeXRenderer))


class TestLaTeXFootnotes(TestCase):
    def setUp(self):
        self.renderer = LaTeXRenderer()
        self.renderer.__enter__()
        self.addCleanup(self.renderer.__exit__, None, None, None)

    def test_footnote_image(self):
        from mistletoe import Document
        raw = ['![alt][foo]\n', '\n', '[foo]: bar "title"\n']
        expected = ('\\documentclass{article}\n'
                  '\\usepackage{graphicx}\n'
                  '\\begin{document}\n'
                  '\n'
                  '\n\\includegraphics{bar}\n'
                  '\n'
                  '\\end{document}\n')
        self.assertEqual(self.renderer.render(Document(raw)), expected)

    def test_footnote_link(self):
        from mistletoe import Document
        raw = ['[name][key]\n', '\n', '[key]: target\n']
        expected = ('\\documentclass{article}\n'
                  '\\usepackage{hyperref}\n'
                  '\\begin{document}\n'
                  '\n'
                  '\\href{target}{name}'
                  '\n'
                  '\\end{document}\n')
        self.assertEqual(self.renderer.render(Document(raw)), expected)
