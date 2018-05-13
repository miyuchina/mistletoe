"""
Make mistletoe easier to import.
"""

__version__ = "0.6.2"
__all__ = ['html_renderer', 'ast_renderer', 'block_token', 'block_tokenizer',
           'span_token', 'span_tokenizer']

from mistletoe.block_token import Document
from mistletoe.base_renderer import BaseRenderer
from mistletoe.html_renderer import HTMLRenderer

def markdown(iterable, renderer=HTMLRenderer):
    """
    Output HTML with default settings.
    Enables inline and block-level HTML tags.
    """
    with renderer() as renderer:
        return renderer.render(Document(iterable))
