import unittest
import mistletoe.block_token as block_token
import mistletoe.span_token as span_token
import mistletoe.latex_token as latex_token
from mistletoe.latex_renderer import LaTeXRenderer

class TestLaTeXRenderer(unittest.TestCase):
    def _test_token(self, token_type, raw, target):
        with LaTeXRenderer() as renderer:
            self.assertEqual(renderer.render(token_type(raw)), target)

    def test_strong(self):
        raw, target = 'some text', '\\textbf{some text}'
        self._test_token(span_token.Strong, raw, target)

    def test_emphasis(self):
        raw, target = 'some text', '\\textit{some text}'
        self._test_token(span_token.Emphasis, raw, target)

    def test_inline_code(self):
        raw, target = 'some code', '\\verb|some code|'
        self._test_token(span_token.InlineCode, raw, target)

    def test_strikethrough(self):
        raw, target = 'some text', '\\sout{some text}'
        self._test_token(span_token.Strikethrough, raw, target)

    def test_image(self):
        raw, target = '![alt](src "title")', '\n\\includegraphics{src}\n'
        self._test_token(span_token.Image, raw, target)

    def test_footnote_image(self):
        raw = ['![alt] [foo]\n', '\n', '[foo]: bar "title"\n']
        target = ('\\documentclass{article}\n'
                  '\\usepackage{csquotes}\n'
                  '\\usepackage{hyperref}\n'
                  '\\usepackage{graphicx}\n'
                  '\\usepackage{listings}\n'
                  '\\usepackage[normalem]{ulem}\n'
                  '\\begin{document}\n'
                  '\n'
                  '\n\\includegraphics{bar}\n'
                  '\n'
                  '\\end{document}\n')
        self._test_token(block_token.Document, raw, target)

    def test_link(self):
        raw, target = '[name](target)', '\\href{target}{name}'
        self._test_token(span_token.Link, raw, target)

    def test_footnote_link(self):
        raw = ['[name] [key]\n', '\n', '[key]: target\n']
        target = ('\\documentclass{article}\n'
                  '\\usepackage{csquotes}\n'
                  '\\usepackage{hyperref}\n'
                  '\\usepackage{graphicx}\n'
                  '\\usepackage{listings}\n'
                  '\\usepackage[normalem]{ulem}\n'
                  '\\begin{document}\n'
                  '\n'
                  '\\href{target}{name}'
                  '\n'
                  '\\end{document}\n')
        self._test_token(block_token.Document, raw, target)

    def test_autolink(self):
        raw, target = 'target', '\\url{target}'
        self._test_token(span_token.AutoLink, raw, target)

    def test_math(self):
        raw, target = '$ 1 + 2 = 3 $', '$ 1 + 2 = 3 $'
        self._test_token(latex_token.Math, raw, target)

    def test_raw_text(self):
        raw, target = '$&#{}', '\\$\\&\\#\\{\\}'
        self._test_token(span_token.RawText, raw, target)

    def test_heading(self):
        raw, target = ['# heading 1\n'], '\n\\section{heading 1}\n'
        self._test_token(block_token.Heading, raw, target)

    def test_quote(self):
        raw = ['> ## heading 2\n', '> a paragraph\n', '> continued\n']
        target = ('\\begin{displayquote}\n'
                  '\n'
                  '\\subsection{heading 2}\n'
                  '\n'
                  'a paragraph continued\n'
                  '\\end{displayquote}\n')
        self._test_token(block_token.Quote, raw, target)

    def test_paragraph(self):
        raw = ['a paragraph\n', 'continued\n']
        target = '\na paragraph continued\n'
        self._test_token(block_token.Paragraph, raw, target)

    def test_block_code(self):
        raw = ['```sh\n', 'mkdir temp\n', 'rmdir temp\n', '```\n']
        target = ('\n\\begin{lstlisting}[language=sh]\n'
                  'mkdir temp\n'
                  'rmdir temp\n'
                  '\\end{lstlisting}\n')
        self._test_token(block_token.BlockCode, raw, target)

    def test_list(self):
        raw = ['- item 1\n',
               '- item 2\n',
               '    2. nested item 1\n',
               '    3. nested item 2\n',
               '        * further nested\n',
               '- item 3\n']
        target = ('\\begin{itemize}\n'
                    '\\item item 1\n'
                    '\\item item 2\n'
                    '\\begin{enumerate}\n'
                      '\\item nested item 1\n'
                      '\\item nested item 2\n'
                      '\\begin{itemize}\n'
                        '\\item further nested\n'
                      '\\end{itemize}\n'
                    '\\end{enumerate}\n'
                    '\\item item 3\n'
                  '\\end{itemize}\n')
        self._test_token(block_token.List, raw, target)

    def test_list_item(self):
        raw = ['    - some **bold** text\n']
        target = '\\item some \\textbf{bold} text\n'
        self._test_token(block_token.ListItem, raw, target)

    def test_table_with_heading(self):
        raw = ['| header 1 | header 2 | header 3 |\n',
                 '| :--- | :---: | ---: |\n',
                 '| cell 1 | cell 2 | cell 3 |\n',
                 '| more 1 | more 2 | more 3 |\n']
        target = ('\\begin{tabular}{l c r}\n'
                    'header 1 & header 2 & header 3\n'
                    '\hline\n'
                    'cell 1 & cell 2 & cell 3\n'
                    'more 1 & more 2 & more 3\n'
                  '\\end{tabular}\n')
        self._test_token(block_token.Table, raw, target)

    def test_table_without_heading(self):
        raw = ['| cell 1 | cell 2 | cell 3 |\n',
                 '| more 1 | more 2 | more 3 |\n']
        target = ('\\begin{tabular}\n'
                    'cell 1 & cell 2 & cell 3\n'
                    'more 1 & more 2 & more 3\n'
                  '\\end{tabular}\n')
        self._test_token(block_token.Table, raw, target)

    def test_table_row(self):
        raw = '| cell 1 | cell 2 | cell 3 |\n'
        target = 'cell 1 & cell 2 & cell 3\n'
        self._test_token(block_token.TableRow, raw, target)

    def test_separator(self):
        raw, target = '***\n', '\\hrulefill\n'
        self._test_token(block_token.Separator, raw, target)

    def test_document(self):
        raw = ['a paragraph\n']
        target = ('\\documentclass{article}\n'
                  '\\usepackage{csquotes}\n'
                  '\\usepackage{hyperref}\n'
                  '\\usepackage{graphicx}\n'
                  '\\usepackage{listings}\n'
                  '\\usepackage[normalem]{ulem}\n'
                  '\\begin{document}\n'
                  '\n'
                  'a paragraph\n'
                  '\\end{document}\n')
        self._test_token(block_token.Document, raw, target)
