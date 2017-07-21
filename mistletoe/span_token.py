import re
import mistletoe.span_tokenizer as tokenizer

__all__ = ['EscapeSequence', 'Emphasis', 'Strong', 'InlineCode',
           'Strikethrough', 'Image', 'Link', 'AutoLink']

def tokenize_inner(content):
    token_types = [globals()[key] for key in __all__]
    fallback_token = RawText
    return tokenizer.tokenize(content, token_types, fallback_token)

class SpanToken(object):
    def __init__(self, content):
        self.children = tokenize_inner(content)

class Strong(SpanToken):
    pattern = re.compile(r"\*\*(.+?)\*\*(?!\*)|__(.+)__(?!_)")

class Emphasis(SpanToken):
    pattern = re.compile(r"\*((?:\*\*|[^\*])+?)\*(?!\*)|_((?:__|[^_])+?)_")

class InlineCode(SpanToken):
    pattern = re.compile(r"`(.+?)`")

class Strikethrough(SpanToken):
    pattern = re.compile(r"~~(.+)~~")

class Image(SpanToken):
    pattern = re.compile(r"(\!\[(.+?)\]\((.+?)\))")
    def __init__(self, raw):
        self.alt = raw[2:raw.index(']')]
        src = raw[raw.index('(')+1:-1]
        if src.find('"') != -1:
            self.src = src[:src.index(' "')]
            self.title = src[src.index(' "')+2:-1]
        else:
            self.src = src
            self.title = ''

class Link(SpanToken):
    pattern = re.compile(r"(\[((?:!\[(.+?)\]\((.+?)\))|(?:.+?))\]\((.+?)\))")
    def __init__(self, raw):
        split_index = len(raw) - raw[::-1].index(']') - 1
        super().__init__(raw[1:split_index])
        self.target = raw[split_index+2:-1]

class AutoLink(SpanToken):
    pattern = re.compile(r"<(.+?)>")
    def __init__(self, raw):
        self.name = raw
        self.target = raw

class EscapeSequence(SpanToken):
    pattern = re.compile(r"\\([\*\(\)\[\]\~])")
    def __init__(self, raw):
        self.content = raw

class RawText(SpanToken):
    def __init__(self, content):
        self.content = content
