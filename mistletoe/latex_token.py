import re
import mistletoe.span_token as span_token

class Math(span_token.SpanToken):
    pattern = re.compile(r'(\$(.+?)\$)')

    def __init__(self, raw):
        self.content = raw
