import html
import parser
import lib.html_renderer as renderer

__all__ = ['Heading', 'Quote', 'Paragraph', 'BlockCode',
           'List', 'ListItem', 'Separator']

class BlockToken(object):
    def __init__(self, content, tagname, tokenize_func):
        self.children = tokenize_func(content)
        self.tagname = tagname

    def render(self):
        inner = ''.join([ token.render() for token in self.children ])
        return renderer.tagify(self.tagname, inner)

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
        inner = renderer.tagify_attrs('code', attrs, content)
        return renderer.tagify('pre', inner)

class List(BlockToken):
    # pre: items = [
    # "- item 1\n",
    # "- item 2\n",
    # "    - nested item\n",
    # "- item 3\n"
    # ]
    def __init__(self):
        self.children = []
        self.tagname = 'ul'

    def add(self, item):
        self.children.append(item)

class ListItem(BlockToken):
    # pre: line = "- some *italics* text\n"
    def __init__(self, line):
        super().__init__(line.strip()[2:], 'li', parser.tokenize_inner)

class Separator(BlockToken):
    def __init__(self, line):
        pass

    def render(self):
        return '<hr>'
