"""
Block-level tokenizer for mistletoe.
"""


class FileWrapper:
    def __init__(self, lines):
        self.lines = lines if isinstance(lines, list) else list(lines)
        self._index = -1
        self._anchor = 0

    def __next__(self):
        self._index += 1
        if self._index < len(self.lines):
            return self.lines[self._index]
        raise StopIteration

    def __iter__(self):
        return self

    def __repr__(self):
        return repr(self.lines[self._index+1:])

    def anchor(self):
        self._anchor = self._index

    def reset(self):
        self._index = self._anchor

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
        content (list[str]): user input lines to be parsed.
        token_types (list): a list of block-level token constructors.

    Returns:
        block-level token instances.
    """
    return make_tokens(tokenize_block(iterable, token_types))


def tokenize_block(iterable, token_types):
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
    tokens = []
    for token_type, result in parse_buffer:
        token = token_type(result)
        if token is not None:
            tokens.append(token)
    return tokens


class ParseBuffer(list):
    def __init__(self, *args):
        super().__init__(*args)
        self.loose = False
