"""
HTML Attributes renderer for mistletoe.
"""

import html
from mistletoe import block_token
from mistletoe import span_token
from mistletoe.block_token import HTMLAttributes
from mistletoe.html_renderer import HTMLRenderer


class HTMLAttributesRenderer(HTMLRenderer):
    """
    HTML Attributes renderer class.

    See mistletoe.html_renderer module for more info.
    """
    def __init__(self, *extras):
        """
        Args:
            extras (list): allows subclasses to add even more custom tokens.
        """
        super().__init__(HTMLAttributes, *extras)
        self.RENDERER_START = False

    def render(self, token):
        """
        Grabs the class name from input token and finds its corresponding
        render function.

        Basically a janky way to do polymorphism.

        Arguments:
            token: whose __class__.__name__ is in self.render_map.
        """
        # reconcile our htmlattributes
        if not self.RENDERER_START: 
            self.reconcile_attrs(token)
        return self.render_map[token.__class__.__name__](token)

    def reconcile_attrs(self, doc_token):
        """Traverse token children while assigning html attributes if available"""
        self.RENDERER_START = True
        recon_tokens = []
        htmlAttributesToken: block_token.HTMLAttributes = None
        for token_type in doc_token.children:
            if 'HTMLAttributes' == token_type.__class__.__name__: 
                htmlAttributesToken = token_type
                continue
            if htmlAttributesToken: 
                htmlAttributesToken.apply_props(token_type)
                htmlAttributesToken.clear()
                htmlAttributesToken = None
            recon_tokens.append(token_type)
        doc_token.children = recon_tokens

    def render_html_attributes(self, token: block_token) -> str:
        return '' if not hasattr(token,'html_props') else token.html_props

    def render_image(self, token: span_token.Image) -> str:
        template = '<img src="{}" alt="{}"{}{attrs} />'
        title = ' title="{}"'.format(html.escape(token.title)) if token.title else ''
        attrs = self.render_html_attributes(token)
        return template.format(token.src, self.render_to_plain(token), title, attrs=attrs)

    def render_link(self, token: span_token.Link) -> str:
        template = '<a href="{target}"{title}{attr}>{inner}</a>'
        target = self.escape_url(token.target)
        if token.title:
            title = ' title="{}"'.format(html.escape(token.title))
        else:
            title = ''
        inner = self.render_inner(token)
        attr = '' if not hasattr(token,'html_props') else token.html_props
        return template.format(target=target, title=title, inner=inner, attr=attr)

    def render_auto_link(self, token: span_token.AutoLink) -> str:
        template = '<a href="{target}"{attr}>{inner}</a>'
        if token.mailto:
            target = 'mailto:{}'.format(token.target)
        else:
            target = self.escape_url(token.target)
        inner = self.render_inner(token)
        attr = '' if not hasattr(token,'html_props') else token.html_props
        return template.format(target=target, inner=inner, attr=attr)

    def render_heading(self, token: block_token.Heading) -> str:
        template = '<h{level}{attr}>{inner}</h{level}>'
        inner = self.render_inner(token)
        attr = '' if not hasattr(token,'html_props') else token.html_props
        return template.format(level=token.level, attr=attr, inner=inner)

    def render_quote(self, token: block_token.Quote) -> str:
        attr = '' if not hasattr(token,'html_props') else token.html_props
        elements = [f'<blockquote{attr}>']
        self._suppress_ptag_stack.append(False)
        elements.extend([self.render(child) for child in token.children])
        self._suppress_ptag_stack.pop()
        elements.append('</blockquote>')
        return '\n'.join(elements)

    def render_paragraph(self, token: block_token.Paragraph) -> str:
        if self._suppress_ptag_stack[-1]:
            return '{}'.format(self.render_inner(token))
        attrs = '' if not hasattr(token,'html_props') else token.html_props
        return '<p{attrs}>{}</p>'.format(self.render_inner(token), attrs=attrs)

    # def render_block_code(self, token: block_token.BlockCode) -> str:
    #     template = '<pre{attrs}><code{attr}>{inner}</code></pre>'
    #     if token.language:
    #         attr = ' class="{}"'.format('language-{}'.format(html.escape(token.language)))
    #     else:
    #         attr = ''
    #     inner = html.escape(token.children[0].content)
    #     attrs = '' if not hasattr(token,'html_props') else token.html_props
    #     return template.format(attr=attr, inner=inner, attrs=attrs)

    def render_list(self, token: block_token.List) -> str:
        template = '<{tag}{olattr}{attrs}>\n{inner}\n</{tag}>'
        attrs = '' if not hasattr(token,'html_props') else token.html_props
        tag = 'ol' if token.start is not None else 'ul'
        olattr = ' start="{}"'.format(token.start) if tag == 'ol' else ''
        self._suppress_ptag_stack.append(not token.loose)
        inner = '\n'.join([self.render(child) for child in token.children])
        self._suppress_ptag_stack.pop()
        return template.format(tag=tag, olattr=olattr, attrs=attrs, inner=inner)

    def render_list_item(self, token: block_token.ListItem) -> str:
        if len(token.children) == 0:
            return '<li></li>'
        inner = '\n'.join([self.render(child) for child in token.children])
        inner_template = '\n{}\n'
        if self._suppress_ptag_stack[-1]:
            if token.children[0].__class__.__name__ == 'Paragraph':
                inner_template = inner_template[1:]
            if token.children[-1].__class__.__name__ == 'Paragraph':
                inner_template = inner_template[:-1]
        attrs = '' if not hasattr(token,'html_props') else token.html_props
        return '<li{attrs}>{}</li>'.format(inner_template.format(inner), attrs=attrs)

    def render_table(self, token: block_token.Table) -> str:
        # This is actually gross and I wonder if there's a better way to do it.
        #
        # The primary difficulty seems to be passing down alignment options to
        # reach individual cells.
        template = '<table{attrs}>\n{inner}</table>'
        if hasattr(token, 'header'):
            head_template = '<thead>\n{inner}</thead>\n'
            head_inner = self.render_table_row(token.header, is_header=True)
            head_rendered = head_template.format(inner=head_inner)
        else: head_rendered = ''
        body_template = '<tbody>\n{inner}</tbody>\n'
        body_inner = self.render_inner(token)
        body_rendered = body_template.format(inner=body_inner)
        attrs = '' if not hasattr(token,'html_props') else token.html_props
        return template.format(inner=head_rendered+body_rendered, attrs=attrs)

    def render_table_row(self, token: block_token.TableRow, is_header=False) -> str:
        template = '<tr{attrs}>\n{inner}</tr>\n'
        inner = ''.join([self.render_table_cell(child, is_header)
                         for child in token.children])
        attrs = '' if not hasattr(token,'html_props') else token.html_props
        return template.format(inner=inner, attrs=attrs)

    def render_table_cell(self, token: block_token.TableCell, in_header=False) -> str:
        template = '<{tag}{attr}>{inner}</{tag}>\n'
        tag = 'th' if in_header else 'td'
        if token.align is None:
            align = 'left'
        elif token.align == 0:
            align = 'center'
        elif token.align == 1:
            align = 'right'
        attr = ' align="{}"'.format(align)
        inner = self.render_inner(token)
        return template.format(tag=tag, attr=attr, inner=inner)

    def render_document(self, token: block_token.Document) -> str:
        self.footnotes.update(token.footnotes)
        inner = '\n'.join([self.render(child) for child in token.children])
        doc_html = '{}\n'.format(inner) if inner else ''
        self.RENDERER_START = False
        return doc_html