"""
Block-level tokenizer for mistletoe.
"""

import warnings


# Lists and quotes share a limit so their combined depth stays safe to render.
MAX_BLOCK_NESTING = 100


class FileWrapper:
    def __init__(self, lines, start_line=1, depth=0, token_types=None):
        self.lines = lines if isinstance(lines, list) else list(lines)
        self.start_line = start_line
        self.depth = depth
        self.token_types = token_types
        self._index = -1
        self._anchor = 0

    def __next__(self):
        if self._index + 1 < len(self.lines):
            self._index += 1
            return self.lines[self._index]
        raise StopIteration

    def __iter__(self):
        return self

    def __repr__(self):
        return repr(self.lines[self._index + 1:])

    def get_pos(self):
        """Returns the current reading position.
        The result is an opaque value which can be passed to `set_pos`."""
        return self._index

    def set_pos(self, pos):
        """Sets the current reading position."""
        self._index = pos

    def anchor(self):
        """@deprecated use `get_pos` instead"""
        self._anchor = self.get_pos()

    def reset(self):
        """@deprecated use `set_pos` instead"""
        self.set_pos(self._anchor)

    def peek(self):
        if self._index + 1 < len(self.lines):
            return self.lines[self._index + 1]
        return None

    def backstep(self):
        if self._index != -1:
            self._index -= 1

    def line_number(self):
        return self.start_line + self._index


def tokenize(iterable, token_types):
    """
    Searches for token_types in iterable.

    Args:
        iterable (list): user input lines to be parsed.
        token_types (list): a list of block-level token constructors.

    Returns:
        block-level token instances.
    """
    return make_tokens(tokenize_block(iterable, token_types))


def tokenize_block(iterable, token_types, start_line=1, depth=0):
    """
    Returns a list of tuples (token_type, read_result, line_number).

    Footnotes are parsed here, but span-level parsing has not
    started yet.
    """
    if depth >= MAX_BLOCK_NESTING:
        warnings.warn(
            ('Maximum block nesting depth of {} reached; '
             'further list and quote markers are treated as text.').format(MAX_BLOCK_NESTING),
            UserWarning,
            stacklevel=2,
        )
        token_types = [token_type for token_type in token_types
                       if not getattr(token_type, 'nesting_container', False)]
    lines = FileWrapper(iterable, start_line=start_line, depth=depth, token_types=token_types)
    parse_buffer = ParseBuffer()
    line = lines.peek()
    while line is not None:
        for token_type in token_types:
            if token_type.start(line):
                line_number = lines.line_number() + 1
                result = token_type.read(lines)
                if result is not None:
                    parse_buffer.append((token_type, result, line_number))
                    break
        else:  # unmatched newlines
            next(lines)
            parse_buffer.loose = True
        line = lines.peek()
    return parse_buffer


def make_tokens(parse_buffer):
    """
    Takes a list of tuples (token_type, read_result, line_number),
    applies token_type(read_result), and sets the line_number attribute.

    Footnotes are already parsed before this point,
    and span-level parsing is started here.
    """
    tokens = []
    for token_type, result, line_number in parse_buffer:
        token = token_type(result)
        if token is not None:
            token.line_number = line_number
            tokens.append(token)
    return tokens


class ParseBuffer(list):
    """
    A wrapper around builtin list,
    so that setattr(list, 'loose') is legal.
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.loose = False
