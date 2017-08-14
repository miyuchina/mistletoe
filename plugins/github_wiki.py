"""
GitHub Wiki support for mistletoe.
"""

import re
import html
from mistletoe.span_token import SpanToken
from mistletoe.html_renderer import HTMLRenderer, escape_url

__all__ = ['GithubWiki', 'GithubWikiRenderer']

class GithubWiki(SpanToken):
    pattern = re.compile(r"(\[\[(.+?)\|(.+?)\]\])")
    def __init__(self, raw):
        alt, target = raw[2:-2].split('|', 1)
        super().__init__(alt.strip())
        self.target = target.strip()

class GithubWikiRenderer(HTMLRenderer):
    def __init__(self):
        super().__init__(GithubWiki)

    def render_github_wiki(self, token, footnotes):
        template = '<a href="{target}">{inner}</a>'
        target = escape_url(token.target)
        inner = self.render_inner(token, footnotes)
        return template.format(target=target, inner=inner)
