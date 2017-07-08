import html
import parser
from lib.base_token import Token

__all__ = ['Heading', 'Quote', 'Paragraph', 'BlockCode',
           'List', 'ListItem', 'Separator']

class BlockToken(Token):
    def __init__(self, content, tagname, tokenize_func):
        self.content = content
        self.tagname = tagname
        self._tokenize_func = tokenize_func

    def render(self):
        inner_tokens = self._tokenize_func(self.content)
        inner = ''.join([ token.render() for token in inner_tokens ])
        return Token.tagify(self.tagname, inner)

class Heading(BlockToken):
    # pre: line = "### heading 3\n"
    def __init__(self, line):
        hashes, content = line.strip().split(' ', 1)
        tagname = "h{}".format(len(hashes))
        super().__init__(content, tagname, parser.tokenize_inner)

class Quote(BlockToken):
    # pre: lines[i] = "> some text\n"
    def __init__(self, lines):
        content = [ line[2:] for line in lines ]
        super().__init__(content, 'blockquote', parser.tokenize)

class Paragraph(BlockToken):
    # pre: lines = ["some\n", "continuous\n", "lines\n"]
    def __init__(self, lines):
        content = ' '.join([ line.strip() for line in lines ])
        super().__init__(content, 'p', parser.tokenize_inner)

class BlockCode(BlockToken):
    # pre: lines = ["```sh\n", "rm -rf /", ..., "```"]
    def __init__(self, lines):
        self.content = ''.join(lines[1:-1]) # implicit newlines
        self.language = lines[0].strip()[3:]

    def render(self):
        attrs = { 'class': self.language }
        content = html.escape(self.content)
        inner = Token.tagify_attrs('code', attrs, content)
        return Token.tagify('pre', inner)

class List(BlockToken):
    # pre: items = [
    # "- item 1\n",
    # "- item 2\n",
    # "    - nested item\n",
    # "- item 3\n"
    # ]
    def __init__(self):
        super().__init__([], 'ul', lambda x: x)

    def add(self, item):
        self.content.append(item)

class ListItem(BlockToken):
    # pre: line = "- some *italics* text\n"
    def __init__(self, line):
        super().__init__(line.strip()[2:], 'li', parser.tokenize_inner)

class Separator(BlockToken):
    def render():
        return '<hr>'
