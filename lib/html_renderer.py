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
            'EscapeSequence': '{_escape}',

            'Heading': '<h{level}>{_inner}</h{level}>',
            'Quote': '<blockquote>{_inner}</blockquote>',
            'Paragraph': '<p>{_inner}</p>',
            'BlockCode': ('<pre><code class="lang-{language}">{_inner}'
                          '</code></pre>'),
            'List': '<{_tag}{_attr}>{_inner}</{_tag}>',
            'ListItem': '<li>{_inner}</li>',
            'Document': '<html><body>{_inner}</body></html>'
        }

    def render(self, token):
        token_type = type(token).__name__
        template = self.render_map[token_type]
        if hasattr(token, 'children'): self.inner_helper(token)
        if hasattr(token, 'content'): self.escape_helper(token)
        if token_type == 'List': self.list_helper(token)
        if token_type == 'TableCell': self.table_cell_helper(token)
        return template.format(**token.__dict__)

    def inner_helper(self, token):
        inner = [ self.render(child) for child in token.children ]
        token._inner = ''.join(inner)

    def escape_helper(self, token):
        token._escape = html.escape(token.content)

    def list_helper(self, token):
        if hasattr(token, 'start'):
            token._tag = 'ol'
            token._attr = ' start="{}"'.format(token.start)
        else:
            token._tag = 'ul'
            token._attr = ''
