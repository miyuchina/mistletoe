"""
Provides MathJax support for rendering Markdown with LaTeX to html.
"""

from mistletoe.html_renderer import HTMLRenderer
from mistletoe.latex_renderer import LaTeXRenderer

class MathJaxRenderer(HTMLRenderer, LaTeXRenderer):
    """
    MRO will first look for render functions under HTMLRenderer,
    then LaTeXRenderer.
    """
    mathjax_src = '<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.0/MathJax.js?config=TeX-MML-AM_CHTML"></script>\n'

    def __enter__(self):
        super().__enter__()                    # HTMLRenderer.__enter__
        super(HTMLRenderer, self).__enter__()  # LaTeXRenderer.__enter__
        return self

    def __exit__(self, *args):
        super().__exit__(*args)                   # HTMLRenderer.__exit__
        super(HTMLRenderer, self).__exit__(*args) # LaTeXRenderer.__exit__

    def render_math(self, token, footnotes):
        """
        Ensure Math tokens are all enclosed in two dollar signs.
        """
        if token.content.startswith('$$'):
            return self.render_raw_text(token, footnotes)
        return '${}$'.format(self.render_raw_text(token, footnotes))

    def render_document(self, token, footnotes):
        """
        Append CDN link for MathJax to the end of <body>.
        """
        output = super().render_document(token, footnotes)
        return output + self.mathjax_src
