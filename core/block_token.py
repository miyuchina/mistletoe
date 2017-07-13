import re
import core.block_tokenizer as tokenizer
import core.leaf_token as leaf_token

# TODO: add list
# __all__ = ['Heading', 'Quote', 'BlockCode', 'List', 'Separator']
__all__ = ['Heading', 'Quote', 'BlockCode', 'Separator']

def tokenize(lines):
    token_types = [ globals()[key] for key in __all__ ]
    fallback_token = Paragraph
    bt = tokenizer.BlockTokenizer(lines, token_types, fallback_token)
    return bt.get_tokens()

class BlockToken(object):
    def __init__(self, content, tokenize_func):
        self.children = tokenize_func(content)

class Document(BlockToken):
    def __init__(self, lines):
        super().__init__(lines, tokenize)

class Heading(BlockToken):
    # pre: line = "### heading 3\n"
    _atx_pattern = re.compile(r'(#+) ([^#]+)( #* *)?\n$')
    def __init__(self, lines):
        if len(lines) == 1:
            match_obj = self._atx_pattern.match(lines[0])
            try:
                self.level = len(match_obj.group(1))
                content = match_obj.group(2)
            except AttributeError:
                raise RuntimeError('Unrecognized heading pattern.')
        else:
            if lines[-1][0] == '=': self.level = 1
            elif lines[-1][0] == '-': self.level = 2
            content = ' '.join([ line.strip() for line in lines[:-1] ])
        super().__init__(content, leaf_token.tokenize_inner)

    @staticmethod
    def match(lines):
        if len(lines) == 1:
            if Heading._atx_pattern.match(lines[0]):
                return True
        else:
            return lines[-1].startswith('---') or lines[-1].startswith('===')
        return False

class Quote(BlockToken):
    # pre: lines[i] = "> some text\n"
    def __init__(self, lines):
        content = [ line[2:] for line in lines ]
        super().__init__(content, tokenize)

    @staticmethod
    def match(lines):
        for line in lines:
            if not line.startswith('> '): return False
        return True

class Paragraph(BlockToken):
    # pre: lines = ["some\n", "continuous\n", "lines\n"]
    def __init__(self, lines):
        content = ' '.join([ line.strip() for line in lines ])
        super().__init__(content, leaf_token.tokenize_inner)

    @staticmethod
    def match(lines):
        for line in lines:
            if line == '\n': return False
        return True

class BlockCode(BlockToken):
    # pre: lines = ["```sh\n", "rm -rf /", ..., "```"]
    def __init__(self, lines):
        self.content = ''.join(lines[1:-1]) # implicit newlines
        self.language = lines[0].strip()[3:]

    @staticmethod
    def match(lines):
        return lines[0].startswith('```') and lines[-1] == '```'

class List(BlockToken):
    # pre: items = [
    # "- item 1\n",
    # "- item 2\n",
    # "    - nested item\n",
    # "- item 3\n"
    # ]
    def __init__(self, lines, level=0):
        self.children = self._build_list(lines)
        self._level = level
        self._check_ordered(lines[0])

    def _check_ordered(self, line):
        leader = line.split(' ', 1)[0]
        if leader[:-1].isdigit():
            self.start = int(leader[:-1])

    def _build_list(self, lines):
        index = 0
        while index < len(lines):
            line = lines[index][self._level*4:]
            if line.startswith(' '*4):
                curr_level = self._level + 1
                end_index = self.read(index, lines, curr_level)
                yield List(lines[index:end_index], curr_level)
                index = end_index
            else:
                yield ListItem(lines[index])
                index += 1

    @staticmethod
    def read(index, lines, level=0):
        while index < len(lines):
            expected_content = lines[index][level*4:].strip()
            if not re.match(r'([\+\-\*] )|([0-9]\. )', expected_content):
                return index
            index += 1
        return index

    @staticmethod
    def check_start(line): return re.match(r'([\+\-\*] )|([0-9]\. )', line)

class ListItem(BlockToken):
    # pre: line = "- some *italics* text\n"
    def __init__(self, line):
        content = line.strip().split(' ', 1)[1]
        super().__init__(content, leaf_token.tokenize_inner)

class Separator(BlockToken):
    def __init__(self, line):
        self.line = line

    @staticmethod
    def match(lines):
        return len(lines) == 1 and lines[0] == '* * *\n'
