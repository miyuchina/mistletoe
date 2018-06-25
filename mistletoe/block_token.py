"""
Built-in block-level token classes.
"""

import re
import sys
from itertools import zip_longest
import mistletoe.block_tokenizer as tokenizer
from mistletoe import span_token
from mistletoe.core_tokens import (
        is_link_label,
        follows,
        shift_whitespace,
        whitespace,
        is_control_char,
        normalize_label,
)


"""
Tokens to be included in the parsing process, in the order specified.
"""
__all__ = ['BlockCode', 'Heading', 'Quote', 'CodeFence', 'ThematicBreak',
           'List', 'Table', 'Footnote', 'Paragraph']


"""
Stores a reference to the current document token.

When parsing, footnote entries will be stored in the document by
accessing this pointer.
"""
_root_node = None


def tokenize(lines):
    """
    A wrapper around block_tokenizer.tokenize. Pass in all block-level
    token constructors as arguments to block_tokenizer.tokenize.

    Doing so (instead of importing block_token module in block_tokenizer)
    avoids cyclic dependency issues, and allows for future injections of
    custom token classes.

    _token_types variable is at the bottom of this module.

    See also: block_tokenizer.tokenize, span_token.tokenize_inner.
    """
    return tokenizer.tokenize(lines, _token_types)


def add_token(token_cls, position=0):
    """
    Allows external manipulation of the parsing process.
    This function is usually called in BaseRenderer.__enter__.

    Arguments:
        token_cls (SpanToken): token to be included in the parsing process.
        position (int): the position for the token class to be inserted into.
    """
    _token_types.insert(position, token_cls)


def remove_token(token_cls):
    """
    Allows external manipulation of the parsing process.
    This function is usually called in BaseRenderer.__exit__.

    Arguments:
        token_cls (BlockToken): token to be removed from the parsing process.
    """
    _token_types.remove(token_cls)


def reset_tokens():
    """
    Resets global _token_types to all token classes in __all__.
    """
    global _token_types
    _token_types = [globals()[cls_name] for cls_name in __all__]


