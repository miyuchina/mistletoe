__all__ = ['html_renderer', 'ast_renderer', 'block_token', 'block_tokenizer',
           'span_token', 'span_tokenizer']

from mistletoe.block_token import Document
from mistletoe.html_renderer import render

def markdown(iterable, render_func=render):
    return render_func(Document(iterable))
