"""
Built-in block-level token classes.
"""

import re
from types import GeneratorType
from itertools import zip_longest
import mistletoe.block_tokenizer as tokenizer
import mistletoe.span_token as span_token


__all__ = ['Heading', 'Quote', 'BlockCode', 'Separator', 'List', 'Table',
           'FootnoteBlock', 'Paragraph']


def tokenize(lines, root=None):
    """
    A wrapper around block_tokenizer.tokenize. Pass in all block-level
    token constructors as arguments to block_tokenizer.tokenize.

    Doing so (instead of importing block_token module in block_tokenizer)
    avoids cyclic dependency issues, and allows for future injections of
    custom token classes.

    _token_types variable is at the bottom of this module.

    See also: block_tokenizer.tokenize, span_token.tokenize_inner.
    """
    return tokenizer.tokenize(lines, _token_types, root)


def add_token(token_cls, position=0):
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


class BlockToken(object):
    """
    Base class for span-level tokens. Recursively parse inner tokens.

    Naming conventions:
        * lines denotes a list of (possibly unparsed) input lines, and is
          commonly used as the argument name for constructors.
        * self.children is a tuple with all the inner tokens (thus if a
          token has children attribute, it is not a leaf node; if a token
          calls span_token.tokenize_inner, it is the boundary between
          span-level tokens and block-level tokens);
        * match is a static method used by tokenize to check if line_buffer
          matches the current token. Every subclass of BlockToken must
          define a match function (see block_tokenizer.tokenize).

    Attributes:
        children (tuple): inner tokens.
    """
    def __init__(self, lines, tokenize_func):
        self._children = tokenize_func(lines)

    def __contains__(self, text):
        return any(text in child for child in self.children)


    @property
    def children(self):
        """
        Actual children attribute.

        If self.children is never accessed, the generator is never actually
        run. This allows for lazy-parsing of the input, while still maintaining
        idempotent behavior for tokens.
        """
        if isinstance(self._children, GeneratorType):
            self._children = tuple(self._children)
        return self._children
    
    @staticmethod
    def read(lines):
        return until('\n', lines)


class Document(BlockToken):
    """
    Document token.
    """
    def __init__(self, lines):
        self.footnotes = {}
        # Document tokens have immediate access to first-level block tokens.
        # Useful for footnotes, etc.
        self._children = tuple(tokenize(lines, root=self))


class Heading(BlockToken):
    """
    Heading token. (["### some heading ###\n"])
    Boundary between span-level and block-level tokens.

    Attributes:
        level (int): heading level.
        children (tuple): inner tokens.
    """
    def __init__(self, lines):
        hashes, content = lines[0].split('# ', 1)
        content = content.split(' #', 1)[0].strip()
        self.level = len(hashes) + 1
        super().__init__(content, span_token.tokenize_inner)

    @staticmethod
    def start(line):
        return (line.startswith('#')
                and line.find('# ') != -1
                and len(line.split(' ', 1)[0]) <= 6)

    @staticmethod
    def read(line):
        return []

class SetextHeading(BlockToken):
    def __init__(self, lines):
        self.level = 1 if lines[-1].startswith('=') else 2
        content = ''.join(lines[:-1])
        super().__init__(content, span_token.tokenize_inner)

    @staticmethod
    def start(line):
        return line != '\n'

    @staticmethod
    def read(lines):
        line_buffer = []
        for line in lines:
            if line == '\n':
                break
            line_buffer.append(line)
            if line.startswith(('===', '---')):
                return line_buffer
        raise tokenizer.MismatchException(line_buffer)


class Quote(BlockToken):
    """
    Quote token. (["> # heading\n", "> paragraph\n"])
    """
    def __init__(self, lines):
        content = []
        for line in lines:
            if line.startswith('> '):
                content.append(line[2:])
            else:  # lazy continuation
                content.append(line)
        super().__init__(content, tokenize)

    @staticmethod
    def start(line):
        return line.startswith('> ')


