import re
import html
import urllib.parse
import mistletoe
import mistletoe.html_token
from mistletoe.html_renderer import HTMLRenderer
from mistletoe.span_token import SpanToken

__all__ = ['GitHubWiki', 'GitHubWikiRenderer']

class Context(object):
    def __init__(self):
        self.renderer = GitHubWikiRenderer

    def __enter__(self):
        mistletoe.span_token.GitHubWiki = GitHubWiki
        mistletoe.span_token.__all__.append('GitHubWiki')
        return self

    def __exit__(self, exception_type, exception_val, traceback):
        del mistletoe.span_token.GitHubWiki
        mistletoe.span_token.__all__.remove('GitHubWiki')

    def render(self, token):
        return self.renderer().render(token)

class GitHubWiki(SpanToken):
    pattern = re.compile(r"(\[\[(.+?)\|(.+?)\]\])")
    def __init__(self, raw):
        alt, target = raw[2:-2].split('|', 1)
        super().__init__(alt.strip())
        self.target = target.strip()

class GitHubWikiRenderer(HTMLRenderer):
    def __init__(self, preamble=''):
        super().__init__(preamble)
        self.render_map['GitHubWiki'] = self.render_github_wiki

    def render_github_wiki(self, token):
        template = '<a href="{target}">{inner}</a>'
        target = urllib.parse.quote_plus(token.target)
        inner = self.render_inner(token)
        return template.format(target=target, inner=inner)

if __name__ == '__main__':
    lines = ['# GitHub Wiki link demo\n',
             'A block-level token that\n',
             'contains a [[Github Wiki|target]]\n',
             'link.\n']
    with mistletoe.html_token.Context(), Context() as c:
        token = mistletoe.Document(lines)
        print(c.render(token))
