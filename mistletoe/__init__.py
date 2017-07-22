__all__ = ['html_renderer', 'ast_renderer', 'block_token', 'block_tokenizer',
           'span_token', 'span_tokenizer']

from mistletoe.block_token import Document

def markdown(iterable):
    import mistletoe.html_token as token
    import mistletoe.html_renderer as renderer
    rendered = renderer.render(Document(iterable))
    token.clear()
    return rendered
