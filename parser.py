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

    def build_list(lines, level=0):
        l = List()
        index = 0
        while index < len(lines):
            curr_line = lines[index][level*4:]
            if curr_line.startswith('- '):
                l.add(ListItem(lines[index]))
            elif curr_line.startswith(' '*4):
                curr_level = level + 1
                end_index = read_list(index, lines, curr_level)
                l.add(build_list(lines[index:end_index], curr_level))
                index = end_index - 1
            index += 1
        return l

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
    re_bold = re.compile(r"\*\*(.+?)\*\*")
    re_ital = re.compile(r"\*(.+?)\*")
    re_code = re.compile(r"`(.+?)`")
    re_link = re.compile(r"\[(.+?)\]\((.+?)\)")

    def append_token(token_type, close_tag, content):
        index = content.index(close_tag, 1) + len(close_tag)
        tokens.append(token_type(content[:index]))
        tokenize_inner_helper(content[index:])

    def append_raw_text(content):
        try:                  # next token
            matches = [re_bold.search(content),
                       re_ital.search(content),
                       re_code.search(content),
                       re_link.search(content)]
            index = min([ match.start() for match in matches if match ])
        except ValueError:    # no more tokens
            index = len(content)
        tokens.append(RawText(content[:index]))
        tokenize_inner_helper(content[index:])

    def tokenize_inner_helper(content):
        if content == '':                                 # base case
            return
        if re_bold.match(content):      # bold
            append_token(Bold, '**', content)
        elif re_ital.match(content):    # italics
            append_token(Italic, '*', content)
        elif re_code.match(content):    # inline code
            append_token(InlineCode, '`', content)
        elif re_link.match(content):    # link
            append_token(Link, ')', content)
        else:                           # raw text
            append_raw_text(content)

    tokenize_inner_helper(content)
    return tokens

