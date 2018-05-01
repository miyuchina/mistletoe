"""
Built-in block-level token classes.
"""

import re
import sys
from types import GeneratorType
from itertools import zip_longest
import mistletoe.block_tokenizer as tokenizer
import mistletoe.span_token as span_token

"""
Tokens to be included in the parsing process, in the order specified.
"""
__all__ = ['Heading', 'Quote', 'CodeFence', 'BlockCode', 'Separator',
           'List', 'Table', 'FootnoteBlock', 'SetextHeading', 'Paragraph']


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
        if isinstance(lines, str):
            lines = lines.splitlines(keepends=True)
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
    def read(lines):
        return [next(lines)]

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
        line_buffer = [next(lines)]
        next_line = lines.peek()
        while (next_line is not None
                and next_line != '\n'
                and not Heading.start(next_line)
                and not BlockCode.start(next_line)
                and not CodeFence.start(next_line)
                and not List.start(next_line)):
            line = next(lines)
            line_buffer.append(line)
            if line.startswith(('===', '---')):
                return line_buffer
            next_line = lines.peek()
        raise tokenizer.MismatchException(line_buffer)


class Quote(BlockToken):
    """
    Quote token. (["> # heading\n", "> paragraph\n"])
    """
    def __init__(self, lines):
        content = [line[2:] if line.startswith('> ') else line for line in lines]
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
        content = ''.join(lines).strip()
        super().__init__(content, span_token.tokenize_inner)

    @staticmethod
    def start(line):
        return line != '\n'

    @classmethod
    def read(cls, lines):
        line_buffer = [next(lines)]
        next_line = lines.peek()
        while (next_line is not None
                and not Heading.start(next_line)
                and not BlockCode.start(next_line)
                and not CodeFence.start(next_line)
                and not List.start(next_line)):
            line_buffer.append(next(line))
            next_line = lines.peek()
        return line_buffer


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
    def __init__(self, items):
        self._children = items
        self.loose = self.__class__.loose
        first_leader = self.children[0].leader
        self.start = first_leader if isinstance(first_leader, int) else None

    @classmethod
    def start(cls, line):
        return ListItem.parse_leader(line)

    @classmethod
    def read(cls, lines):
        cls.loose = False
        item_buffer = []
        while True:
            while lines.peek() == '\n':
                next(lines)
            item_lines = ListItem.read(lines)
            if item_lines is None:
                break
            item = ListItem(item_lines)
            cls.loose |= item.loose
            item_buffer.append(item)
        return item_buffer


class ListItem:
    pattern = re.compile(r' {0,3}(\d{1,9}[.)]|[+\-*]) {1,4}')
    leader = None
    prepend = -1

    def __init__(self, lines):
        self.leader = self.__class__.leader
        self.prepend = self.__class__.prepend
        lines[0] = lines[0][self.prepend:]
        self.loose = True
        self.children = tuple(tokenize(lines))
        if len(self.children) == 1 and isinstance(self.children[0], Paragraph):
            self.children = self.children[0].children
            self.loose = False

    @classmethod
    def in_continuation(cls, line):
        return len(line) - len(line.lstrip()) >= cls.prepend

    @classmethod
    def parse_leader(cls, line):
        pos = 0 if cls.prepend == -1 else cls.prepend
        match_obj = cls.pattern.match(line)
        if match_obj is None:
            return False
        content = match_obj.group(0)
        if cls.prepend != -1 and len(content) - len(content.lstrip()) >= cls.prepend:
            return False
        leader = match_obj.group(1)
        cls.leader = leader if len(leader) == 1 else int(leader[:-1])
        cls.prepend = len(content)
        return True

    @classmethod
    def read(cls, lines):
        cls.leader = None
        cls.prepend = -1
        newline = False
        line_buffer = []
        next_line = lines.peek()
        if next_line is not None and cls.parse_leader(next_line):
            line_buffer.append(next(lines))
            next_line = lines.peek()
        else:
            return None
        while (next_line is not None
                and (not cls.parse_leader(next_line))
                and (not newline or cls.in_continuation(next_line))):
            line = next(lines)
            line = line[cls.prepend:] if newline else line.lstrip(' ')
            line_buffer.append(line)
            newline = next_line == '\n'
            next_line = lines.peek()
        return line_buffer



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
        line_buffer = [next(lines)]
        while lines.peek() is not None and '|' in lines.peek():
            line_buffer.append(next(lines))
        if len(line_buffer) < 2 or '---' not in line_buffer[1]:
            raise tokenizer.MismatchException()
        return line_buffer


class TableRow(BlockToken):
    """
    Table row token.

    Should only be called by Table.__init__().
    """
    def __init__(self, line, row_align=None):
        self.row_align = row_align or [None]
        cells = filter(None, line.strip().split('|'))
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
        line_buffer = [next(lines)]
        while (lines.peek() is not None
                and cls._is_legal(lines.peek())
                and lines.peek() != '\n'):
            line_buffer.append(next(lines))
        return line_buffer

    def store_footnotes(self, root):
        for entry in self.children:
            root.footnotes[entry.key] = entry.value


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
        return [next(lines)]


def until(stop_line, lines, func=None):
    line_buffer = [next(lines)]
    for line in lines:
        if (line == stop_line if func is None else func(line, stop_line)):
            break
        line_buffer.append(line)
    return line_buffer


_token_types = []
reset_tokens()