class BlockToken(object):
    """
    Base class for block-level tokens. Recursively parse inner tokens.

    Naming conventions:

        * lines denotes a list of (possibly unparsed) input lines, and is
          commonly used as the argument name for constructors.

        * BlockToken.children is a list with all the inner tokens (thus if
          a token has children attribute, it is not a leaf node; if a token
          calls span_token.tokenize_inner, it is the boundary between
          span-level tokens and block-level tokens);

        * BlockToken.start takes a line from the document as argument, and
          returns a boolean representing whether that line marks the start
          of the current token. Every subclass of BlockToken must define a
          start function (see block_tokenizer.tokenize).

        * BlockToken.read takes the rest of the lines in the ducment as an
          iterator (including the start line), and consumes all the lines
          that should be read into this token.

          Default to stop at an empty line.
          
          Note that BlockToken.read does not have to return a list of lines.
          Because the return value of this function will be directly
          passed into the token constructor, we can return any relevant
          parsing information, sometimes even ready-made tokens,
          into the constructor. See block_tokenizer.tokenize.

          If BlockToken.read returns None, the read result is ignored,
          but the token class is responsible for resetting the iterator
          to a previous state. See block_tokenizer.FileWrapper.anchor,
          block_tokenizer.FileWrapper.reset.

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
        lines = [line if line.endswith('\n') else '{}\n'.format(line) for line in lines]
        self.footnotes = {}
        global _root_node
        _root_node = self
        span_token._root_node = self
        self.children = tokenize(lines)
        span_token._root_node = None
        _root_node = None


class Heading(BlockToken):
    """
    Heading token. (["### some heading ###\\n"])
    Boundary between span-level and block-level tokens.

    Attributes:
        level (int): heading level.
        children (list): inner tokens.
    """
    pattern = re.compile(r' {0,3}(#{1,6})(?:\n|\s+?(.*?)(?:\n|\s+?#+\s*?$))')
    level = 0
    content = ''
    def __init__(self, match):
        self.level, content = match
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

    @classmethod
    def read(cls, lines):
        next(lines)
        return cls.level, cls.content

class SetextHeading(BlockToken):
    """
    Setext headings.
    
    Not included in the parsing process, but called by Paragraph.__new__.
    """
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
    Quote token. (["> # heading\\n", "> paragraph\\n"])
    """
    def __init__(self, parse_buffer):
        # span-level tokenizing happens here.
        self.children = tokenizer.make_tokens(parse_buffer)

    @staticmethod
    def start(line):
        stripped = line.lstrip(' ')
        if len(line) - len(stripped) > 3:
            return False
        return stripped.startswith('>')

    @classmethod
    def read(cls, lines):
        # first line
        line = cls.convert_leading_tabs(next(lines).lstrip()).split('>', 1)[1]
        if len(line) > 0 and line[0] == ' ':
            line = line[1:]
        line_buffer = [line]

        # set booleans
        in_code_fence = CodeFence.start(line)
        in_block_code = BlockCode.start(line)
        blank_line = line.strip() == ''

        # loop
        next_line = lines.peek()
        while (next_line is not None
                and next_line.strip() != ''
                and not Heading.start(next_line)
                and not CodeFence.start(next_line)
                and not ThematicBreak.start(next_line)
                and not List.start(next_line)):
            stripped = cls.convert_leading_tabs(next_line.lstrip())
            prepend = 0
            if stripped[0] == '>':
                # has leader, not lazy continuation
                prepend += 1
                if stripped[1] == ' ':
                    prepend += 1
                stripped = stripped[prepend:]
                in_code_fence = CodeFence.start(stripped)
                in_block_code = BlockCode.start(stripped)
                blank_line = stripped.strip() == ''
                line_buffer.append(stripped)
            elif in_code_fence or in_block_code or blank_line:
                # not paragraph continuation text
                break
            else:
                # lazy continuation, preserve whitespace
                line_buffer.append(next_line)
            next(lines)
            next_line = lines.peek()

        # block level tokens are parsed here, so that footnotes
        # in quotes can be recognized before span-level tokenizing.
        Paragraph.parse_setext = False
        parse_buffer = tokenizer.tokenize_block(line_buffer, _token_types)
        Paragraph.parse_setext = True
        return parse_buffer

    @staticmethod
    def convert_leading_tabs(string):
        string = string.replace('>\t', '   ', 1)
        count = 0
        for i, c in enumerate(string):
            if c == '\t':
                count += 4
            elif c == ' ':
                count += 1
            else:
                break
        if i == 0:
            return string
        return '>' + ' ' * count + string[i:]


class Paragraph(BlockToken):
    """
    Paragraph token. (["some\\n", "continuous\\n", "lines\\n"])
    Boundary between span-level and block-level tokens.
    """
    setext_pattern = re.compile(r' {0,3}(=|-)+ *$')
    parse_setext = True  # can be disabled by Quote

    def __new__(cls, lines):
        if not isinstance(lines, list):
            # setext heading token, return directly
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
                and not Quote.start(next_line)):

            # check if next_line starts List
            list_pair = ListItem.parse_marker(next_line)
            if (len(next_line) - len(next_line.lstrip()) < 4
                    and list_pair is not None):
                prepend, leader = list_pair
                # non-empty list item
                if next_line[:prepend].endswith(' '):
                    # unordered list, or ordered list starting from 1
                    if not leader[:-1].isdigit() or leader[:-1] == '1':
                        break

            # check if next_line starts HTMLBlock other than type 7
            html_block = HTMLBlock.start(next_line)
            if html_block and html_block != 7:
                break

            # check if we see a setext underline
            if cls.parse_setext and cls.is_setext_heading(next_line):
                line_buffer.append(next(lines))
                return SetextHeading(line_buffer)

            # check if we have a ThematicBreak (has to be after setext)
            if ThematicBreak.start(next_line):
                break

            # no other tokens, we're good
            line_buffer.append(next(lines))
            next_line = lines.peek()
        return line_buffer

    @classmethod
    def is_setext_heading(cls, line):
        return cls.setext_pattern.match(line)


class BlockCode(BlockToken):
    """
    Indented code.

    Attributes:
        children (list): contains a single span_token.RawText token.
        language (str): always the empty string.
    """
    def __init__(self, lines):
        self.language = ''
        self.children = (span_token.RawText(''.join(lines).strip('\n')+'\n'),)

    @staticmethod
    def start(line):
        return line.replace('\t', '    ', 1).startswith('    ')

    @classmethod
    def read(cls, lines):
        line_buffer = []
        for line in lines:
            if line.strip() == '':
                line_buffer.append(line.lstrip(' ') if len(line) < 5 else line[4:])
                continue
            if not line.replace('\t', '    ', 1).startswith('    '):
                lines.backstep()
                break
            line_buffer.append(cls.strip(line))
        return line_buffer

    @staticmethod
    def strip(string):
        count = 0
        for i, c in enumerate(string):
            if c == '\t':
                return string[i+1:]
            elif c == ' ':
                count += 1
            else:
                break
            if count == 4:
                return string[i+1:]
        return string


