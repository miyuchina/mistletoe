"""
Provides MathJax support for rendering Markdown with LaTeX to html.
"""

from mistletoe.html_renderer import HtmlRenderer
from mistletoe.latex_renderer import LaTeXRenderer


class MathJaxRenderer(HtmlRenderer, LaTeXRenderer):
    def __init__(self, **kwargs):
        """
        Args:
            **kwargs: additional parameters to be passed to the ancestors'
                      constructors.
        """
        super().__init__(**kwargs)

    mathjax_src = '<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.0/MathJax.js?config=TeX-MML-AM_CHTML"></script>\n'

    def render_math(self, token):
        """
        Convert single dollar sign enclosed math expressions to the ``\\(...\\)`` syntax, to support
        the default MathJax settings which ignore single dollar signs as described at
        https://docs.mathjax.org/en/latest/basic/mathematics.html#tex-and-latex-input.
        """
        if token.content.startswith('$$'):
            return self.render_raw_text(token)
        return '\\({}\\)'.format(self.render_raw_text(token).strip('$'))

    def render_document(self, token):
        """
        Append CDN link for MathJax to the end of <body>.
        """
        return super().render_document(token) + self.mathjax_src
