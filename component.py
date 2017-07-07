import parser

# TODO: make everything html safe

class Component(object):
    def tagify(tag, content):
        return "<{0}>{1}</{0}>".format(tag, content)

    def tagify_attrs(tag, attrs, content):
        attrs = [ "{}=\"{}\"".format(key, attrs[key]) for key in attrs ]
        attrs = ' '.join(attrs)
        return "<{0} {1}>{2}</{0}>".format(tag, attrs, content)

class Heading(Component):
    # pre: line = "### heading 3\n"
    def __init__(self, line):
        hashes, self.content = line.strip().split(' ', 1)
        self.level = len(hashes)

    def render(self):
        inner_tokens = parser.tokenize_inner(self.content)
        inner = ''.join([ token.render() for token in inner_tokens ])
        return Component.tagify("h{}".format(self.level), inner)

class Quote(Component):
    # pre: lines[i] = "> some text\n"
    def __init__(self, lines):
        self.content = [ line.strip()[2:] for line in lines ]

    def render(self):
        inner_tokens = parser.tokenize(self.content)
        inner = '\n'.join([ token.render() for token in inner_tokens ])
        return Component.tagify('blockquote', inner)

class BlockCode(Component):
    # pre: lines = ["```sh\n", "rm -rf /", ..., "```"]
    def __init__(self, lines):
        self.content = ''.join(lines[1:-1]) # implicit newlines
        self.language = lines[0].strip()[3:]

    def render(self):
        attrs = { 'class': self.language }
        inner = Component.tagify_attrs('code', attrs, self.content)
        return Component.tagify('pre', inner)

class Bold(Component):
    # pre: raw = "** some string **"
    def __init__(self, raw):
        self.content = raw[2:-2]

    def render(self):
        return Component.tagify('b', self.content)

class Italic(Component):
    # pre: raw = "* some string *"
    def __init__(self, raw):
        self.content = raw[1:-1]

    def render(self):
        return Component.tagify('em', self.content)

class InlineCode(Component):
    # pre: raw = "`some code`"
    def __init__(self, raw):
        self.content = raw[1:-1]

    def render(self):
        return Component.tagify('code', self.content)

class Link(Component):
    # pre: raw = "[link name](link target)"
    def __init__(self, raw):
        self.name = raw[1:raw.index(']')]
        self.target = raw[raw.index('(')+1:-1]

    def render(self):
        attrs = { 'href': self.target }
        return Component.tagify_attrs('a', attrs, self.name)

class Paragraph(Component):
    # pre: lines = ["some\n", "continuous\n", "lines\n"]
    def __init__(self, lines):
        self.content = ' '.join([ line.strip() for line in lines ])

    def render(self):
        inner_tokens = parser.tokenize_inner(self.content)
        inner = ''.join([ token.render() for token in inner_tokens ])
        return Component.tagify('p', inner)

class List(Component):
    # pre: items = [
    # "- item 1\n",
    # "- item 2\n",
    # "    - nested item\n",
    # "- item 3\n"
    # ]
    def __init__(self):
        self.items = []

    def add(self, item):
        self.items.append(item)

    def render(self):
        inner = ''.join([ item.render() for item in self.items ])
        return Component.tagify('ul', inner)

class ListItem(Component):
    # pre: line = "- some *italics* text\n"
    def __init__(self, line):
        self.content = line.strip()[2:]

    def render(self):
        inner_tokens = parser.tokenize_inner(self.content)
        inner = ''.join([ token.render() for token in inner_tokens ])
        return Component.tagify('li', inner)

class Separator(Component):
    def render():
        return '<hr>'

class RawText(Component):
    def __init__(self, content):
        self.content = content

    def render(self):
        return self.content
