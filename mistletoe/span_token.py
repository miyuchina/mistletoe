"""
Built-in span-level token classes.
"""

import re
from types import GeneratorType
import mistletoe.span_tokenizer as tokenizer

"""
Tokens to be included in the parsing process, in the order specified.
"""
__all__ = ['EscapeSequence', 'Emphasis', 'Strong', 'InlineCode',
           'Strikethrough', 'Image', 'FootnoteImage', 'Link',
           'FootnoteLink', 'AutoLink', 'LineBreak', 'RawText']


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


def _first_not_none_group(match_obj):
    return next(group for group in match_obj.groups() if group is not None)


class SpanToken(object):
    """
    Base class for span-level tokens. Recursively parse inner tokens.

    Naming conventions:
        * match_obj is passed in from span_tokenizer.tokenize, and contains
          user input.
        * self.children is (usually) a list with all the inner tokens
          (thus if a token has children attribute, it is not a leaf node);
        * self.content denotes string stored (and later rendered) as-is,
          without need for extra parsing (thus if a token has content
          attribute, it is a leaf node).
        * pattern is a class variable (regex pattern) used by tokenize_inner
          to search for the next token. Match groups are available for easier
          separation of different components of the input. Every subclass of
          SpanToken must define its pattern (see span_tokenizer.tokenize),
          except RawText.

    Attributes:
        children (list): inner tokens.
    """
    def __init__(self, match_obj):
        self.children = tokenize_inner(match_obj.group(1))

    def __contains__(self, text):
        if hasattr(self, 'children'):
            return any(text in child for child in self.children)
        else:
            return text in self.content


class Strong(SpanToken):
    """
    Strong tokens. ("**some text**")
    """
    pattern = re.compile(r"\*\*([^\s*].*?)\*\*|\b__([^\s_].*?)__\b", re.DOTALL)
    def __init__(self, match_obj):
        self.children = tokenize_inner(_first_not_none_group(match_obj))


class Emphasis(SpanToken):
    """
    Emphasis tokens. ("*some text*")
    """
    pattern = re.compile(r"\*([^\s*].*?)\*|\b_([^\s_].*?)_\b", re.DOTALL)
    def __init__(self, match_obj):
        self.children = tokenize_inner(_first_not_none_group(match_obj))


class InlineCode(SpanToken):
    """
    Inline code tokens. ("`some code`")
    """
    pattern = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.DOTALL)
    def __init__(self, match_obj):
        self.children = (RawText(' '.join(match_obj.group(2).split())),)


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
    pattern = re.compile(r'\!\[(.*?)\]\s*\((.+?)(?:\s*\"(.+?)\")?\)', re.DOTALL)
    def __init__(self, match_obj):
        self.children = (RawText(match_obj.group(1)),)
        self.src = match_obj.group(2)
        self.title = match_obj.group(3)


class FootnoteImage(SpanToken):
    """
    Footnote image tokens. ("![alt] [some key]")

    Attributes:
        children (iterator): a single RawText node for alternative text.
        src (FootnoteAnchor): could point to both src and title.
    """
    pattern = re.compile(r"\!\[(.*?)\]\s*?\[(.+?)\]", re.DOTALL)
    def __init__(self, match_obj):
        self.children = (RawText(match_obj.group(1)),)
        self.src = FootnoteAnchor(match_obj.group(2))


class Link(SpanToken):
    """
    Link tokens. ("[name](target)")

    Attributes:
        children (list): link name still needs further parsing.
        target (str): link target.
    """
    pattern = re.compile(r"\[((?:!\[(?:.+?)\][\[\(](?:.+?)[\)\]])|(?:.+?))\]\s*?\((\S+)\)", re.DOTALL)
    def __init__(self, match_obj):
        super().__init__(match_obj)
        self.target = match_obj.group(2)


class FootnoteLink(SpanToken):
    """
    Footnote-style links. ("[name] [some target]")

    Attributes:
        children (list): link name still needs further parsing.
        target (FootnoteAnchor): to be looked up when rendered.
    """
    pattern = re.compile(r"\[((?:!\[(?:.+?)\][\[\(](?:.+?)[\)\]])|(?:.+?))\](?:\s*?\[(.+?)\])?", re.DOTALL)
    def __init__(self, match_obj):
        super().__init__(match_obj)
        self.target = FootnoteAnchor(match_obj.group(2) or match_obj.group(1))


class AutoLink(SpanToken):
    """
    Autolink tokens. ("<http://www.google.com>")

    Attributes:
        children (iterator): a single RawText node for alternative text.
        target (str): link target.
    """
    pattern = re.compile(r"<([A-Za-z][A-Za-z0-9+.-]{1,31}:[^ <>]*?|[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)*)>")
    def __init__(self, match_obj):
        self.children = (RawText(match_obj.group(1)),)
        self.target = match_obj.group(1)
        self.mailto = '@' in self.target and 'mailto' not in self.target.casefold()


class EscapeSequence(SpanToken):
    """
    Escape sequences. ("\*")

    Attributes:
        children (iterator): a single RawText node for alternative text.
    """
    pattern = re.compile(r"\\([!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~])")
    def __init__(self, match_obj):
        self.children = (RawText(match_obj.group(1)),)


class LineBreak(SpanToken):
    """
    Hard line breaks. Two spaces at the end of a line, or a backslash.
    """
    pattern = re.compile(r'(?: {2,}|\\)\n')
    def __init__(self, _):
        self.content = ''


class RawText(SpanToken):
    """
    Raw text. A leaf node.

    RawText is the only token that accepts a string for its constructor,
    instead of a match object. Also, all recursions should bottom out here.
    """
    def __init__(self, raw):
        self.content = raw


class FootnoteAnchor(SpanToken):
    """
    Footnote anchor.
    To be replaced at render time.
    """
    def __init__(self, raw):
        self.key = raw

_token_types = []
reset_tokens()