class CodeFence(BlockToken):
    """
    Code fence. (["```sh\\n", "rm -rf /", ..., "```"])
    Boundary between span-level and block-level tokens.

    Attributes:
        children (list): contains a single span_token.RawText token.
        language (str): language of code block (default to empty).
    """
    pattern = re.compile(r'( {0,3})((?:`|~){3,}) *(\S*)')
    _open_info = None
    def __init__(self, match):
        lines, open_info = match
        self.language = span_token.EscapeSequence.strip(open_info[2])
        self.children = (span_token.RawText(''.join(lines)),)

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
        return line_buffer, cls._open_info


class List(BlockToken):
    """
    List token.

    Attributes:
        children (list): a list of ListItem tokens.
        loose (bool): whether the list is loose.
        start (NoneType or int): None if unordered, starting number if ordered.
    """
    pattern = re.compile(r' {0,3}(?:\d{0,9}[.)]|[+\-*])(?:[ \t]*$|[ \t]+)')
    def __init__(self, matches):
        self.children = [ListItem(*match) for match in matches]
        self.loose = any(item.loose for item in self.children)
        leader = self.children[0].leader
        self.start = None
        if len(leader) != 1:
            self.start = int(leader[:-1])

    @classmethod
    def start(cls, line):
        return cls.pattern.match(line)

    @classmethod
    def read(cls, lines):
        leader = None
        next_marker = None
        matches = []
        while True:
            output, next_marker = ListItem.read(lines, next_marker)
            item_leader = output[2]
            if leader is None:
                leader = item_leader
            elif not cls.same_marker_type(leader, item_leader):
                lines.reset()
                break
            matches.append(output)
            if next_marker is None:
                break
        return matches

    @staticmethod
    def same_marker_type(leader, other):
        if len(leader) == 1:
            return leader == other
        return leader[:-1].isdigit() and other[:-1].isdigit() and leader[-1] == other[-1]


