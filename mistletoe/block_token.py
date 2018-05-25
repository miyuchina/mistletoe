"""
Built-in block-level token classes.
"""

import re
import sys
from itertools import zip_longest
import mistletoe.block_tokenizer as tokenizer
import mistletoe.span_token as span_token

"""
Tokens to be included in the parsing process, in the order specified.
"""
__all__ = ['BlockCode', 'Heading', 'Quote', 'CodeFence', 'ThematicBreak',
           'List', 'Table', 'Footnote', 'Paragraph']


_root_node = None


def tokenize(lines, parent=None):
    """
    A wrapper around block_tokenizer.tokenize. Pass in all block-level
    token constructors as arguments to block_tokenizer.tokenize.

    Doing so (instead of importing block_token module in block_tokenizer)
    avoids cyclic dependency issues, and allows for future injections of
    custom token classes.

    _token_types variable is at the bottom of this module.

    See also: block_tokenizer.tokenize, span_token.tokenize_inner.
    """
    return tokenizer.tokenize(lines, _token_types, parent)


def add_token(token_cls, position=0):
    """
    Allows external manipulation of the parsing process.
    This function is usually called in BaseRenderer.__enter__.

    Arguments:
        token_cls (SpanToken): token to be included in the parsing process.
    """
    _token_types.insert(position, token_cls)


