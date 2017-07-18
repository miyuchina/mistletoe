import itertools
import core.block_tokenizer as tokenizer
import core.leaf_token as leaf_token

__all__ = ['Heading', 'Quote', 'BlockCode', 'List', 'Table', 'Separator']

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
    def __init__(self, lines):
        if len(lines) == 1:
            hashes, content = lines[0].split('# ', 1)
            content = content.split(' #', 1)[0].strip()
            self.level = len(hashes) + 1
        else:
            if lines[-1][0] == '=': self.level = 1
            elif lines[-1][0] == '-': self.level = 2
            content = ' '.join([ line.strip() for line in lines[:-1] ])
        super().__init__(content, leaf_token.tokenize_inner)

    @staticmethod
    def match(lines):
        if len(lines) == 1 and lines[0].find('# ') != -1: return 1
        else:
            return (lines[-1].startswith('---')
                 or lines[-1].startswith('==='))
        return 0

class Quote(BlockToken):
    def __init__(self, lines):
        content = []
        for line in lines:
            if line.startswith('> '): content.append(line[2:])
            else: content.append(line)
        super().__init__(content, tokenize)

    @staticmethod
    def match(lines): return lines[0].startswith('> ')

class Paragraph(BlockToken):
    # pre: lines = ["some\n", "continuous\n", "lines\n"]
    def __init__(self, lines):
        content = ''.join(lines).replace('\n', ' ').strip()
        self.children = leaf_token.tokenize_inner(content)

    @staticmethod
    def match(lines):
        for line in lines:
            if line == '\n': return 0
        return 1

class BlockCode(BlockToken):
    # pre: lines = ["```sh\n", "rm -rf /", ..., "```"]
    def __init__(self, lines):
        if lines[0].startswith('```'):
            content = ''.join(lines[1:-1])
            self.language = lines[0].strip()[3:]
        else:
            content = ''.join([ line[4:] for line in lines ])
            self.language = ''
        self.children = [ leaf_token.RawText(content) ]

    @staticmethod
    def match(lines):
        if lines[0].startswith('```') and lines[-1] == '```\n': return 1
        for line in lines:
            if not line.startswith(' '*4): return 0
        return True

class List(BlockToken):
    # pre: items = [
    # "- item 1\n",
    # "- item 2\n",
    # "    - nested item\n",
    # "- item 3\n"
    # ]
    def __init__(self, lines):
        self.children = self._build_list(lines)
        leader = lines[0].split(' ', 1)[0]
        if leader[:-1].isdigit():
            self.start = int(leader[:-1])

    def _build_list(self, lines):
        line_buffer = []
        nested = 0
        for line in lines:
            if line.startswith(' '*4):
                line_buffer.append(line[4:])
                nested = 1
            elif nested:
                yield List(line_buffer)
                line_buffer.clear()
                nested = 0
                yield ListItem(line)
            else: yield ListItem(line)
        if nested: yield List(line_buffer)

    @staticmethod
    def match(lines):
        for line in lines:
            content = line.strip()
            if not (content.startswith('+ ')
                    or content.startswith('- ')
                    or content.startswith('* ')
                    or (content.split(' ')[0][:-1].isdigit())):
                return 0
        return 1

class ListItem(BlockToken):
    # pre: line = "- some *italics* text\n"
    def __init__(self, line):
        content = line.strip().split(' ', 1)[1]
        super().__init__(content, leaf_token.tokenize_inner)

class Table(BlockToken):
    def __init__(self, lines):
        self.has_header_row = lines[1].find('---') != -1
        if self.has_header_row:
            self.column_align = self.parse_delimiter(lines.pop(1))
        else: self.column_align = [ None ]
        self.children = ( TableRow(line, self.column_align) for line in lines )

    @staticmethod
    def parse_delimiter(delimiter):
        columns = delimiter[1:-2].split('|')
        return [ Table.parse_delimiter_column(column.strip())
                    for column in columns ]

    @staticmethod
    def parse_delimiter_column(column):
        if column[:4] == ':---' and column[-4:] == '---:': return 0
        if column[-4:] == '---:': return 1
        else: return None

    @staticmethod
    def match(lines):
        for line in lines:
            if line[0] != '|' or line[-2] != '|': return False
        return True

class TableRow(BlockToken):
    def __init__(self, line, row_align=[ 0 ]):
        cells = line[1:-2].split('|')
        self.children = ( TableCell(cell.strip(), align)
                for cell, align in itertools.zip_longest(cells, row_align) )

class TableCell(BlockToken):
    # self.align: None => align-left; 0 => align-mid; 1 => align-right
    def __init__(self, content, align=0):
        self.align = align
        super().__init__(content, leaf_token.tokenize_inner)

class Separator(BlockToken):
    def __init__(self, line):
        self.line = line

    @staticmethod
    def match(lines):
        return len(lines) == 1 and lines[0] == '* * *\n'
