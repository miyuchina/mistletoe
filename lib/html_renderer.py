import html

class HTMLRenderer(object):
    def __init__(self):
        self.render_map = {
                'Strong':         self.render_strong,
                'Emphasis':       self.render_emphasis,
                'InlineCode':     self.render_inline_code,
                'RawText':        self.render_raw_text,
                'Strikethrough':  self.render_strikethrough,
                'Image':          self.render_image,
                'Link':           self.render_link,
                'EscapeSequence': self.render_raw_text,
                'Heading':        self.render_heading,
                'Quote':          self.render_quote,
                'Paragraph':      self.render_paragraph,
                'BlockCode':      self.render_block_code,
                'List':           self.render_list,
                'ListItem':       self.render_list_item,
                'Table':          self.render_table,
                'TableRow':       self.render_table_row,
                'TableCell':      self.render_table_cell,
                'Separator':      self.render_separator,
                'Document':       self.render_document,
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
        tp = '<img src="{}" title="{}" alt="{}">'
        return tp.format(token.src, token.title, token.alt)

    def render_link(self, token):
        tp = '<a href="{}">{}</a>'
        return tp.format(token.target, self.render_inner(token))

    def render_raw_text(self, token):
        return html.escape(token.content)

    def render_heading(self, token):
        tp = '<h{level}>{inner}</h{level}>'
        return tp.format(level=token.level, inner=self.render_inner(token))

    def render_quote(self, token):
        tp = '<blockquote>{inner}</blockquote>'
        return tp.format(inner=self.render_inner(token))

    def render_paragraph(self, token):
        return '<p>{}</p>'.format(self.render_inner(token))

    def render_block_code(self, token):
        tp = '<pre><code class="lang-{}">{}</code></pre>'
        return tp.format(token.language, self.render_inner(token))

    def render_list(self, token):
        tp = '<{tag}{attr}>{inner}</{tag}>'
        if hasattr(token, 'start'):
            tag = 'ol'
            attr = ' start="{}"'.format(token.start)
        else:
            tag = 'ul'
            attr = ''
        inner = self.render_inner(token)
        return tp.format(tag=tag, attr=attr, inner=inner)

    def render_list_item(self, token):
        return '<li>{}</li>'.format(self.render_inner(token))

    def render_table(self, token):
        tp = '<table>{inner}</table>'
        if token.has_header:
            head_tp = '<thead>{inner}</thead>'
            header = token.children.send(None)
            head_inner = self.render_table_row(header, True)
            head_rendered = head_tp.format(inner=head_inner)
        else: head_rendered = ''
        body_tp = '<tbody>{inner}</tbody>'
        body_inner = self.render_inner(token)
        body_rendered = body_tp.format(inner=body_inner)
        return tp.format(inner=head_rendered+body_rendered)

    def render_table_row(self, token, is_header=False):
        tp = '<tr>{inner}</tr>'
        inner = ''.join([ self.render_table_cell(child, is_header)
                                        for child in token.children ])
        return tp.format(inner=inner)

    def render_table_cell(self, token, in_header=False):
        tp = '<{tag}{attr}>{inner}</{tag}>'
        tag = 'th' if in_header else 'td'
        if token.align is None: align = 'left'
        elif token.align == 0 : align = 'center'
        elif token.align == 1 : align = 'right'
        attr = ' align="{}"'.format(align)
        inner = self.render_inner(token)
        return tp.format(tag=tag, attr=attr, inner=inner)

    def render_separator(self, token):
        return '<hr>'

    def render_document(self, token):
        tp = '<html><body>{inner}</body></html>'
        return tp.format(inner=self.render_inner(token))
