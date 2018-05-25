"""
Block-level tokenizer for mistletoe.
"""


class FileWrapper:
    def __init__(self, lines):
        self.lines = [line.replace('\t', '    ') for line in lines]
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


def tokenize(iterable, token_types, parent=None):
    """
    Searches for token_types in iterable.

    Args:
        content (list[str]): user input lines to be parsed.
        token_types (list): a list of block-level token constructors.

    Returns:
        block-level token instances.
    """
    lines = FileWrapper(iterable)
    tokens = []
    line = lines.peek()
    while line is not None:
        for token_type in token_types:
            if token_type.start(line):
                result = token_type.read(lines)
                if result is not None:
                    token = token_type(result)
                    if token is not None:
                        tokens.append(token)
                    break
        else:  # unmatched newlines
            next(lines)
            if parent and hasattr(parent, "loose"):
                parent.loose = True
        line = lines.peek()
    return tokens