class Paragraph(BlockToken):
    """
    Paragraph token. (["some\n", "continuous\n", "lines\n"])
    Boundary between span-level and block-level tokens.
    """
    def __init__(self, lines):
        content = ''.join(lines)
        super().__init__(content, span_token.tokenize_inner)

    @staticmethod
    def start(line):
        return line != '\n'


class BlockCode(BlockToken):
    def __init__(self, lines):
        self.language = ''
        self._children = (span_token.RawText(''.join(line[4:] for line in lines)),)

    @staticmethod
    def start(line):
        return line.startswith('    ')

    @staticmethod
    def read(lines):
        return until('\n', lines)


class CodeFence(BlockToken):
    """
    Code fence. (["```sh\n", "rm -rf /", ..., "```"])
    Boundary between span-level and block-level tokens.

    Attributes:
        children (iterator): contains a single span_token.RawText token.
        language (str): language of code block (default to empty).
    """
    _open_line = ''
    def __init__(self, lines):
        self.language = lines[0].strip()[3:]
        self._children = (span_token.RawText(''.join(lines[1:])),)

    @classmethod
    def start(cls, line):
        if line.startswith('```'):
            cls._open_line = '```'
            return True
        if line.startswith('~~~'):
            cls._open_line = '~~~'
            return True
        return False

    @classmethod
    def read(cls, lines):
        return until(cls._open_line, lines, func=str.startswith)


class List(BlockToken):
    """
    List tokens. (["- item\n", "    - nested item\n", "- item\n" ])
    Boundary between span-level and block-level tokens.

    Attributes:
        children (list): inner tokens (ListItem or List).
        start (int): first index of ordered list (undefined if unordered).
    """
    def __init__(self, lines):
        self._children = self.build_list(lines)
        leader = lines[0].split(' ', 1)[0]
        if leader[:-1].isdigit():
            self.start = int(leader[:-1])
        else:
            self.start = None

    @classmethod
    def build_list(cls, lines):
        """
        Constructor helper; builds a list from lines.

        The basic control structure looks something like this:

        - Does the current line have a valid leader?
            * yes: we are in a normal line
            * no:
                + Does it start with four spaces?
                    - yes:
                        * Does it have a valid leader?
                            + yes: we are in a nested list
                            - no:  we are in a lazy-continuation line
                    - no: we are in a lazy-continuation line

        Yields:
            a stream of ListItems or sub-Lists.
        """
        line_buffer = []
        nested = False

        def clear_buffer():
            """
            After each clear_buffer() call, nested is always False,
            and line_buffer is always empty.
            """
            nonlocal nested, line_buffer
            if not line_buffer:
                # start of the list; nested = False
                return
            yield List(line_buffer) if nested else ListItem(line_buffer)
            nested = False
            line_buffer = []

        for line in lines:
            if cls.has_valid_leader(line):
                yield from clear_buffer()
            elif line.startswith('    '):
                line = line[4:]
                if cls.has_valid_leader(line) and not nested:
                    yield from clear_buffer()
                    nested = True
            line_buffer.append(line)
        yield from clear_buffer()

    @classmethod
    def has_valid_leader(cls, line):
        """
        Helper function; mainly because _build_list is gross enough.

        Note: returns False if line starts with spaces.
        """
        return (line.startswith(('+ ', '- ', '* '))         # unordered
                or (line.split(' ', 1)[0][:-1].isdigit()))  # ordered

    @classmethod
    def start(cls, line):
        return cls.has_valid_leader(line.strip())

    @classmethod
    def read(cls, lines):
        line_buffer = []
        for line in lines:
            if line == '\n' and not cls.has_valid_leader(lines.peek() or ''):
                break
            line_buffer.append(line)
        return line_buffer


