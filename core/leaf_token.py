import re
import html
import lib.html_renderer as renderer

__all__ = ['Bold', 'Italic', 'InlineCode', 'Strikethrough',
           'Link', 'RawText']

class LeafToken(object):
    def __init__(self, content, tagname):
        self.children = tokenize_inner(content)
        self.tagname = tagname

    def render(self):
        inner = ''.join([ token.render() for token in self.children ])
        return renderer.tagify(self.tagname, inner)

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

class Strikethrough(LeafToken):
    def __init__(self, raw):
        super().__init__(raw[2:-2], 'del')

class Link(LeafToken):
    # pre: raw = "[link name](link target)"
    def __init__(self, raw):
        self.name = raw[1:raw.index(']')]
        self.target = raw[raw.index('(')+1:-1]

    def render(self):
        attrs = { 'href': self.target }
        name = html.escape(self.name)
        return renderer.tagify_attrs('a', attrs, name)

class RawText(LeafToken):
    def __init__(self, content):
        self.content = content

    def render(self):
        return html.escape(self.content)

def tokenize_inner(content):
    tokens = []
    re_bold = re.compile(r"\*\*(.+?)\*\*")
    re_ital = re.compile(r"\*(.+?)\*")
    re_code = re.compile(r"`(.+?)`")
    re_thru = re.compile(r"~~(.+?)~~")
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
                       re_thru.search(content),
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
        elif re_thru.match(content):
            append_token(Strikethrough, '~~', content)
        elif re_link.match(content):    # link
            append_token(Link, ')', content)
        else:                           # raw text
            append_raw_text(content)

    tokenize_inner_helper(content)
    return tokens

