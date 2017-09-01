"""
Block-level tokenizer for mistletoe.
"""

import re    # TODO: git rid ov it plz?


class NonBreakingLine(str):
    def __new__(cls):
        return super().__new__(cls, '\n')
    
    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True


def normalize(lines):
    """
    Normalizes input stream. Mostly exist because only newlines
    can trigger block-level token matching in tokenize.

    This function is embarrasing, gross, and looks like a spaghetti.
    """
    heading = re.compile(r'#+ |=+$|-+$')
    code_fence = False
    for line in lines:
        # normalize tabs
        line = line.replace('\t', '    ')
        # append headings with a newline
        # enclose code fence with newlines.
        if not code_fence and line.startswith('```'):
            code_fence = True
            yield '\n'
            yield line
        elif code_fence:
            if line == '```\n':
                code_fence = False
                yield line
                yield '\n'
            elif line == '\n':
                yield NonBreakingLine()
            else:
                yield line
        elif heading.match(line):
            yield line
            yield '\n'
        else: yield line
    # close all unclosed code fences
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
            token = _match_for_token(line_buffer, token_types, fallback_token, root)
            if token is not None:
                yield token
            line_buffer.clear()


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

