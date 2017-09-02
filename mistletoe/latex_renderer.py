"""
LaTeX renderer for mistletoe.
"""

from itertools import chain
import mistletoe.latex_token as latex_token
from mistletoe.base_renderer import BaseRenderer

class LaTeXRenderer(BaseRenderer):
    def __init__(self, *extras):
        """
        Args:
            extras (list): allows subclasses to add even more custom tokens.
        """
        tokens = self._tokens_from_module(latex_token)
        super().__init__(*chain(tokens, extras))

    def render_strong(self, token):
        return '\\textbf{{{}}}'.format(self.render_inner(token))

    def render_emphasis(self, token):
        return '\\textit{{{}}}'.format(self.render_inner(token))

    def render_inline_code(self, token):
        return '\\verb|{}|'.format(self.render_inner(token))

    def render_strikethrough(self, token):
        return '\\sout{{{}}}'.format(self.render_inner(token))

    @staticmethod
    def render_image(token):
        return '\n\\includegraphics{{{}}}\n'.format(token.src)

    def render_footnote_image(self, token):
        maybe_src = self.footnotes.get(token.src.key, '')
        src = maybe_src.split(' "', 1)[0]
        return '\n\\includegraphics{{{}}}\n'.format(src)

    def render_link(self, token):
        template = '\\href{{{target}}}{{{inner}}}'
        inner = self.render_inner(token)
        return template.format(target=token.target, inner=inner)

    def render_footnote_link(self, token):
        template = '\\href{{{target}}}{{{inner}}}'
        inner = self.render_inner(token)
        target = self.footnotes.get(token.target.key, '')
        return template.format(target=target, inner=inner)

    @staticmethod
    def render_auto_link(token):
        return '\\url{{{}}}'.format(token.target)

    @staticmethod
    def render_math(token):
        return token.content

    def render_escape_sequence(self, token):
        return self.render_inner(token)

    @staticmethod
    def render_raw_text(token):
        return (token.content.replace('$', '\$').replace('#', '\#')
                             .replace('{', '\{').replace('}', '\}')
                             .replace('&', '\&'))

    def render_heading(self, token):
        inner = self.render_inner(token)
        if token.level == 1:
            return '\n\\section{{{}}}\n'.format(inner)
        elif token.level == 2:
            return '\n\\subsection{{{}}}\n'.format(inner)
        return '\n\\subsubsection{{{}}}\n'.format(inner)

    def render_quote(self, token):
        template = '\\begin{{displayquote}}\n{inner}\\end{{displayquote}}\n'
        return template.format(inner=self.render_inner(token))

    def render_paragraph(self, token):
        return '\n{}\n'.format(self.render_inner(token))

    def render_block_code(self, token):
        template = ('\n\\begin{{lstlisting}}[language={}]\n'
                    '{}'
                    '\\end{{lstlisting}}\n')
        inner = self.render_inner(token)
        return template.format(token.language, inner)

    def render_list(self, token):
        template = '\\begin{{{tag}}}\n{inner}\\end{{{tag}}}\n'
        tag = 'enumerate' if token.start is not None else 'itemize'
        inner = self.render_inner(token)
        return template.format(tag=tag, inner=inner)

    def render_list_item(self, token):
        inner = self.render_inner(token)
        return '\\item {}\n'.format(inner)

    def render_table(self, token):
        def render_align(column_align):
            if column_align != [None]:
                cols = [get_align(col) for col in token.column_align]
                return '{{{}}}'.format(' '.join(cols))
            else:
                return ''

        def get_align(col):
            if col is None:
                return 'l'
            elif col == 0:
                return 'c'
            elif col == 1:
                return 'r'
            raise RuntimeError('Unrecognized align option: ' + col)

        template = ('\\begin{{tabular}}{align}\n'
                    '{inner}'
                    '\\end{{tabular}}\n')
        if token.has_header:
            head_template = '{inner}\\hline\n'
            header = next(token.children)
            head_inner = self.render_table_row(header)
            head_rendered = head_template.format(inner=head_inner)
        else: head_rendered = ''
        inner = self.render_inner(token)
        align = render_align(token.column_align)
        return template.format(inner=head_rendered+inner, align=align)

    def render_table_row(self, token):
        cells = [self.render(child) for child in token.children]
        return ' & '.join(cells) + '\n'

    def render_table_cell(self, token):
        return self.render_inner(token)

    @staticmethod
    def render_separator(token):
        return '\\hrulefill\n'

    def render_document(self, token):
        # I probably should import those packages iff the document
        # is actually using them... oh well.
        template = ('\\documentclass{{article}}\n'
                    '\\usepackage{{csquotes}}\n'
                    '\\usepackage{{hyperref}}\n'
                    '\\usepackage{{graphicx}}\n'
                    '\\usepackage{{listings}}\n'
                    '\\usepackage[normalem]{{ulem}}\n'
                    '\\begin{{document}}\n'
                    '{inner}'
                    '\\end{{document}}\n')
        self.footnotes.update(token.footnotes)
        return template.format(inner=self.render_inner(token))
