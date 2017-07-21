import re
import html
import urllib.parse
import mistletoe
import mistletoe.html_renderer

class GitHubWiki(mistletoe.span_token.SpanToken):
    pattern = re.compile(r"(\[\[(.+?)\|(.+?)\]\])")
    def __init__(self, raw):
        alt, target = raw[2:-2].split('|', 1)
        super().__init__(alt)
        self.target = target

class CustomRenderer(mistletoe.html_renderer.HTMLRenderer):
    def __init__(self, preamble=''):
        super().__init__(preamble)
        self.render_map['GitHubWiki'] = self.render_github_wiki

    def render_github_wiki(self, token):
        template = '<a href="{target}">{inner}</a>'
        target = urllib.parse.quote_plus(target)
        inner = self.render_inner(token)
        return template.format(target=target, inner=inner)

mistletoe.span_token.GitHubWiki = GitHubWiki
mistletoe.span_token.__all__.append('GitHubWiki')

if __name__ == '__main__':
    lines = ['# GitHub Wiki link demo\n',
             'A block-level token that\n',
             'contains a [[Github Wiki|target]]\n',
             'link.\n']
    token = mistletoe.block_token.Document(lines)
    print(CustomRenderer().render(token))
