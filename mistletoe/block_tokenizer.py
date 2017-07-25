"""
Block-level tokenizer for mistletoe.
"""

import re    # TODO: git rid ov it plz?

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
        if heading.match(line):
            yield line
            yield '\n'
        # enclose code fence with newlines.
        elif not code_fence and line.startswith('```'):
            code_fence = True
            yield '\n'
            yield line
        elif code_fence:
            if line == '```\n':
                code_fence = False
                yield line
                yield '\n'
            elif line == '\n':
                yield ' ' + line
            else:
                yield line
        else: yield line
    # end the document with a newline, so that tokenize
    # can yield the last token
    yield '\n'

def tokenize(iterable, token_types, fallback_token):
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
            matched = False
            # tries to match in the order of token_types
            for token_type in token_types:
                if token_type.match(line_buffer):
                    yield token_type(line_buffer)
                    matched = True
                    break
            if not matched:
                yield fallback_token(line_buffer)
            line_buffer.clear()
