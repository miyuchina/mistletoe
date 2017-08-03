import re
import html
import mistletoe.span_token as span_token
from mistletoe.html_renderer import HTMLRenderer, escape_url

__all__ = ['GitHubWiki', 'GitHubWikiRenderer']

class GitHubWiki(span_token.SpanToken):
    pattern = re.compile(r"(\[\[(.+?)\|(.+?)\]\])")
    def __init__(self, raw):
        alt, target = raw[2:-2].split('|', 1)
        super().__init__(alt.strip())
        self.target = target.strip()

class GitHubWikiRenderer(HTMLRenderer):
    def __init__(self, preamble=''):
        super().__init__(preamble)
        self.render_map['GitHubWiki'] = self.render_github_wiki

    def __enter__(self):
        span_token.GitHubWiki = GitHubWiki
        span_token.__all__.append('GitHubWiki')
        return super().__enter__()

    def __exit__(self, exception_type, exception_val, traceback):
        del span_token.GitHubWiki
        span_token.__all__.remove('GitHubWiki')
        super().__exit__(exception_type, exception_val, traceback)

    def render_github_wiki(self, token, footnotes):
        template = '<a href="{target}">{inner}</a>'
        target = escape_url(token.target)
        inner = self.render_inner(token, footnotes)
        return template.format(target=target, inner=inner)

if __name__ == '__main__':
    lines = ['# GitHub Wiki link demo\n',
             'A block-level token that\n',
             'contains a [[Github Wiki|target]]\n',
             'link.\n']
    with GitHubWikiRenderer as r:
        print(r(Document(lines)))
