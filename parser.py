import re
from lib.block_token import *
from lib.leaf_token import *
from lib.reader import *

def tokenize(lines):
    tokens = []
    index = 0

    def shift_token(token_type, reader_func):
        end_index = reader_func(index, lines)
        tokens.append(token_type(lines[index:end_index]))
        return end_index

    def shift_line_token(token_type=None):
        if token_type:
            tokens.append(token_type(lines[index]))
        return index + 1

    while index < len(lines):
        if lines[index].startswith('#'):        # heading
            index = shift_line_token(Heading)
        elif lines[index].startswith('> '):     # quote
            index = shift_token(Quote, read_quote)
        elif lines[index].startswith('```'):    # block code
            index = shift_token(BlockCode, read_block_code)
        elif lines[index] == '---\n':           # separator
            index = shift_line_token(Separator)
        elif lines[index].startswith('- '):     # list
            index = shift_token(build_list, read_list)
        elif lines[index] == '\n':              # skip empty line
            index = shift_line_token()
        else:                                   # paragraph
            index = shift_token(Paragraph, read_paragraph)
    return tokens

def tokenize_inner(content):
    tokens = []

    def append_token(token_type, content, index):
        tokens.append(token_type(content[:index]))
        tokenize_inner_helper(content[index:])

    def tokenize_inner_helper(content):
        if content == '':                                 # base case
            return
        if re.match(r"\*\*(.+?)\*\*", content):           # bold
            i = content.index('**', 1) + 2
            append_token(Bold, content, i)
        elif re.match(r"\*(.+?)\*", content):             # italics
            i = content.index('*', 1) + 1
            append_token(Italic, content, i)
        elif re.match(r"`(.+?)`", content):               # inline code
            i = content.index('`', 1) + 1
            append_token(InlineCode, content, i)
        elif re.match(r"\[(.+?)\]\((.+?)\)", content):    # link
            i = content.index(')') + 1
            append_token(Link, content, i)
        else:                                             # raw text
            try:                      # next token
                p = r"(`(.+?)`)|(\*\*(.+?)\*\*)|(\*(.+?)\*)|\[(.+?)\]\((.+?)\)"
                i = re.search(p, content).start()
            except AttributeError:    # no more tokens
                i = len(content)
            append_token(RawText, content, i)
    tokenize_inner_helper(content)
    return tokens

def build_list(lines, level=0):
    l = List()
    index = 0
    while index < len(lines):
        if lines[index][level*4:].startswith('- '):
            l.add(ListItem(lines[index]))
        else:
            curr_level = level + 1
            end_index = read_list(index, lines, curr_level)
            l.add(build_list(lines[index:end_index], curr_level))
            index = end_index - 1
        index += 1
    return l

