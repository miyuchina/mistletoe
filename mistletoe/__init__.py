__all__ = ['html_renderer', 'ast_renderer', 'block_token', 'block_tokenizer',
           'span_token', 'span_tokenizer']

from mistletoe.block_token import Document

def markdown(iterable):
    from mistletoe.html_token import Context
    from mistletoe.html_renderer import render
    with Context():
        rendered = render(Document(iterable))
        return rendered
