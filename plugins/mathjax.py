from mistletoe.latex_token import Math
from mistletoe.html_renderer import HTMLRenderer
from mistletoe.latex_renderer import LaTeXRenderer

class MathJaxRenderer(HTMLRenderer, LaTeXRenderer):
    mathjax_src = '<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.0/MathJax.js?config=TeX-MML-AM_CHTML"></script>\n'

    def __enter__(self):
        super().__enter__()
        super(HTMLRenderer, self).__enter__()
        return self

    def __exit__(self, *args):
        super().__exit__(*args)
        super(HTMLRenderer, self).__exit__(*args)

    def render_math(self, token, footnotes):
        if token.content.startswith('$$'):
            return token.content
        return '${}$'.format(token.content)

    def render_document(self, token, footnotes):
        output = super().render_document(token, footnotes)
        return output + self.mathjax_src
