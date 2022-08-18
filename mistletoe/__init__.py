"""
Make mistletoe easier to import.
"""

__version__ = "0.9.0"
__all__ = ['html_renderer', 'ast_renderer', 'block_token', 'block_tokenizer',
           'span_token', 'span_tokenizer']

from mistletoe.block_token import Document
from mistletoe.html_renderer import HTMLRenderer

def markdown(iterable, renderer=HTMLRenderer):
    """
    Converts markdown input to the output supported by the given renderer.
    If no renderer is supplied, ``HTMLRenderer`` is used.

    Note that extra token types supported by the given renderer
    are automatically (and temporarily) added to the parsing process.
    """
    with renderer() as renderer:
        return renderer.render(Document(iterable))
