"""
Block-level tokenizer for mistletoe.
"""

import re    # TODO: git rid ov it plz?


class NeedMoreLines(Exception): pass


def normalize(lines):
    """
    Normalizes input stream. Mostly exist because only newlines
    can trigger block-level token matching in tokenize.
    """
    heading = re.compile(r'#+ |=+$|-+$')
    code_fence = False
    for line in lines:
        # normalize tabs
        line = line.replace('\t', '    ')
        if line.startswith('```'):
            if code_fence:
                yield line
                yield '\n'
                code_fence = False
            else:
                yield '\n'
                yield line
                code_fence = True
        # append headings with a newline
        elif not code_fence and heading.match(line):
            yield line
            yield '\n'
        else:
            yield line
    if code_fence:
        yield '```\n'
    # end the document with a newline, so that tokenize
    # can yield the last token
    yield '\n'

def tokenize(iterable, token_types, fallback_token, root=None):
    """
    Searches for token_types in iterable, and applies fallback_token
    to lines in between.

    Args:
        content (list[str]): user input lines to be parsed.
        token_types (list): a list of block-level token constructors.
        fallback_token (block_token.BlockToken): token for unmatched lines.

    Yields:
        block-level token instances.
    """
    line_buffer = []
    for line in normalize(iterable):
        if line != '\n':    # not a new block
            line_buffer.append(line)
        elif line_buffer:   # skip multiple empty lines
            try:
                token = _match_for_token(line_buffer, token_types, fallback_token, root)
                if token is not None:
                    yield token
                line_buffer.clear()
            except NeedMoreLines:
                line_buffer.append('\n')
                continue


def _match_for_token(line_buffer, token_types, fallback_token, root):
    for token_type in token_types:
        if token_type.match(line_buffer):
            if root and token_type.__name__ == 'FootnoteBlock':
                return store_footnotes(root, token_type(line_buffer))
            else:
                return token_type(line_buffer)
    return fallback_token(line_buffer)


def store_footnotes(root_node, footnote_block):
    for entry in footnote_block.children:
        root_node.footnotes[entry.key] = entry.value

