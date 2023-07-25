"""
Block-level tokenizer for mistletoe.
"""


class FileWrapper:
    def __init__(self, lines):
        self.lines = lines if isinstance(lines, list) else list(lines)
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
        return repr(self.lines[self._index+1:])

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
            return self.lines[self._index+1]
        return None

    def backstep(self):
        if self._index != -1:
            self._index -= 1


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


def tokenize_block(iterable, token_types):
    """
    Returns a list of pairs (token_type, read_result).

    Footnotes are parsed here, but span-level parsing has not
    started yet.
    """
    lines = FileWrapper(iterable)
    parse_buffer = ParseBuffer()
    line = lines.peek()
    while line is not None:
        for token_type in token_types:
            if token_type.start(line):
                result = token_type.read(lines)
                if result is not None:
                    parse_buffer.append((token_type, result))
                    break
        else:  # unmatched newlines
            next(lines)
            parse_buffer.loose = True
        line = lines.peek()
    return parse_buffer


def make_tokens(parse_buffer):
    """
    Takes a list of pairs (token_type, read_result) and
    applies token_type(read_result).

    Footnotes are already parsed before this point,
    and span-level parsing is started here.
    """
    tokens = []
    for token_type, result in parse_buffer:
        token = token_type(result)
        if token is not None:
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
