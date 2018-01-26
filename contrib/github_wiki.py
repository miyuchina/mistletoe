"""
GitHub Wiki support for mistletoe.
"""

import re
from mistletoe.span_token import SpanToken, tokenize_inner
from mistletoe.html_renderer import HTMLRenderer, escape_url


__all__ = ['GithubWiki', 'GithubWikiRenderer']


class GithubWiki(SpanToken):
    pattern = re.compile(r"\[\[ *(.+?) *\| *(.+?) *\]\]")
    def __init__(self, match_obj):
        super().__init__(match_obj)
        self.target = match_obj.group(2)


class GithubWikiRenderer(HTMLRenderer):
    def __init__(self):
        super().__init__(GithubWiki)

    def render_github_wiki(self, token):
        template = '<a href="{target}">{inner}</a>'
        target = escape_url(token.target)
        inner = self.render_inner(token)
        return template.format(target=target, inner=inner)
