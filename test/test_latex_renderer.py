from unittest import TestCase, mock
import mistletoe.latex_token as latex_token
from mistletoe.latex_renderer import LaTeXRenderer


class TestLaTeXRenderer(TestCase):
    def setUp(self):
        self.renderer = LaTeXRenderer()
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

    def test_strong(self):
        self._test_token('Strong', '\\textbf{inner}')

    def test_emphasis(self):
        self._test_token('Emphasis', '\\textit{inner}')

    def test_inline_code(self):
        func_path = 'mistletoe.latex_renderer.LaTeXRenderer.render_raw_text'
        with mock.patch(func_path, return_value='inner'):
            self._test_token('InlineCode', '\\verb|inner|')

    def test_strikethrough(self):
        self._test_token('Strikethrough', '\\sout{inner}')

    def test_image(self):
        output = '\n\\includegraphics{src}\n'
        self._test_token('Image', output, src='src')

    def test_link(self):
        output = '\\href{target}{inner}'
        self._test_token('Link', output, target='target')

    def test_autolink(self):
        output = '\\url{target}'
        self._test_token('AutoLink', output, target='target')

    def test_math(self):
        output = '$ 1 + 2 = 3 $'
        self._test_token('Math', output,
                         children=False, content='$ 1 + 2 = 3 $')

    def test_raw_text(self):
        output = '\\$\\&\\#\\{\\}'
        self._test_token('RawText', output,
                         children=False, content='$&#{}')

    def test_heading(self):
        output = '\n\\section{inner}\n'
        self._test_token('Heading', output, level=1)

    def test_quote(self):
        output = '\\begin{displayquote}\ninner\\end{displayquote}\n'
        self._test_token('Quote', output)

    def test_paragraph(self):
        output = '\ninner\n'
        self._test_token('Paragraph', output)

    def test_block_code(self):
        func_path = 'mistletoe.latex_renderer.LaTeXRenderer.render_raw_text'
        with mock.patch(func_path, return_value='inner'):
            output = '\n\\begin{lstlisting}[language=sh]\ninner\\end{lstlisting}\n'
            self._test_token('BlockCode', output, language='sh')

    def test_list(self):
        output = '\\begin{itemize}\ninner\\end{itemize}\n'
        self._test_token('List', output, start=None)

    def test_list_item(self):
        self._test_token('ListItem', '\\item inner\n')

    def test_table_with_header(self):
        func_path = 'mistletoe.latex_renderer.LaTeXRenderer.render_table_row'
        with mock.patch(func_path, autospec=True, return_value='row\n'):
            output = '\\begin{tabular}{l c r}\nrow\n\\hline\ninner\\end{tabular}\n'
            self._test_token('Table', output, column_align=[None, 0, 1])

    def test_table_without_header(self):
        output = ('\\begin{tabular}\ninner\\end{tabular}\n')
        self._test_token('Table', output, without_attrs=['header'],
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
        output = ('\\documentclass{article}\n'
                  '\\begin{document}\n'
                  'inner'
                  '\\end{document}\n')
        self._test_token('Document', output, footnotes={})


class TestLaTeXFootnotes(TestCase):
    def setUp(self):
        self.renderer = LaTeXRenderer()
        self.renderer.__enter__()
        self.addCleanup(self.renderer.__exit__, None, None, None)

    def test_footnote_image(self):
        from mistletoe import Document
        raw = ['![alt][foo]\n', '\n', '[foo]: bar "title"\n']
        target = ('\\documentclass{article}\n'
                  '\\usepackage{graphicx}\n'
                  '\\begin{document}\n'
                  '\n'
                  '\n\\includegraphics{bar}\n'
                  '\n'
                  '\\end{document}\n')
        self.assertEqual(self.renderer.render(Document(raw)), target)

    def test_footnote_link(self):
        from mistletoe import Document
        raw = ['[name][key]\n', '\n', '[key]: target\n']
        target = ('\\documentclass{article}\n'
                  '\\usepackage{hyperref}\n'
                  '\\begin{document}\n'
                  '\n'
                  '\\href{target}{name}'
                  '\n'
                  '\\end{document}\n')
        self.assertEqual(self.renderer.render(Document(raw)), target)