class ListItem(BlockToken):
    """
    List items. Not included in the parsing process, but called by List.
    """

    pattern = re.compile(r'\s*(\d{0,9}[.)]|[+\-*])(\s*$|\s+)')

    def __init__(self, parse_buffer, prepend, leader):
        self.leader = leader
        self.prepend = prepend
        self.children = tokenizer.make_tokens(parse_buffer)
        self.loose = parse_buffer.loose

    @staticmethod
    def in_continuation(line, prepend):
        return line.strip() == '' or len(line) - len(line.lstrip()) >= prepend

    @staticmethod
    def other_token(line):
        return (Heading.start(line)
                or Quote.start(line)
                or CodeFence.start(line)
                or ThematicBreak.start(line))

    @classmethod
    def parse_marker(cls, line):
        """
        Returns a pair (prepend, leader) iff the line has a valid leader.
        """
        match_obj = cls.pattern.match(line)
        if match_obj is None:
            return None        # no valid leader
        leader = match_obj.group(1)
        content = match_obj.group(0).replace(leader+'\t', leader+'   ', 1)
        # reassign prepend and leader
        prepend = len(content)
        if prepend == len(line.rstrip('\n')):
            prepend = match_obj.end(1) + 1
        else:
            spaces = match_obj.group(2)
            if spaces.startswith('\t'):
                spaces = spaces.replace('\t', '   ', 1)
            spaces = spaces.replace('\t', '    ')
            n_spaces = len(spaces)
            if n_spaces > 4:
                prepend = match_obj.end(1) + 1
        return prepend, leader

    @classmethod
    def read(cls, lines, prev_marker=None):
        next_marker = None
        lines.anchor()
        prepend = -1
        leader = None
        line_buffer = []

        # first line
        line = next(lines)
        prepend, leader = prev_marker if prev_marker else cls.parse_marker(line)
        line = line.replace(leader+'\t', leader+'   ', 1).replace('\t', '    ')
        empty_first_line = line[prepend:].strip() == ''
        if not empty_first_line:
            line_buffer.append(line[prepend:])
        next_line = lines.peek()
        if empty_first_line and next_line is not None and next_line.strip() == '':
            parse_buffer = tokenizer.tokenize_block([next(lines)], _token_types)
            next_line = lines.peek()
            if next_line is not None:
                marker_info = cls.parse_marker(next_line)
                if marker_info is not None:
                    next_marker = marker_info
            return (parse_buffer, prepend, leader), next_marker

        # loop
        newline = 0
        while True:
            # no more lines
            if next_line is None:
                # strip off newlines
                if newline:
                    lines.backstep()
                    del line_buffer[-newline:]
                break
            next_line = next_line.replace('\t', '    ')
            # not in continuation
            if not cls.in_continuation(next_line, prepend):
                # directly followed by another token
                if cls.other_token(next_line):
                    break
                # next_line is a new list item
                marker_info = cls.parse_marker(next_line)
                if marker_info is not None:
                    next_marker = marker_info
                    break
                # not another item, has newlines -> not continuation
                if newline:
                    lines.backstep()
                    del line_buffer[-newline:]
                    break
            next(lines)
            line = next_line
            stripped = line.lstrip(' ')
            diff = len(line) - len(stripped)
            if diff > prepend:
                stripped = ' ' * (diff - prepend) + stripped
            line_buffer.append(stripped)
            newline = newline + 1 if next_line.strip() == '' else 0
            next_line = lines.peek()

        # block-level tokens are parsed here, so that footnotes can be
        # recognized before span-level parsing.
        parse_buffer = tokenizer.tokenize_block(line_buffer, _token_types)
        return (parse_buffer, prepend, leader), next_marker


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
    Footnote token.

    The constructor returns None, because the footnote information
    is stored in Footnote.read.
    """
    label_pattern = re.compile(r'[ \n]{0,3}\[(.+?)\]', re.DOTALL)

    def __new__(cls, _):
        return None

    @classmethod
    def start(cls, line):
        return line.lstrip().startswith('[')

    @classmethod
    def read(cls, lines):
        line_buffer = []
        next_line = lines.peek()
        while next_line is not None and next_line.strip() != '':
            line_buffer.append(next(lines))
            next_line = lines.peek()
        string = ''.join(line_buffer)
        offset = 0
        matches = []
        while offset < len(string) - 1:
            match_info = cls.match_reference(lines, string, offset)
            if match_info is None:
                break
            offset, match = match_info
            matches.append(match)
        cls.append_footnotes(matches, _root_node)
        return matches or None

    @classmethod
    def match_reference(cls, lines, string, offset):
        match_info = cls.match_link_label(string, offset)
        if not match_info:
            cls.backtrack(lines, string, offset)
            return None
        _, label_end, label = match_info

        if not follows(string, label_end-1, ':'):
            cls.backtrack(lines, string, offset)
            return None

        match_info = cls.match_link_dest(string, label_end)
        if not match_info:
            cls.backtrack(lines, string, offset)
            return None
        _, dest_end, dest = match_info

        match_info = cls.match_link_title(string, dest_end)
        if not match_info:
            cls.backtrack(lines, string, dest_end)
            return None
        _, title_end, title = match_info

        return title_end, (label, dest, title)

    @classmethod
    def match_link_label(cls, string, offset):
        start = -1
        end = -1
        escaped = False
        for i, c in enumerate(string[offset:], start=offset):
            if c == '\\' and not escaped:
                escaped = True
            elif c == '[' and not escaped:
                if start == -1:
                    start = i
                else:
                    return None
            elif c == ']' and not escaped:
                end = i
                label = string[start+1:end]
                if label.strip() != '':
                    return start, end+1, label
                return None
            elif escaped:
                escaped = False
        return None

    @classmethod
    def match_link_dest(cls, string, offset):
        offset = shift_whitespace(string, offset+1)
        if offset == len(string):
            return None
        if string[offset] == '<':
            escaped = False
            for i, c in enumerate(string[offset+1:], start=offset+1):
                if c == '\\' and not escaped:
                    escaped = True
                elif c == ' ' or c == '\n' or (c == '<' and not escaped):
                    return None
                elif c == '>' and not escaped:
                    return offset, i+1, string[offset+1:i]
                elif escaped:
                    escaped = False
            return None
        else:
            escaped = False
            count = 0
            for i, c in enumerate(string[offset:], start=offset):
                if c == '\\' and not escaped:
                    escaped = True
                elif c in whitespace:
                    break
                elif not escaped:
                    if c == '(':
                        count += 1
                    elif c == ')':
                        count -= 1
                elif is_control_char(c):
                    return None
                elif escaped:
                    escaped = False
            if count != 0:
                return None
            return offset, i, string[offset:i]

    @classmethod
    def match_link_title(cls, string, offset):
        new_offset = shift_whitespace(string, offset)
        if (new_offset == len(string)
                or '\n' in string[offset:new_offset]
                and string[new_offset] == '['):
            return offset, new_offset, ''
        if string[new_offset] == '"':
            closing = '"'
        elif string[new_offset] == "'":
            closing = "'"
        elif string[new_offset] == '(':
            closing = ')'
        elif '\n' in string[offset:new_offset]:
            return offset, offset, ''
        else:
            return None
        offset = new_offset
        escaped = False
        for i, c in enumerate(string[offset+1:], start=offset+1):
            if c == '\\' and not escaped:
                escaped = True
            elif c == closing and not escaped:
                new_offset = shift_whitespace(string, i+1)
                if '\n' not in string[i+1:new_offset]:
                    return None
                return offset, new_offset, string[offset+1:i]
            elif escaped:
                escaped = False
        return None

    @staticmethod
    def append_footnotes(matches, root):
        for key, dest, title in matches:
            key = normalize_label(key)
            dest = span_token.EscapeSequence.strip(dest.strip())
            title = span_token.EscapeSequence.strip(title)
            if key not in root.footnotes:
                root.footnotes[key] = dest, title

    @staticmethod
    def backtrack(lines, string, offset):
        lines._index -= string[offset+1:].count('\n')


class ThematicBreak(BlockToken):
    """
    Thematic break token (a.k.a. horizontal rule.)
    """
    pattern = re.compile(r' {0,3}(?:([-_*])\s*?)(?:\1\s*?){2,}$')
    def __init__(self, _):
        pass

    @classmethod
    def start(cls, line):
        return cls.pattern.match(line)

    @staticmethod
    def read(lines):
        return [next(lines)]


class HTMLBlock(BlockToken):
    """
    Block-level HTML tokens.

    Attributes:
        content (str): literal strings rendered as-is.
    """
    _end_cond = None
    multiblock = re.compile(r'<(script|pre|style)[ >\n]')
    predefined = re.compile(r'<\/?(.+?)(?:\/?>|[ \n])')
    custom_tag = re.compile(r'(?:' + '|'.join((span_token._open_tag,
                                span_token._closing_tag)) + r')\s*$')

    def __init__(self, lines):
        self.content = ''.join(lines).rstrip('\n')

    @classmethod
    def start(cls, line):
        stripped = line.lstrip()
        if len(line) - len(stripped) >= 4:
            return False
        # rule 1: <pre>, <script> or <style> tags, allow newlines in block
        match_obj = cls.multiblock.match(stripped)
        if match_obj is not None:
            cls._end_cond = '</{}>'.format(match_obj.group(1).casefold())
            return 1
        # rule 2: html comment tags, allow newlines in block
        if stripped.startswith('<!--'):
            cls._end_cond = '-->'
            return 2
        # rule 3: tags that starts with <?, allow newlines in block
        if stripped.startswith('<?'):
            cls._end_cond = '?>'
            return 3
        # rule 4: tags that starts with <!, allow newlines in block
        if stripped.startswith('<!') and stripped[2].isupper():
            cls._end_cond = '>'
            return 4
        # rule 5: CDATA declaration, allow newlines in block
        if stripped.startswith('<![CDATA['):
            cls._end_cond = ']]>'
            return 5
        # rule 6: predefined tags (see html_token._tags), read until newline
        match_obj = cls.predefined.match(stripped)
        if match_obj is not None and match_obj.group(1).casefold() in span_token._tags:
            cls._end_cond = None
            return 6
        # rule 7: custom tags, read until newline
        match_obj = cls.custom_tag.match(stripped)
        if match_obj is not None:
            cls._end_cond = None
            return 7
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
                line_buffer.pop()
                break
        return line_buffer


_token_types = []
reset_tokens()

