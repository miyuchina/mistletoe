import itertools
import mistletoe.block_tokenizer as tokenizer
import mistletoe.span_token as span_token

__all__ = ['Heading', 'Quote', 'BlockCode', 'Separator', 'List', 'Table']

def tokenize(lines):
    token_types = [globals()[key] for key in __all__]
    fallback_token = Paragraph
    return tokenizer.tokenize(lines, token_types, fallback_token)

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
            if lines[-1][0] == '=':
                self.level = 1
            elif lines[-1][0] == '-':
                self.level = 2
            content = ' '.join([line.strip() for line in lines[:-1]])
        super().__init__(content, span_token.tokenize_inner)

    @staticmethod
    def match(lines):
        if len(lines) == 1 and lines[0].find('# ') != -1:
            return True
        return lines[-1].startswith('---') or lines[-1].startswith('===')

class Quote(BlockToken):
    def __init__(self, lines):
        content = []
        for line in lines:
            if line.startswith('> '):
                content.append(line[2:])
            else:
                content.append(line)
        super().__init__(content, tokenize)

    @staticmethod
    def match(lines):
        return lines[0].startswith('> ')

class Paragraph(BlockToken):
    # pre: lines = ["some\n", "continuous\n", "lines\n"]
    def __init__(self, lines):
        content = ''.join(lines).replace('\n', ' ').strip()
        self.children = span_token.tokenize_inner(content)

    @staticmethod
    def match(lines):
        for line in lines:
            if line == '\n':
                return False
        return True

class BlockCode(BlockToken):
    # pre: lines = ["```sh\n", "rm -rf /", ..., "```"]
    def __init__(self, lines):
        if lines[0].startswith('```'):
            content = ''.join(lines[1:-1])
            self.language = lines[0].strip()[3:]
        else:
            content = ''.join([line[4:] for line in lines])
            self.language = ''
        self.children = [span_token.RawText(content)]

    @staticmethod
    def match(lines):
        if lines[0].startswith('```') and lines[-1] == '```\n':
            return True
        for line in lines:
            if not line.startswith(' '*4):
                return False
        return True

class List(BlockToken):
    # pre: items = [
    # "- item 1\n",
    # "- item 2\n",
    # "    - nested item\n",
    # "- item 3\n"
    # ]
    def __init__(self, lines):
        self.children = List._build_list(lines)
        leader = lines[0].split(' ', 1)[0]
        if leader[:-1].isdigit():
            self.start = int(leader[:-1])

    @staticmethod
    def _build_list(lines):
        line_buffer = []
        nested = False
        for line in lines:
            if List.has_valid_leader(line):
                if line_buffer:
                    if nested:
                        yield List(line_buffer)
                        nested = False
                    else:
                        yield ListItem(line_buffer)
                    line_buffer.clear()
                line_buffer.append(line)
            elif line.startswith(' '*4):
                if not nested and List.has_valid_leader(line[4:]):
                    if line_buffer:
                        yield ListItem(line_buffer)
                        line_buffer.clear()
                    nested = True
                line_buffer.append(line[4:])
            else:
                line_buffer.append(line)
        if line_buffer:
            yield List(line_buffer) if nested else ListItem(line_buffer)
            line_buffer.clear()     # recursion magic; critical

    @staticmethod
    def has_valid_leader(line):
        return (line.startswith(('+ ', '- ', '* '))
                or (line.split(' ')[0][:-1].isdigit()))

    @staticmethod
    def match(lines):
        if not List.has_valid_leader(lines[0].strip()):
            return False
        return True

class ListItem(BlockToken):
    def __init__(self, lines):
        line = ' '.join([line.strip() for line in lines])
        content = line.split(' ', 1)[1].strip()
        super().__init__(content, span_token.tokenize_inner)

class Table(BlockToken):
    def __init__(self, lines):
        self.has_header = lines[1].find('---') != -1
        if self.has_header:
            self.column_align = self.parse_delimiter(lines.pop(1))
        else: self.column_align = [None]
        self.children = (TableRow(line, self.column_align) for line in lines)

    @staticmethod
    def parse_delimiter(delimiter):
        columns = delimiter[1:-2].split('|')
        return [Table.parse_delimiter_column(column.strip())
                for column in columns]

    @staticmethod
    def parse_delimiter_column(column):
        if column[:4] == ':---' and column[-4:] == '---:':
            return 0
        if column[-4:] == '---:':
            return 1
        return None

    @staticmethod
    def match(lines):
        for line in lines:
            if line[0] != '|' or line[-2] != '|':
                return False
        return True

class TableRow(BlockToken):
    def __init__(self, line, row_align=None):
        if row_align is None:
            row_align = [None]
        cells = line[1:-2].split('|')
        self.children = (TableCell(cell.strip(), align)
                         for cell, align in itertools.zip_longest(cells, row_align))

class TableCell(BlockToken):
    # self.align: None => align-left; 0 => align-mid; 1 => align-right
    def __init__(self, content, align=None):
        self.align = align
        super().__init__(content, span_token.tokenize_inner)

class Separator(BlockToken):
    def __init__(self, line):
        self.line = line

    @staticmethod
    def match(lines):
        return len(lines) == 1 and lines[0] == '* * *\n'