class ListItem(BlockToken):
    """
    List item token. (["- item 1\n", "continued\n"])

    Should only be called by List._build_list().
    """
    def __init__(self, lines):
        if lines[-1].strip() == '':
            lines[0] = lines[0].split(' ', 1)[1]
            super().__init__(lines, tokenize)
        else:
            line = ' '.join([line.strip() for line in lines])
            try:
                content = line.split(' ', 1)[1].strip()
            except IndexError:
                content = ''
            super().__init__(content, span_token.tokenize_inner)


class Table(BlockToken):
    """
    Table token.

    Attributes:
        has_header (bool): whether table has header row.
        column_align (list): align options for each column (default to [None]).
        children (tuple): inner tokens (TableRows).
    """
    def __init__(self, lines):
        if '---' in lines[1]:
            self.column_align = [self.parse_align(column)
                    for column in self.split_delimiter(lines[1])]
            self.header = TableRow(lines[0], self.column_align)
            self._children = (TableRow(line, self.column_align) for line in lines[2:])
        else:
            self.column_align = [None]
            self._children = (TableRow(line) for line in lines)

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
        line_buffer = []
        while lines.peek() is not None and '|' in lines.peek():
            line_buffer.append(next(lines))
        if len(line_buffer) < 1 or '---' not in line_buffer[0]:
            raise tokenizer.MismatchException()
        return line_buffer


class TableRow(BlockToken):
    """
    Table row token.

    Should only be called by Table.__init__().
    """
    def __init__(self, line, row_align=None):
        self.row_align = row_align or [None]
        cells = line[1:-2].split('|')
        self._children = (TableCell(cell.strip(), align)
                          for cell, align in zip_longest(cells, self.row_align))


class TableCell(BlockToken):
    """
    Table cell token.
    Boundary between span-level and block-level tokens.

    Should only be called by TableRow.__init__().

    Attributes:
        align (bool): align option for current cell (default to None).
        children (tuple): inner (span-)tokens.
    """
    def __init__(self, content, align=None):
        self.align = align
        super().__init__(content, span_token.tokenize_inner)


class FootnoteBlock(BlockToken):
    """
    Footnote tokens.
    A collection of footnote entries.

    Attributes:
        children (list): footnote entry tokens.
    """
    def __init__(self, lines):
        self._children = (FootnoteEntry(line) for line in lines)

    @classmethod
    def _is_legal(cls, line):
        return line.strip().startswith('[') and ']:' in line

    @classmethod
    def start(cls, line):
        return cls._is_legal(line)

    @classmethod
    def read(cls, lines):
        line_buffer = []
        while (lines.peek() is not None
                and cls._is_legal(lines.peek())
                and lines.peek() != '\n'):
            line_buffer.append(next(lines))
        return line_buffer


class FootnoteEntry(BlockToken):
    """
    Footnote entry tokens.
    Special tokens that aren't really boundaries (but kind of are).

    Should only be called by FootnoteBlock.__init__().

    Attributes:
        key (str): key of footnote entry.
        value (str): value of footnote entry.
    """
    def __init__(self, line):
        key, value = line.strip().split(']:')
        self.key = key[1:]
        self.value = value.strip()


class Separator(BlockToken):
    """
    Separator token (a.k.a. horizontal rule.)
    """
    def __init__(self, lines):
        self.lines = lines

    @classmethod
    def start(cls, line):
        chars = set(line.strip().replace(' ', ''))
        return len(chars) == 1 and chars.pop() in {'-', '_', '*'}

    @staticmethod
    def read(lines):
        return []


def until(stop_line, lines, func=None):
    line_buffer = []
    for line in lines:
        if (line == stop_line if func is None else func(line, stop_line)):
            break
        line_buffer.append(line)
    return line_buffer


"""
Tokens to be included in the parsing process, in the order specified.
"""
_token_types = [Heading, Quote, CodeFence, BlockCode, Separator, List,
                Table, FootnoteBlock, SetextHeading, Paragraph]
