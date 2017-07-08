import re
import components as token

__all__ = ['read_quote', 'read_block_code', 'read_paragraph', 'read_list']

def tokenize(lines):
    tokens = []
    index = 0
    while index < len(lines):
        if lines[index].startswith('#'):
            tokens.append(token.Heading(lines[index]))
            index += 1
        elif lines[index].startswith('> '):
            end_index = read_quote(index, lines)
            tokens.append(token.Quote(lines[index:end_index]))
            index = end_index
        elif lines[index].startswith('```'):
            end_index = read_block_code(index, lines)
            tokens.append(token.BlockCode(lines[index:end_index]))
            index = end_index
        elif lines[index] == '---\n':
            tokens.append(token.Separator)
            index += 1
        elif lines[index].startswith('- '):
            end_index = read_list(index, lines)
            tokens.append(build_list(lines[index:end_index]))
            index = end_index
        elif lines[index] == '\n':
            index += 1
        else:
            end_index = read_paragraph(index, lines)
            tokens.append(token.Paragraph(lines[index:end_index]))
            index = end_index
    return tokens

def read_quote(index, lines):
    while index < len(lines):
        if not lines[index].startswith('> '):
            return index
        index += 1
    return index

def read_block_code(index, lines):
    index += 1    # skip first line
    while index < len(lines):
        if lines[index] == '```\n':
            return index + 1
        index += 1
    return index

def read_paragraph(index, lines):
    index += 1
    while index < len(lines):
        if lines[index] == '\n':
            return index
        index += 1
    return index

def read_list(index, lines, level=0):
    while index < len(lines):
        if not lines[index][level*4:].strip().startswith('- '):
            return index
        index += 1
    return index

def build_list(lines, level=0):
    l = token.List()
    index = 0
    while index < len(lines):
        if lines[index][level*4:].startswith('- '):
            l.add(token.ListItem(lines[index]))
        else:
            curr_level = level + 1
            end_index = read_list(index, lines, curr_level)
            l.add(build_list(lines[index:end_index], curr_level))
            index = end_index - 1
        index += 1
    return l

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
            append_token(token.Bold, content, i)
        elif re.match(r"\*(.+?)\*", content):             # italics
            i = content.index('*', 1) + 1
            append_token(token.Italic, content, i)
        elif re.match(r"`(.+?)`", content):               # inline code
            i = content.index('`', 1) + 1
            append_token(token.InlineCode, content, i)
        elif re.match(r"\[(.+?)\]\((.+?)\)", content):    # link
            i = content.index(')') + 1
            append_token(token.Link, content, i)
        else:                                             # raw text
            try:                      # next token
                p = r"(`(.+?)`)|(\*\*(.+?)\*\*)|(\*(.+?)\*)|\[(.+?)\]\((.+?)\)"
                i = re.search(p, content).start()
            except AttributeError:    # no more tokens
                i = len(content)
            append_token(token.RawText, content, i)
    tokenize_inner_helper(content)
    return tokens
