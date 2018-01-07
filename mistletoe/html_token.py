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
    _last_tag = ''
    def __init__(self, lines):
        self.content = ''.join(lines) # implicit newlines

    @classmethod
    def start(cls, line):
        open_tag_end = line.find('>')
        if not line.startswith('<') or open_tag_end == -1:
            return False
        if HTMLSpan.pattern.match(line.strip()):
            cls._last_tag = ''
        else:
            cls._last_tag = line[1:open_tag_end].split(' ')[0]
        return True

    @classmethod
    def read(cls, lines):
        if not cls._last_tag:
            return []
        line_buffer = []
        for line in lines:
            line_buffer.append(line)
            start = line.find('</')
            end = line[start:].find('>')
            if start != -1 and end != -1 and line[start+2:end] == cls._last_tag:
                break
        return line_buffer


class HTMLSpan(span_token.SpanToken):
    """
    Span-level HTML tokens.

    Attributes:
        content (str): literal strings rendered as-is.
    """
    pattern = re.compile(r"<([A-z0-9]+?)(?: .+?)?(?: ?/>|>.*?<\/\1>)")
    def __init__(self, match_obj):
        self.content = match_obj.group(0)
