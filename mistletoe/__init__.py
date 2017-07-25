"""
Make mistletoe easier to import.
"""

__all__ = ['html_renderer', 'ast_renderer', 'block_token', 'block_tokenizer',
           'span_token', 'span_tokenizer']

from mistletoe.block_token import Document

def markdown(iterable):
    """
    Output HTML with default settings.
    Enables inline and block-level HTML tags.
    """
    from mistletoe.html_token import Context
    from mistletoe.html_renderer import render
    with Context(): # span_token.HTMLSpan, block_token.HTMLBlock
        return render(Document(iterable))
