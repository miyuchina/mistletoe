import html

class HTMLRenderer(object):
    def __init__(self):
        self.render_map = {
                'Strong': self.render_strong,
                'Emphasis': self.render_emphasis,
                'InlineCode': self.render_inline_code,
                'RawText': self.render_raw_text,
                'Strikethrough': self.render_strikethrough,
                'Image': self.render_image,
                'Link': self.render_link,
                'EscapeSequence': self.render_raw_text,
                }

    def render(self, token):
        return self.render_map[type(token).__name__](token)

    def render_inner(self, token):
        return ''.join( self.render(child) for child in token.children )

    def render_strong(self, token):
        return '<strong>{}</strong>'.format(self.render_inner(token))

    def render_emphasis(self, token):
        return '<em>{}</em>'.format(self.render_inner(token))

    def render_inline_code(self, token):
        return '<code>{}</code>'.format(self.render_inner(token))

    def render_strikethrough(self, token):
        return '<del>{}</del>'.format(self.render_inner(token))

    def render_image(self, token):
        tp = '<img src="{src}" title="{title}" alt="{alt}">'
        return tp.format(**token.__dict__)

    def render_link(self, token):
        tp = '<a href="{target}">{inner}</a>'
        return tp.format(target=token.target, inner=self.render_inner(token))

    def render_raw_text(self, token):
        return html.escape(token.content)
