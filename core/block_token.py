import re
import html
import core.block_tokenizer as tokenizer
import core.leaf_token as leaf_token

__all__ = ['Heading', 'Quote', 'Paragraph', 'BlockCode',
           'List', 'ListItem', 'Separator']

class BlockToken(object):
    def __init__(self, content, tokenize_func):
        self.children = tokenize_func(content)

class Document(BlockToken):
    def __init__(self, lines):
        super().__init__(lines, tokenize)

class Heading(BlockToken):
    # pre: line = "### heading 3\n"
    def __init__(self, line):
        hashes, content = line.strip().split(' ', 1)
        self.level = len(hashes)
        super().__init__(content, leaf_token.tokenize_inner)

class Quote(BlockToken):
    # pre: lines[i] = "> some text\n"
    def __init__(self, lines):
        content = [ line[2:] for line in lines ]
        super().__init__(content, tokenize)

class Paragraph(BlockToken):
    # pre: lines = ["some\n", "continuous\n", "lines\n"]
    def __init__(self, lines):
        content = ' '.join([ line.strip() for line in lines ])
        super().__init__(content, leaf_token.tokenize_inner)

class BlockCode(BlockToken):
    # pre: lines = ["```sh\n", "rm -rf /", ..., "```"]
    def __init__(self, lines):
        self.content = ''.join(lines[1:-1]) # implicit newlines
        self.language = lines[0].strip()[3:]

class List(BlockToken):
    # pre: items = [
    # "- item 1\n",
    # "- item 2\n",
    # "    - nested item\n",
    # "- item 3\n"
    # ]
    def __init__(self, lines, level=0):
        self.children = []
        self._level = level
        self._build_list(lines)

    def _check_ordered(self, line):
        leader = line.split(' ', 1)[0]
        if leader[:-1].isdigit():
            self.start = int(leader[:-1])

    def _build_list(self, lines):
        self._check_ordered(lines[0])
        index = 0
        while index < len(lines):
            line = lines[index][self._level*4:]
            if line.startswith(' '*4):
                curr_level = self._level + 1
                end_index = tokenizer.read_list(index, lines, curr_level)
                sublist = List(lines[index:end_index], curr_level)
                self.children.append(sublist)
                index = end_index - 1
            else:
                self.children.append(ListItem(lines[index]))
            index += 1

    def add(self, item):
        self.children.append(item)

class ListItem(BlockToken):
    # pre: line = "- some *italics* text\n"
    def __init__(self, line):
        content = line.strip().split(' ', 1)[1]
        super().__init__(content, leaf_token.tokenize_inner)

class Separator(BlockToken):
    def __init__(self, line):
        pass

def tokenize(lines):
    tokens = []
    index = 0

    def shift_token(token_type, tokenize_func):
        end_index = tokenize_func(index, lines)
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
            index = shift_token(Quote, tokenizer.read_quote)
        elif lines[index].startswith('```'):    # block code
            index = shift_token(BlockCode, tokenizer.read_block_code)
        elif lines[index] == '---\n':           # separator
            index = shift_line_token(Separator)
        elif re.match(r'([\+\-\*] )|([0-9]\. )', lines[index]): # list 
            index = shift_token(List, tokenizer.read_list)
        elif lines[index] == '\n':              # skip empty line
            index = shift_line_token()
        else:                                   # paragraph
            index = shift_token(Paragraph, tokenizer.read_paragraph)
    return tokens
