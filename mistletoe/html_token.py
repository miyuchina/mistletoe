"""
Mixin HTML tags support for mistletoe.

Injection into the parsing process is achieved in the corresponding
renderer (mistletoe.html_renderer in this case.)
"""

import re
import mistletoe.span_token as span_token
import mistletoe.block_token as block_token


__all__ = ['HTMLBlock', 'HTMLSpan']


_tags = {'address', 'article', 'aside', 'base', 'basefont', 'blockquote',
        'body', 'caption', 'center', 'col', 'colgroup', 'dd', 'details',
        'dialog', 'dir', 'div', 'dl', 'dt', 'fieldset', 'figcaption', 'figure',
        'footer', 'form', 'frame', 'frameset', 'h1', 'h2', 'h3', 'h4', 'h5',
        'h6', 'head', 'header', 'hr', 'html', 'iframe', 'legend', 'li', 'link',
        'main', 'menu', 'menuitem', 'meta', 'nav', 'noframes', 'ol',
        'optgroup', 'option', 'p', 'param', 'section', 'source', 'summary',
        'table', 'tbody', 'td', 'tfoot', 'th', 'thead', 'title', 'tr', 'track', 'ul'}

_tag   = r'[A-Za-z][A-Za-z0-9-]*'
_attrs = r'(?:\s+[A-Za-z_:][A-Za-z0-9_.:-]*(?:\s*=\s*(?:[^ "\'=<>`]+|\'[^\']*?\'|"[^\"]*?"))?)*'

_open_tag    = r'<' + _tag + _attrs + r'\s*/?>'
_closing_tag = r'</' + _tag + r'\s*>'
_comment     = r'<!--(?!>|->)(?:(?!--).)+?(?<!-)-->'
_instruction = r'<\?.+?\?>'
_declaration = r'<![A-Z].+?>'
_cdata       = r'<!\[CDATA.+?\]\]>'


class HTMLBlock(block_token.BlockToken):
    """
    Block-level HTML tokens.

    Attributes:
        content (str): literal strings rendered as-is.
    """
    _end_cond = None
    multiblock = re.compile(r'<(script|pre|style)[ >\n]')
    predefined = re.compile(r'<\/?(.+?)(?:\/?>|[ \n])')
    custom_tag = re.compile(r'(?:' + '|'.join((_open_tag, _closing_tag)) + r')\s*$')
    def __init__(self, lines):
        self.content = ''.join(lines) # implicit newlines

    @classmethod
    def start(cls, line):
        stripped = line.lstrip()
        if len(line) - len(stripped) >= 4:
            return False
        # rule 1: <pre>, <script> or <style> tags, allow newlines in block
        match_obj = cls.multiblock.match(stripped)
        if match_obj is not None:
            cls._end_cond = '</{}>'.format(match_obj.group(1).casefold())
            return True
        # rule 2: html comment tags, allow newlines in block
        if stripped.startswith('<!--'):
            cls._end_cond = '-->'
            return True
        # rule 3: tags that starts with <?, allow newlines in block
        if stripped.startswith('<?'):
            cls._end_cond = '?>'
            return True
        # rule 4: tags that starts with <!, allow newlines in block
        if stripped.startswith('<!') and stripped[2].isupper():
            cls._end_cond = '>'
            return True
        # rule 5: CDATA declaration, allow newlines in block
        if stripped.startswith('<![CDATA['):
            cls._end_cond = ']]>'
            return True
        # rule 6: predefined tags (see html_token._tags), read until newline
        match_obj = cls.predefined.match(stripped)
        if match_obj is not None and match_obj.group(1).casefold() in _tags:
            cls._end_cond = None
            return True
        # rule 7: custom tags, read until newline
        match_obj = cls.custom_tag.match(stripped)
        if match_obj is not None:
            cls._end_cond = None
            return True
        return False

    @classmethod
    def read(cls, lines):
        # note: stop condition can trigger on the starting line
        line_buffer = []
        for line in lines:
            line_buffer.append(line)
            if cls._end_cond is not None:
                if cls._end_cond in line.casefold():
                    break
            elif line.strip() == '':
                break
        return line_buffer


class HTMLSpan(span_token.SpanToken):
    """
    Span-level HTML tokens.

    Attributes:
        content (str): literal strings rendered as-is.
    """
    pattern = re.compile('|'.join([_open_tag, _closing_tag, _comment,
                                   _instruction, _declaration, _cdata]),
                                   re.DOTALL)

    def __init__(self, match_obj):
        self.content = match_obj.group(0)
