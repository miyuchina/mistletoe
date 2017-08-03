"""
Mixin HTML tags support for mistletoe.

Injection into the parsing process is achieved in the corresponding
renderer (mistletoe.html_renderer in this case.)
"""

import re
import mistletoe.span_token as span_token
import mistletoe.block_token as block_token

__all__ = ['HTMLBlock', 'HTMLSpan']

class HTMLBlock(block_token.BlockToken):
    """
    Block-level HTML tokens.

    Attributes:
        content (str): literal strings rendered as-is.
    """
    def __init__(self, lines):
        self.content = ''.join(lines) # implicit newlines

    @staticmethod
    def match(lines):
        open_tag_end = lines[0].find('>')
        close_tag_start = lines[-1].find('</')
        if (not lines[0].strip().startswith('<')
            or open_tag_end == -1
            or close_tag_start == -1):
            return False
        open_tag = lines[0][1:open_tag_end].split(' ')[0]
        close_tag = lines[-1][close_tag_start+2:-2]
        if open_tag != close_tag:
            return False
        return True

class HTMLSpan(span_token.SpanToken):
    """
    Span-level HTML tokens.

    Attributes:
        content (str): literal strings rendered as-is.
    """
    pattern = re.compile(r"(<([A-z0-9]+)( .+)?>(.+)<\/\2>)")
    def __init__(self, content):
        self.content = content
