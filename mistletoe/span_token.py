"""
Built-in span-level token classes.
"""

import re
from types import GeneratorType
import mistletoe.span_tokenizer as tokenizer
from mistletoe.core_tokens import find_core_tokens

"""
Tokens to be included in the parsing process, in the order specified.
"""
__all__ = ['EscapeSequence', 'InlineCode', 'Strikethrough',
           'AutoLink', 'CoreTokens', 'LineBreak', 'RawText']


def tokenize_inner(content):
    """
    A wrapper around span_tokenizer.tokenize. Pass in all span-level token
    constructors as arguments to span_tokenizer.tokenize.

    Doing so (instead of importing span_token module in span_tokenizer)
    avoids cyclic dependency issues, and allows for future injections of
    custom token classes.

    _token_types variable is at the bottom of this module.

    See also: span_tokenizer.tokenize, block_token.tokenize.
    """
    return tokenizer.tokenize(content, _token_types)


def add_token(token_cls, position=1):
    """
    Allows external manipulation of the parsing process.
    This function is called in BaseRenderer.__enter__.

    Arguments:
        token_cls (SpanToken): token to be included in the parsing process.
    """
    _token_types.insert(position, token_cls)


def remove_token(token_cls):
    """
    Allows external manipulation of the parsing process.
    This function is called in BaseRenderer.__exit__.

    Arguments:
        token_cls (SpanToken): token to be removed from the parsing process.
    """
    _token_types.remove(token_cls)


def reset_tokens():
    """
    Returns a list of tokens with the original tokens.
    """
    global _token_types
    _token_types = [globals()[cls_name] for cls_name in __all__]


class SpanToken:
    parse_inner = True
    parse_group = 1
    precedence = 5

    def __init__(self, match):
        if not self.parse_inner:
            self.content = match.group(self.parse_group)

    def __contains__(self, text):
        if hasattr(self, 'children'):
            return any(text in child for child in self.children)
        return text in self.content

    @classmethod
    def find(cls, string):
        return cls.pattern.finditer(string)


class CoreTokens(SpanToken):
    precedence = 3
    def __new__(self, match):
        return globals()[match.type](match)

    find = find_core_tokens


class Strong(SpanToken):
    """
    Strong tokens. ("**some text**")
    """


class Emphasis(SpanToken):
    """
    Emphasis tokens. ("*some text*")
    """


class InlineCode(SpanToken):
    """
    Inline code tokens. ("`some code`")
    """
    pattern = re.compile(r"(?<!\\|`)(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.DOTALL)
    parse_inner = False
    parse_group = 2

    def __init__(self, match):
        content = match.group(self.parse_group)
        self.children = (RawText(' '.join(content.split())),)


class Strikethrough(SpanToken):
    """
    Strikethrough tokens. ("~~some text~~")
    """
    pattern = re.compile(r"~~(.+)~~", re.DOTALL)


class Image(SpanToken):
    """
    Image tokens. ("![alt](src "title")")

    Attributes:
        children (iterator): a single RawText node for alternative text.
        src (str): image source.
        title (str): image title (default to empty).
    """
    def __init__(self, match):
        self.src = match.group(2).strip()
        self.title = match.group(3)


class FootnoteImage(SpanToken):
    """
    Footnote image tokens. ("![alt][some key]")

    Attributes:
        children (iterator): a single RawText node for alternative text.
        src (FootnoteAnchor): could point to both src and title.
    """
    def __init__(self, match):
        self.src = FootnoteAnchor(match.group(2) or match.group(1))


class Link(SpanToken):
    """
    Link tokens. ("[name](target)")

    Attributes:
        children (list): link name still needs further parsing.
        target (str): link target.
    """
    def __init__(self, match):
        self.target = EscapeSequence.strip(match.group(2).strip())
        self.title = EscapeSequence.strip(match.group(3))


class FootnoteLink(SpanToken):
    """
    Footnote-style links. ("[name] [some target]")

    Attributes:
        children (list): link name still needs further parsing.
        target (FootnoteAnchor): to be looked up when rendered.
    """
    def __init__(self, match):
        self.target = FootnoteAnchor(match.group(2) or match.group(1))


class AutoLink(SpanToken):
    """
    Autolink tokens. ("<http://www.google.com>")

    Attributes:
        children (iterator): a single RawText node for alternative text.
        target (str): link target.
    """
    pattern = re.compile(r"<([A-Za-z][A-Za-z0-9+.-]{1,31}:[^ <>]*?|[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)*)>")
    parse_inner = False

    def __init__(self, match):
        content = match.group(self.parse_group)
        self.children = (RawText(content),)
        self.target = content
        self.mailto = '@' in self.target and 'mailto' not in self.target.casefold()


class EscapeSequence(SpanToken):
    """
    Escape sequences. ("\*")

    Attributes:
        children (iterator): a single RawText node for alternative text.
    """
    pattern = re.compile(r"\\([!\"#$%&'()*+,-./:;<=>?@\[\\\]^_`{|}~])")
    parse_inner = False
    precedence = 2

    def __init__(self, match):
        self.children = (RawText(match.group(self.parse_group)),)

    @classmethod
    def strip(cls, string):
        return cls.pattern.sub(r'\1', string)


class LineBreak(SpanToken):
    """
    Hard line breaks. Two spaces at the end of a line, or a backslash.
    """
    pattern = re.compile(r'(?: {2,}|\\)\n')
    parse_inner = False
    parse_group = 0

    def __init__(self, _):
        self.content = ''


class RawText(SpanToken):
    """
    Raw text. A leaf node.

    RawText is the only token that accepts a string for its constructor,
    instead of a match object. Also, all recursions should bottom out here.
    """
    def __init__(self, content):
        self.content = content


class FootnoteAnchor(SpanToken):
    """
    Footnote anchor.
    To be replaced at render time.
    """
    def __init__(self, raw):
        self.key = raw.casefold()


_token_types = []
reset_tokens()

