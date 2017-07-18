import html

class HTMLRenderer(object):
    def __init__(self):
        self.render_map = {
            'Strong': '<strong>{_inner}</strong>',
            'Emphasis': '<em>{_inner}</em>',
            'InlineCode': '<code>{_inner}</code>',
            'RawText': '{_escape}',
            'Strikethrough': '<del>{_inner}</del>',
            'Image': '<img src="{src}" title="{title}" alt="{alt}">',
            'Link': '<a href="{target}">{_inner}</a>',
            'EscapeSequence': '{_escape}'
        }

    def render(self, token):
        return self.render_span(token)

    def render_span(self, token):
        template = self.render_map[type(token).__name__]
        if hasattr(token, 'children'): self.render_inner(token)
        elif hasattr(token, 'content'): self.escape_content(token)
        return template.format(**token.__dict__)

    def render_inner(self, token):
        inner = [ self.render_span(child) for child in token.children ]
        token._inner = ''.join(inner)

    def escape_content(self, token):
        token._escape = html.escape(token.content)
