from mistletoe.base_renderer import BaseRenderer
from mistletoe import block_token, span_token


class MarkdownRenderer(BaseRenderer):
    def __init__(self, *extras,
                 enabled_block_tokens=None, enabled_span_tokens=None):
        super().__init__(*extras)
        self.all_block_tokens = block_token._token_types[:]
        self.all_span_tokens = span_token._token_types[:]
        self.enabled_block_tokens = enabled_block_tokens or []
        self.enabled_span_tokens = enabled_span_tokens or []
        block_token._token_types = self.enabled_block_tokens
        span_token._token_types = self.enabled_span_tokens

    def __exit__(self, exception_type, exception_val, traceback):
        block_token._token_types = self.all_block_tokens[:]
        span_token._token_types = self.all_span_tokens[:]

    def render_raw_text(self, token):
        return token.content

    def render_paragraph(self, token):
        return '{}\n'.format(self.render_inner(token))

    def render_document(self, token):
        return self.render_inner(token)

    def __getattr__(self, name):
        return lambda token: NotImplemented
