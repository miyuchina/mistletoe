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

def process_props(result: str):
    if not isinstance(result, str): return None
    if not result.strip().endswith('}'): return None
    def get_props(prop):
        if ':' in prop:
            key, _, value = prop.partition(":")
            return f' {key}="{value}"'
        return None
    propstr = result.strip().replace('{','').replace('}','')
    propslst = propstr.split(',')
    childattr = None
    parentattr = ''

    for prop in propslst:
        prop = prop.strip()
        if prop.startswith('>'):
            childattr = get_props(prop.lstrip('>'))
        else:
            parentattr += get_props(prop)
    
    return (parentattr, childattr)

def apply_props(token, props):
    if not props: return
    token.html_props = props[0]
    if not token.children: return
    for chld in token.children:
        chld.html_props = props[1]


def make_tokens(parse_buffer):
    """
    Takes a list of pairs (token_type, read_result) and
    applies token_type(read_result).

    Footnotes are already parsed before this point,
    and span-level parsing is started here.
    """
    tokens = []
    props = None
    for token_type, result in parse_buffer:
        if not props: 
            props = process_props(result[0])
            if props: continue
        token = token_type(result)
        if token is not None:
            apply_props(token, props)
            tokens.append(token)
            props = None
    return tokens


class ParseBuffer(list):
    """
    A wrapper around builtin list,
    so that setattr(list, 'loose') is legal.
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.loose = False
