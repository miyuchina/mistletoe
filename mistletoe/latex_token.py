import re
import mistletoe.span_token as span_token

__all__ = ['Math']

class Math(span_token.SpanToken):
    pattern = re.compile(r'((\${1,2})([^$]+?)\2)')

    def __init__(self, raw):
        self.content = raw
