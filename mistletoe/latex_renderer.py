"""
LaTeX renderer for mistletoe.
"""

import mistletoe.span_token as span_token
import mistletoe.latex_token as latex_token
from mistletoe.base_renderer import BaseRenderer

class LaTeXRenderer(BaseRenderer):
    def __enter__(self):
        span_token.Math = latex_token.Math
        span_token.__all__.insert(1, 'Math')
        self.render_map['Math'] = self.render_math
        return self

    def __exit__(self, exception_type, exception_val, traceback):
        del span_token.Math
        span_token.__all__.pop(1)
        del self.render_map['Math']

    def render_strong(self, token, footnotes):
        return '\\textbf{{{}}}'.format(self.render_inner(token, footnotes))

    def render_emphasis(self, token, footnotes):
        return '\\textit{{{}}}'.format(self.render_inner(token, footnotes))

    def render_inline_code(self, token, footnotes):
        return '\\verb|{}|'.format(self.render_inner(token, footnotes))

    def render_strikethrough(self, token, footnotes):
        return '\\sout{{{}}}'.format(self.render_inner(token, footnotes))

    @staticmethod
    def render_image(token, footnotes):
        return '\n\\includegraphics{{{}}}\n'.format(token.src)

    @staticmethod
    def render_footnote_image(token, footnotes):
        maybe_src = footnotes.get(token.src.key, '')
        src = maybe_src.split(' "', 1)[0]
        return '\n\\includegraphics{{{}}}\n'.format(src)

    def render_link(self, token, footnotes):
        template = '\\href{{{target}}}{{{inner}}}'
        inner = self.render_inner(token, footnotes)
        return template.format(target=token.target, inner=inner)

    def render_footnote_link(self, token, footnotes):
        template = '\\href{{{target}}}{{{inner}}}'
        inner = self.render_inner(token, footnotes)
        target = footnotes.get(token.target.key, '')
        return template.format(target=target, inner=inner)

    @staticmethod
    def render_auto_link(token, footnotes):
        return '\\url{{{}}}'.format(token.target)

    @staticmethod
    def render_math(token, footnotes):
        return token.content

    @staticmethod
    def render_raw_text(token, footnotes):
        return (token.content.replace('$', '\$').replace('#', '\#')
                             .replace('{', '\{').replace('}', '\}')
                             .replace('&', '\&'))

    def render_heading(self, token, footnotes):
        inner = self.render_inner(token, footnotes)
        if token.level == 1:
            return '\n\\section{{{}}}\n'.format(inner)
        elif token.level == 2:
            return '\n\\subsection{{{}}}\n'.format(inner)
        return '\n\\subsubsection{{{}}}\n'.format(inner)

    def render_quote(self, token, footnotes):
        template = '\\begin{{displayquote}}\n{inner}\\end{{displayquote}}\n'
        return template.format(inner=self.render_inner(token, footnotes))

    def render_paragraph(self, token, footnotes):
        return '\n{}\n'.format(self.render_inner(token, footnotes))

    def render_block_code(self, token, footnotes):
        template = ('\n\\begin{{lstlisting}}[language={}]\n'
                    '{}'
                    '\\end{{lstlisting}}\n')
        inner = self.render_inner(token, footnotes)
        return template.format(token.language, inner)

    def render_list(self, token, footnotes):
        template = '\\begin{{{tag}}}\n{inner}\\end{{{tag}}}\n'
        tag = 'enumerate' if hasattr(token, 'start') else 'itemize'
        inner = self.render_inner(token, footnotes)
        return template.format(tag=tag, inner=inner)

    def render_list_item(self, token, footnotes):
        inner = self.render_inner(token, footnotes)
        return '\\item {}\n'.format(inner)

    def render_table(self, token, footnotes):
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
            header = token.children.send(None)
            head_inner = self.render_table_row(header, footnotes)
            head_rendered = head_template.format(inner=head_inner)
        else: head_rendered = ''
        inner = self.render_inner(token, footnotes)
        align = render_align(token.column_align)
        return template.format(inner=head_rendered+inner, align=align)

    def render_table_row(self, token, footnotes):
        cells = [self.render(child, footnotes) for child in token.children]
        return ' & '.join(cells) + '\n'

    def render_table_cell(self, token, footnotes):
        return self.render_inner(token, footnotes)

    @staticmethod
    def render_separator(token, footnotes):
        return '\\hrulefill\n'

    def render_document(self, token, footnotes):
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
        inner = self.render_inner(token, token.footnotes)
        return template.format(inner=inner)
