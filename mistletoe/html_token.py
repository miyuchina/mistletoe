"""
Mixin HTML tags support for mistletoe.
"""

import re
import mistletoe.span_token as span_token
import mistletoe.block_token as block_token

__all__ = ['HTMLBlock', 'HTMLSpan']

class Context(object):
    """
    Context manager for HTMLBlock and HTMLSpan token injections.

    Essentially it allows you to do this:

        >>> from html_token import Context
        >>> span_token.HTMLSpan
        AttributeError: module 'span_token' has no attribute 'HTMLSpan'
        >>> with Context():
        ...     span_token.HTMLSpan
        <class 'html_token.HTMLSpan'>
        >>> span_token.HTMLSpan
        AttributeError: module 'span_token' has no attribute 'HTMLSpan'

    ... which is significantly cleaner than if one were to inject
    them manually every time.
    """
    def __enter__(self):
        # injecting attributes:
        span_token.HTMLSpan = HTMLSpan            
        block_token.HTMLBlock = HTMLBlock
        # ... which will be picked up by the tokenizer by:
        span_token.__all__.insert(0, 'HTMLSpan')
        block_token.__all__.insert(0, 'HTMLBlock')
        return self

    def __exit__(self, exception_type, exception_val, traceback):
        # clear up namespace
        del span_token.HTMLSpan
        del block_token.HTMLBlock
        # stop trying to match for these tokens
        span_token.__all__.pop(0)
        block_token.__all__.pop(0)

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
