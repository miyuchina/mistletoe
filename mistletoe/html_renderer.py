"""
HTML renderer for mistletoe.
"""

import html
import re
import sys
from itertools import chain
from typing import Dict, Tuple, Union
from urllib.parse import quote
from mistletoe import block_token
from mistletoe import span_token
from mistletoe.block_token import HTMLBlock
from mistletoe.span_token import HTMLSpan
from mistletoe.base_renderer import BaseRenderer

Attributes = Union[Dict[str, str], Tuple[()]]
"""
You can specify HTML attributes as a dictionary mapping strings to strings.
The dictionary values are automatically HTMl escaped for you.

If you don't need any attributes, you can also specify an empty tuple.
"""

class HTMLRenderer(BaseRenderer):
    """
    HTML renderer class.

    See mistletoe.base_renderer module for more info.

    Some methods of the `HTMLRenderer` class take an optional `Attributes`
    argument letting you easily add custom HTML attributes, for example::

        class MyRenderer(HTMLRenderer):
            def render_heading(self, token):
                return super().render_heading(
                    token, attr={'id': self.stringify(token).replace(' ', '-')}
                )
    """
    def __init__(self, *extras):
        """
        Args:
            extras (list): allows subclasses to add even more custom tokens.
        """
        self._suppress_ptag_stack = [False]
        super().__init__(*chain((HTMLBlock, HTMLSpan), extras))
        # html.entities.html5 includes entitydefs not ending with ';',
        # CommonMark seems to hate them, so...
        self._stdlib_charref = html._charref
        _charref = re.compile(r'&(#[0-9]+;'
                              r'|#[xX][0-9a-fA-F]+;'
                              r'|[^\t\n\f <&#;]{1,32};)')
        html._charref = _charref

    def __exit__(self, *args):
        super().__exit__(*args)
        html._charref = self._stdlib_charref

    def stringify(self, token) -> str:
        if hasattr(token, 'children'):
            inner = [self.stringify(child) for child in token.children]
            return ''.join(inner)
        return token.content

    def render_to_plain(self, token) -> str:
        return html.escape(self.stringify(token))

    def render_strong(self, token: span_token.Strong) -> str:
        template = '<strong>{}</strong>'
        return template.format(self.render_inner(token))

    def render_emphasis(self, token: span_token.Emphasis) -> str:
        template = '<em>{}</em>'
        return template.format(self.render_inner(token))

    def render_inline_code(self, token: span_token.InlineCode) -> str:
        template = '<code>{}</code>'
        inner = html.escape(token.children[0].content)
        return template.format(inner)

    def render_strikethrough(self, token: span_token.Strikethrough) -> str:
        template = '<del>{}</del>'
        return template.format(self.render_inner(token))

    def render_image(self, token: span_token.Image, attr: Attributes = ()) -> str:
        template = '<img{} />'
        attributes = {'src': token.src, 'alt': self.render_to_plain(token)}
        if token.title:
            attributes['title'] = token.title
        attributes.update(attr)
        return template.format(self._render_attributes(attributes))

    def render_link(self, token: span_token.Link, attr: Attributes = ()) -> str:
        template = '<a{attr}>{inner}</a>'
        attributes = {'href': self.quote_url(token.target)}
        if token.title:
            attributes['title'] = token.title
        attributes.update(attr)
        inner = self.render_inner(token)
        return template.format(inner=inner, attr=self._render_attributes(attributes))

    def render_auto_link(self, token: span_token.AutoLink, attr: Attributes = ()) -> str:
        template = '<a{attr}>{inner}</a>'
        attributes = {'href': 'mailto:{}'.format(token.target) if token.mailto else self.quote_url(token.target)}
        attributes.update(attr)
        inner = self.render_inner(token)
        return template.format(inner=inner, attr=self._render_attributes(attributes))

    def render_escape_sequence(self, token: span_token.EscapeSequence) -> str:
        return self.render_inner(token)

    def render_raw_text(self, token: span_token.RawText) -> str:
        return html.escape(token.content)

    @staticmethod
    def render_html_span(token: span_token.HTMLSpan) -> str:
        return token.content

    def render_heading(self, token: block_token.Heading, attr: Attributes = ()) -> str:
        template = '<h{level}{attr}>{inner}</h{level}>'
        inner = self.render_inner(token)
        return template.format(level=token.level, inner=inner, attr=self._render_attributes(attr))

    def render_quote(self, token: block_token.Quote, attr: Attributes = ()) -> str:
        elements = ['<blockquote{}>'.format(self._render_attributes(attr))]
        self._suppress_ptag_stack.append(False)
        elements.extend([self.render(child) for child in token.children])
        self._suppress_ptag_stack.pop()
        elements.append('</blockquote>')
        return '\n'.join(elements)

    def render_paragraph(self, token: block_token.Paragraph) -> str:
        if self._suppress_ptag_stack[-1]:
            return '{}'.format(self.render_inner(token))
        return '<p>{}</p>'.format(self.render_inner(token))

    def render_block_code(self, token: block_token.BlockCode, attr: Attributes = ()) -> str:
        template = '<pre><code{attr}>{inner}</code></pre>'
        attributes = {}
        if token.language:
            attributes['class'] = 'language-{}'.format(token.language)
        attributes.update(attr)
        inner = html.escape(token.children[0].content)
        return template.format(inner=inner, attr=self._render_attributes(attributes))

    def render_list(self, token: block_token.List, attr: Attributes = ()) -> str:
        template = '<{tag}{attr}>\n{inner}\n</{tag}>'
        attributes = {}
        if token.start is not None:
            tag = 'ol'
            if token.start != 1:
                attributes['start'] = str(token.start)
        else:
            tag = 'ul'
        attributes.update(attr)
        self._suppress_ptag_stack.append(not token.loose)
        inner = '\n'.join([self.render(child) for child in token.children])
        self._suppress_ptag_stack.pop()
        return template.format(tag=tag, inner=inner, attr=self._render_attributes(attributes))

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
        return '<li>{}</li>'.format(inner_template.format(inner))

    def render_table(self, token: block_token.Table, attr: Attributes = ()) -> str:
        # This is actually gross and I wonder if there's a better way to do it.
        #
        # The primary difficulty seems to be passing down alignment options to
        # reach individual cells.
        template = '<table{attr}>\n{inner}</table>'
        if hasattr(token, 'header'):
            head_template = '<thead>\n{inner}</thead>\n'
            head_inner = self.render_table_row(token.header, is_header=True)
            head_rendered = head_template.format(inner=head_inner)
        else: head_rendered = ''
        body_template = '<tbody>\n{inner}</tbody>\n'
        body_inner = self.render_inner(token)
        body_rendered = body_template.format(inner=body_inner)
        return template.format(inner=head_rendered+body_rendered, attr=self._render_attributes(attr))

    def render_table_row(self, token: block_token.TableRow, is_header=False) -> str:
        template = '<tr>\n{inner}</tr>\n'
        inner = ''.join([self.render_table_cell(child, is_header)
                         for child in token.children])
        return template.format(inner=inner)

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

    @staticmethod
    def render_thematic_break(token: block_token.ThematicBreak) -> str:
        return '<hr />'

    @staticmethod
    def render_line_break(token: span_token.LineBreak) -> str:
        return '\n' if token.soft else '<br />\n'

    @staticmethod
    def render_html_block(token: block_token.HTMLBlock) -> str:
        return token.content

    def render_document(self, token: block_token.Document) -> str:
        self.footnotes.update(token.footnotes)
        inner = '\n'.join([self.render(child) for child in token.children])
        return '{}\n'.format(inner) if inner else ''

    @staticmethod
    def escape_html(raw: str) -> str:
        """
        This method is deprecated. Use `html.escape` instead.
        """
        return html.escape(raw)

    @staticmethod
    def quote_url(raw: str) -> str:
        """
        Percent-encode URLs.
        """
        return quote(raw, safe='/#:()*?=%@+,&;')

    @classmethod
    def escape_url(cls, raw: str) -> str:
        """
        URL-quote and HTML escape the given string.
        """
        return html.escape(cls.quote_url(raw))
        return html.escape(quote(raw, safe='/#:()*?=%@+,&;'))

    @classmethod
    def _render_attributes(cls, attrs: Attributes) -> str:
        if len(attrs) == 0:
            return ''
        else:
            return ' ' + ' '.join('{}="{}"'.format(k, cls.escape_html(attrs[k])) for k in attrs)
