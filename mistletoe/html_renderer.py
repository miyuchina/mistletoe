"""
HTML renderer for mistletoe.
"""

import html
from itertools import chain
import mistletoe.html_token as html_token
from mistletoe.base_renderer import BaseRenderer

class HTMLRenderer(BaseRenderer):
    """
    HTML renderer class.

    See mistletoe.base_renderer module for more info.
    """
    def __init__(self, *extras):
        """
        Args:
            extras (list): allows subclasses to add even more custom tokens.
        """
        tokens = self._tokens_from_module(html_token)
        super().__init__(*chain(tokens, extras))

    def render_strong(self, token, footnotes):
        template = '<strong>{}</strong>'
        return template.format(self.render_inner(token, footnotes))

    def render_emphasis(self, token, footnotes):
        template = '<em>{}</em>'
        return template.format(self.render_inner(token, footnotes))

    def render_inline_code(self, token, footnotes):
        template = '<code>{}</code>'
        return template.format(self.render_inner(token, footnotes))

    def render_strikethrough(self, token, footnotes):
        template = '<del>{}</del>'
        return template.format(self.render_inner(token, footnotes))

    def render_image(self, token, footnotes):
        template = '<img src="{}" title="{}" alt="{}">'
        inner = self.render_inner(token)
        return template.format(token.src, token.title, inner)

    def render_footnote_image(self, token, footnotes):
        template = '<img src="{src}" title="{title}" alt="{inner}">'
        maybe_src = footnotes.get(token.src.key, '')
        if maybe_src.find('"') != -1:
            src = maybe_src[:maybe_src.index(' "')]
            title = maybe_src[maybe_src.index(' "')+2:-1]
        else:
            src = maybe_src
            title = ''
        inner = self.render_inner(token, footnotes)
        return template.format(src=src, title=title, inner=inner)

    def render_link(self, token, footnotes):
        template = '<a href="{target}">{inner}</a>'
        target = escape_url(token.target)
        inner = self.render_inner(token, footnotes)
        return template.format(target=target, inner=inner)

    def render_footnote_link(self, token, footnotes):
        template = '<a href="{target}">{inner}</a>'
        raw_target = footnotes.get(token.target.key, '')
        target = escape_url(raw_target)
        inner = self.render_inner(token, footnotes)
        return template.format(target=target, inner=inner)

    def render_auto_link(self, token, footnotes):
        template = '<a href="{target}">{inner}</a>'
        target = escape_url(token.target)
        inner = self.render_inner(token, footnotes)
        return template.format(target=target, inner=inner)

    def render_escape_sequence(self, token, footnotes):
        return self.render_inner(token, footnotes)

    @staticmethod
    def render_raw_text(token, footnotes):
        return html.escape(token.content)

    @staticmethod
    def render_html_span(token, footnotes):
        return token.content

    def render_heading(self, token, footnotes):
        template = '<h{level}>{inner}</h{level}>\n'
        inner = self.render_inner(token, footnotes)
        return template.format(level=token.level, inner=inner)

    def render_quote(self, token, footnotes):
        template = '<blockquote>\n{inner}</blockquote>\n'
        return template.format(inner=self.render_inner(token, footnotes))

    def render_paragraph(self, token, footnotes):
        return '<p>{}</p>\n'.format(self.render_inner(token, footnotes))

    def render_block_code(self, token, footnotes):
        template = '<pre>\n<code{attr}>\n{inner}</code>\n</pre>\n'
        if token.language:
            attr = ' class="{}"'.format('lang-{}'.format(token.language))
        else:
            attr = ''
        inner = self.render_inner(token, footnotes)
        return template.format(attr=attr, inner=inner)

    def render_list(self, token, footnotes):
        template = '<{tag}{attr}>\n{inner}</{tag}>\n'
        if token.start:
            tag = 'ol'
            attr = ' start="{}"'.format(token.start)
        else:
            tag = 'ul'
            attr = ''
        inner = self.render_inner(token, footnotes)
        return template.format(tag=tag, attr=attr, inner=inner)

    def render_list_item(self, token, footnotes):
        return '<li>{}</li>\n'.format(self.render_inner(token, footnotes))

    def render_table(self, token, footnotes):
        # This is actually gross and I wonder if there's a better way to do it.
        #
        # The primary difficulty seems to be passing down alignment options to
        # reach individual cells.
        template = '<table>\n{inner}</table>\n'
        if token.has_header:
            head_template = '<thead>\n{inner}</thead>\n'
            header = next(token.children)
            head_inner = self.render_table_row(header, footnotes, True)
            head_rendered = head_template.format(inner=head_inner)
        else: head_rendered = ''
        body_template = '<tbody>\n{inner}</tbody>\n'
        body_inner = self.render_inner(token, footnotes)
        body_rendered = body_template.format(inner=body_inner)
        return template.format(inner=head_rendered+body_rendered)

    def render_table_row(self, token, footnotes, is_header=False):
        template = '<tr>\n{inner}</tr>\n'
        inner = ''.join([self.render_table_cell(child, footnotes, is_header)
                         for child in token.children])
        return template.format(inner=inner)

    def render_table_cell(self, token, footnotes, in_header=False):
        template = '<{tag}{attr}>{inner}</{tag}>\n'
        tag = 'th' if in_header else 'td'
        if token.align is None:
            align = 'left'
        elif token.align == 0:
            align = 'center'
        elif token.align == 1:
            align = 'right'
        attr = ' align="{}"'.format(align)
        inner = self.render_inner(token, footnotes)
        return template.format(tag=tag, attr=attr, inner=inner)

    @staticmethod
    def render_separator(token, footnotes):
        return '<hr>\n'

    @staticmethod
    def render_html_block(token, footnotes):
        return token.content

    def render_document(self, token, footnotes):
        return self.render_inner(token, token.footnotes)

def escape_url(raw):
    """
    Escape urls to prevent code injection craziness. (Hopefully.)
    """
    from urllib.parse import quote
    return quote(raw, safe='/#:')
