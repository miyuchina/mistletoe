import re
import html

__all__ = ['Strong', 'Emphasis', 'InlineCode', 'Strikethrough',
           'Link', 'RawText']

class LeafToken(object):
    def __init__(self, content):
        self.children = tokenize_inner(content)

class Strong(LeafToken):
    # pre: raw = "**some string**"
    def __init__(self, raw):
        super().__init__(raw[2:-2])

class Emphasis(LeafToken):
    # pre: raw = "*some string*"
    def __init__(self, raw):
        super().__init__(raw[1:-1])

class InlineCode(LeafToken):
    # pre: raw = "`some code`"
    def __init__(self, raw):
        super().__init__(raw[1:-1])

class Strikethrough(LeafToken):
    def __init__(self, raw):
        super().__init__(raw[2:-2])

class Link(LeafToken):
    # pre: raw = "[link name](link target)"
    def __init__(self, raw):
        self.name = raw[1:raw.index(']')]
        self.target = raw[raw.index('(')+1:-1]

class RawText(LeafToken):
    def __init__(self, content):
        self.content = content

def tokenize_inner(content):
    tokens = []
    re_strg = re.compile(r"\*\*(.+)\*\*|__(.+)__")
    re_emph = re.compile(r"\*(.+)\*|_(.+)_")
    re_code = re.compile(r"`(.+)`")
    re_thru = re.compile(r"~~(.+)~~")
    re_link = re.compile(r"\[(.+)\]\((.+)\)")

    def append_token(token_type, match_obj, content):
        index = match_obj.end()
        tokens.append(token_type(content[:index]))
        tokenize_inner_helper(content[index:])

    def append_raw_text(content):
        try:                  # next token
            matches = [re_strg.search(content),
                       re_emph.search(content),
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
        if re_strg.match(content):      # strong
            append_token(Strong, re_strg.match(content), content)
        elif re_emph.match(content):    # emphasis
            append_token(Emphasis, re_emph.match(content), content)
        elif re_code.match(content):    # inline code
            append_token(InlineCode, re_code.match(content), content)
        elif re_thru.match(content):
            append_token(Strikethrough, re_thru.match(content), content)
        elif re_link.match(content):    # link
            append_token(Link, re_link.match(content), content)
        else:                           # raw text
            append_raw_text(content)

    tokenize_inner_helper(content)
    return tokens

