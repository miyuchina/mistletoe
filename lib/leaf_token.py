import html
from lib.base_token import Token

__all__ = ['Bold', 'Italic', 'InlineCode', 'Link', 'RawText']

class LeafToken(Token):
    def __init__(self, content, tagname):
        self.content = content
        self.tagname = tagname

    def render(self):
        content = html.escape(self.content)
        return Token.tagify(self.tagname, content)

class Bold(LeafToken):
    # pre: raw = "** some string **"
    def __init__(self, raw):
        super().__init__(raw[2:-2], 'b')

class Italic(LeafToken):
    # pre: raw = "* some string *"
    def __init__(self, raw):
        super().__init__(raw[1:-1], 'em')

class InlineCode(LeafToken):
    # pre: raw = "`some code`"
    def __init__(self, raw):
        super().__init__(raw[1:-1], 'code')

class Link(LeafToken):
    # pre: raw = "[link name](link target)"
    def __init__(self, raw):
        self.name = raw[1:raw.index(']')]
        self.target = raw[raw.index('(')+1:-1]

    def render(self):
        attrs = { 'href': self.target }
        name = html.escape(self.name)
        return Token.tagify_attrs('a', attrs, name)

class RawText(LeafToken):
    def __init__(self, content):
        self.content = content

    def render(self):
        return html.escape(self.content)