def remove_token(token_cls):
    """
    Allows external manipulation of the parsing process.
    This function is usually called in BaseRenderer.__exit__.

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


class BlockToken(object):
    """
    Base class for span-level tokens. Recursively parse inner tokens.

    Naming conventions:
        * lines denotes a list of (possibly unparsed) input lines, and is
          commonly used as the argument name for constructors.
        * self.children is a list with all the inner tokens (thus if a
          token has children attribute, it is not a leaf node; if a token
          calls span_token.tokenize_inner, it is the boundary between
          span-level tokens and block-level tokens);
        * match is a static method used by tokenize to check if line_buffer
          matches the current token. Every subclass of BlockToken must
          define a match function (see block_tokenizer.tokenize).

    Attributes:
        children (list): inner tokens.
    """
    def __init__(self, lines, tokenize_func):
        self.children = tokenize_func(lines)

    def __contains__(self, text):
        return any(text in child for child in self.children)
    
    @staticmethod
    def read(lines):
        line_buffer = [next(lines)]
        for line in lines:
            if line == '\n':
                break
            line_buffer.append(line)
        return line_buffer


class Document(BlockToken):
    """
    Document token.
    """
    def __init__(self, lines):
        if isinstance(lines, str):
            lines = lines.splitlines(keepends=True)
        self.footnotes = {}
        global _root_node
        _root_node = self
        self.children = tokenize(lines)
        _root_node = None


class Heading(BlockToken):
    """
    Heading token. (["### some heading ###\n"])
    Boundary between span-level and block-level tokens.

    Attributes:
        level (int): heading level.
        children (list): inner tokens.
    """
    pattern = re.compile(r' {0,3}(#{1,6})(?:\n| +?(.*?)(?:\n| +?#+ *?$))')
    level = 0
    content = ''
    def __init__(self, _):
        self.level = self.__class__.level
        content = self.__class__.content
        super().__init__(content, span_token.tokenize_inner)

    @classmethod
    def start(cls, line):
        match_obj = cls.pattern.match(line)
        if match_obj is None:
            return False
        cls.level = len(match_obj.group(1))
        cls.content = (match_obj.group(2) or '').strip()
        if set(cls.content) == {'#'}:
            cls.content = ''
        return True

    @staticmethod
    def read(lines):
        return [next(lines)]

class SetextHeading(BlockToken):
    def __init__(self, lines):
        self.level = 1 if lines.pop().lstrip().startswith('=') else 2
        content = '\n'.join([line.strip() for line in lines])
        super().__init__(content, span_token.tokenize_inner)

    @classmethod
    def start(cls, line):
        raise NotImplementedError()

    @classmethod
    def read(cls, lines):
        raise NotImplementedError()


class Quote(BlockToken):
    """
    Quote token. (["> # heading\n", "> paragraph\n"])
    """
    def __init__(self, lines):
        super().__init__(lines, tokenize)

    @staticmethod
    def start(line):
        stripped = line.lstrip(' ')
        if len(line) - len(stripped) > 3:
            return False
        return stripped.startswith('>')

    @staticmethod
    def read(lines):
        line_buffer = []
        next_line = lines.peek()
        while next_line is not None:
            if (next_line.strip() == ''
                    or BlockCode.start(next_line)
                    or Heading.start(next_line)
                    or CodeFence.start(next_line)
                    or ThematicBreak.start(next_line)
                    or List.start(next_line)):
                break
            stripped = next(lines).lstrip()
            prepend = 0
            if stripped[0] == '>':
                prepend += 1
                if stripped[1] == ' ':
                    prepend += 1
            line_buffer.append(stripped[prepend:])
            next_line = lines.peek()
        return line_buffer


class Paragraph(BlockToken):
    """
    Paragraph token. (["some\n", "continuous\n", "lines\n"])
    Boundary between span-level and block-level tokens.
    """
    setext_pattern = re.compile(r' {0,3}(=|-)+ *$')

    def __new__(cls, lines):
        if not isinstance(lines, list):
            return lines
        return super().__new__(cls)

    def __init__(self, lines):
        content = ''.join([line.lstrip() for line in lines]).strip()
        super().__init__(content, span_token.tokenize_inner)

    @staticmethod
    def start(line):
        return line.strip() != ''

    @classmethod
    def read(cls, lines):
        line_buffer = [next(lines)]
        next_line = lines.peek()
        while (next_line is not None
                and next_line.strip() != ''
                and not Heading.start(next_line)
                and not CodeFence.start(next_line)
                and not Quote.start(next_line)
                and not List.start(next_line)):
            if cls.is_setext_heading(next_line):
                line_buffer.append(next(lines))
                return SetextHeading(line_buffer)
            if ThematicBreak.start(next_line):
                break
            line_buffer.append(next(lines))
            next_line = lines.peek()
        return line_buffer

    @classmethod
    def is_setext_heading(cls, line):
        return cls.setext_pattern.match(line)


class BlockCode(BlockToken):
    def __init__(self, lines):
        self.language = ''
        self.children = (span_token.RawText(''.join(lines)),)

    @staticmethod
    def start(line):
        return line.startswith('    ')

    @staticmethod
    def read(lines):
        line_buffer = []
        for line in lines:
            if line.strip() == '':
                line_buffer.append(line.lstrip(' ') if len(line) < 5 else line[4:])
                continue
            if not line.startswith('    '):
                lines.backstep()
                break
            line_buffer.append(line[4:])
        return line_buffer


class CodeFence(BlockToken):
    """
    Code fence. (["```sh\n", "rm -rf /", ..., "```"])
    Boundary between span-level and block-level tokens.

    Attributes:
        children (iterator): contains a single span_token.RawText token.
        language (str): language of code block (default to empty).
    """
    pattern = re.compile(r'( {0,3})((?:`|~){3,}) *(\S*)')
    _open_info = None
    def __init__(self, lines):
        self.language = self.__class__._open_info[2]
        self.children = (span_token.RawText(''.join(lines)),)
        self.__class__._open_info = None

    @classmethod
    def start(cls, line):
        match_obj = cls.pattern.match(line)
        if not match_obj:
            return False
        prepend, leader, lang = match_obj.groups()
        if leader[0] in lang or leader[0] in line[match_obj.end():]:
            return False
        cls._open_info = len(prepend), leader, lang
        return True

    @classmethod
    def read(cls, lines):
        next(lines)
        line_buffer = []
        for line in lines:
            stripped_line = line.lstrip(' ')
            diff = len(line) - len(stripped_line)
            if (stripped_line.startswith(cls._open_info[1])
                    and len(stripped_line.split(maxsplit=1)) == 1
                    and diff < 4):
                break
            if diff > cls._open_info[0]:
                stripped_line = ' ' * (diff - cls._open_info[0]) + stripped_line
            line_buffer.append(stripped_line)
        return line_buffer


class List(BlockToken):
    def __init__(self, items):
        self.children, self.loose = items
        leader = self.children[0].leader
        self.start = None
        if len(leader) != 1:
            self.start = int(leader[:-1])

    @classmethod
    def start(cls, line):
        return ListItem.parse_marker(line)

    @classmethod
    def read(cls, lines):
        loose = False
        leader = None
        item_buffer = []
        while True:
            while lines.peek() == '\n':
                next(lines)
            output = ListItem.read(lines)
            if output is None:
                break
            item = ListItem(*output)
            if leader is None:
                leader = item.leader
            elif not cls.same_marker_type(leader, item.leader):
                lines.reset()
                break
            loose |= item.loose
            item_buffer.append(item)
        return item_buffer, loose

    @staticmethod
    def same_marker_type(leader, other):
        if len(leader) == 1:
            return leader == other
        return leader[:-1].isdigit() and other[:-1].isdigit() and leader[-1] == other[-1]


class ListItem(BlockToken):
    pattern = re.compile(r' {0,3}(\d{1,9}[.)]|[+\-*]) {1,4}')

    def __init__(self, lines, prepend, leader):
        self.leader = leader
        self.prepend = prepend
        lines[0] = lines[0][prepend:]
        self.loose = False
        self.children = tokenize(lines, parent=self)

    @staticmethod
    def in_continuation(line, prepend):
        return len(line) - len(line.lstrip()) >= prepend

    @staticmethod
    def other_token(line):
        return (Heading.start(line)
                or Quote.start(line)
                or Heading.start(line)
                or CodeFence.start(line)
                or ThematicBreak.start(line))

    @classmethod
    def parse_marker(cls, line, prepend=-1, leader=None):
        """
        Returns a pair (prepend, leader) iff:

          - the line has a valid leader, and
          - the line is not a sublist of a previous list item
        """
        match_obj = cls.pattern.match(line)
        if match_obj is None:
            return None        # no valid leader
        content = match_obj.group(0)
        if prepend != -1 and len(content) - len(content.lstrip()) >= prepend:
            return None        # is sublist
        # reassign prepend and leader
        prepend = len(content)
        leader = match_obj.group(1)
        return prepend, leader

    @classmethod
    def read(cls, lines):
        lines.anchor()
        prepend = -1
        leader = None
        newline = False
        line_buffer = []
        next_line = lines.peek()
        # first line in list item
        if next_line is None or cls.other_token(next_line):
            return None
        pair = cls.parse_marker(next_line)
        if pair is None:
            return None
        prepend, leader = pair
        line_buffer.append(next(lines))
        next_line = lines.peek()
        while (next_line is not None
                and not cls.other_token(next_line)
                and not cls.parse_marker(next_line, prepend, leader)
                and (not newline or cls.in_continuation(next_line, prepend))):
            line = next(lines)
            stripped = line.lstrip(' ')
            diff = len(line) - len(stripped)
            if diff > prepend:
                stripped = ' ' * (diff - prepend) + stripped
            line_buffer.append(stripped)
            newline = next_line.strip() == ''
            next_line = lines.peek()
        return line_buffer, prepend, leader


class Table(BlockToken):
    """
    Table token.

    Attributes:
        has_header (bool): whether table has header row.
        column_align (list): align options for each column (default to [None]).
        children (list): inner tokens (TableRows).
    """
    def __init__(self, lines):
        if '---' in lines[1]:
            self.column_align = [self.parse_align(column)
                    for column in self.split_delimiter(lines[1])]
            self.header = TableRow(lines[0], self.column_align)
            self.children = [TableRow(line, self.column_align) for line in lines[2:]]
        else:
            self.column_align = [None]
            self.children = [TableRow(line) for line in lines]

    @staticmethod
    def split_delimiter(delimiter):
        """
        Helper function; returns a list of align options.

        Args:
            delimiter (str): e.g.: "| :--- | :---: | ---: |\n"

        Returns:
            a list of align options (None, 0 or 1).
        """
        return re.findall(r':?---+:?', delimiter)

    @staticmethod
    def parse_align(column):
        """
        Helper function; returns align option from cell content.

        Returns:
            None if align = left;
            0    if align = center;
            1    if align = right.
        """
        return (0 if column[0] == ':' else 1) if column[-1] == ':' else None

    @staticmethod
    def start(line):
        return '|' in line

    @staticmethod
    def read(lines):
        lines.anchor()
        line_buffer = [next(lines)]
        while lines.peek() is not None and '|' in lines.peek():
            line_buffer.append(next(lines))
        if len(line_buffer) < 2 or '---' not in line_buffer[1]:
            lines.reset()
            return None
        return line_buffer


class TableRow(BlockToken):
    """
    Table row token.

    Should only be called by Table.__init__().
    """
    def __init__(self, line, row_align=None):
        self.row_align = row_align or [None]
        cells = filter(None, line.strip().split('|'))
        self.children = [TableCell(cell.strip(), align)
                         for cell, align in zip_longest(cells, self.row_align)]


class TableCell(BlockToken):
    """
    Table cell token.
    Boundary between span-level and block-level tokens.

    Should only be called by TableRow.__init__().

    Attributes:
        align (bool): align option for current cell (default to None).
        children (list): inner (span-)tokens.
    """
    def __init__(self, content, align=None):
        self.align = align
        super().__init__(content, span_token.tokenize_inner)


class Footnote(BlockToken):
    """
    Footnote tokens.
    A collection of footnote entries.

    Attributes:
        children (list): footnote entry tokens.
    """
    def __new__(cls, lines):
        for line in lines:
            key, value = line.strip().split(']:')
            key = key[1:].casefold()
            value = value.strip()
            _root_node.footnotes[key] = value
        return None

    @classmethod
    def _is_legal(cls, line):
        return line.strip().startswith('[') and ']:' in line

    @classmethod
    def start(cls, line):
        return cls._is_legal(line)

    @classmethod
    def read(cls, lines):
        line_buffer = [next(lines)]
        while (lines.peek() is not None
                and cls._is_legal(lines.peek())
                and lines.peek() != '\n'):
            line_buffer.append(next(lines))
        return line_buffer


class ThematicBreak(BlockToken):
    """
    Thematic break token (a.k.a. horizontal rule.)
    """
    pattern = re.compile(r' {0,3}(?:([-_*]) *?)(?:\1 *?){2,}$')
    def __init__(self, _):
        pass

    @classmethod
    def start(cls, line):
        return cls.pattern.match(line)

    @staticmethod
    def read(lines):
        return [next(lines)]


_token_types = []
reset_tokens()

