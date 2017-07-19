class LaTeXRenderer(object):
    def __init__(self):
        self.render_map = {
            'Strong':         self.render_strong,
            'Emphasis':       self.render_emphasis,
            'InlineCode':     self.render_inline_code,
            'RawText':        self.render_raw_text,
            'Strikethrough':  self.render_strikethrough,
            'Image':          self.render_image,
            'Link':           self.render_link,
            'EscapeSequence': self.render_raw_text,
            'Heading':        self.render_heading,
            'Quote':          self.render_quote,
            'Paragraph':      self.render_paragraph,
            'BlockCode':      self.render_block_code,
            'List':           self.render_list,
            'ListItem':       self.render_list_item,
            'Separator':      self.render_separator,
            'Document':       self.render_document,
            }

    def render(self, token):
        return self.render_map[type(token).__name__](token)

    def render_inner(self, token):
        return ''.join([self.render(child) for child in token.children])

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

    def render_link(self, token):
        template = '\\href{{{}}}{{{}}}'
        return template.format(token.target, self.render_inner(token))

    @staticmethod
    def render_raw_text(token):
        return token.content

    def render_heading(self, token):
        if token.level == 1:
            return '\n\\section{{{}}}\n'.format(self.render_inner(token))
        elif token.level == 2:
            return '\n\\subsection{{{}}}\n'.format(self.render_inner(token))
        return '\n\\subsubsection{{{}}}\n'.format(self.render_inner(token))

    def render_quote(self, token):
        template = '<blockquote>{inner}</blockquote>'
        return template.format(inner=self.render_inner(token))

    def render_paragraph(self, token):
        return '\n{}\n'.format(self.render_inner(token))

    def render_block_code(self, token):
        template = '\n\\begin{{lstlisting}}[language={}]\n{}\\end{{lstlisting}}\n'
        return template.format(token.language, self.render_inner(token))

    def render_list(self, token):
        template = '\\begin{{{tag}}}\n{inner}\\end{{{tag}}}\n'
        tag = 'enumerate' if hasattr(token, 'start') else 'itemize'
        inner = self.render_inner(token)
        return template.format(tag=tag, inner=inner)

    def render_list_item(self, token):
        return '\\item {}\n'.format(self.render_inner(token))

    @staticmethod
    def render_separator(token):
        return '\\hrulefill'

    def render_document(self, token):
        template = ('\\documentclass{{article}}\n'
                    '\\usepackage{{hyperref}}\n'
                    '\\usepackage{{graphicx}}\n'
                    '\\usepackage{{listings}}\n'
                    '\\usepackage[normalem]{{ulem}}\n'
                    '\\begin{{document}}\n'
                    '{inner}'
                    '\\end{{document}}\n')
        return template.format(inner=self.render_inner(token))
