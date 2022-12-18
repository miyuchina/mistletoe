"""
HTML renderer for mistletoe.
"""

import html
import re
from itertools import chain
from urllib.parse import quote
from mistletoe import block_token
from mistletoe import span_token
from mistletoe.block_token import HTMLBlock
from mistletoe.span_token import HTMLSpan
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

    def render_to_plain(self, token) -> str:
        if hasattr(token, 'children'):
            inner = [self.render_to_plain(child) for child in token.children]
            return ''.join(inner)
        return html.escape(token.content)

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

    def render_image(self, token: span_token.Image) -> str:
        template = '<img src="{}" alt="{}"{} />'
        if token.title:
            title = ' title="{}"'.format(html.escape(token.title))
        else:
            title = ''
        return template.format(token.src, self.render_to_plain(token), title)

    def render_link(self, token: span_token.Link) -> str:
        template = '<a href="{target}"{title}>{inner}</a>'
        target = self.escape_url(token.target)
        if token.title:
            title = ' title="{}"'.format(html.escape(token.title))
        else:
            title = ''
        inner = self.render_inner(token)
        return template.format(target=target, title=title, inner=inner)

    def render_auto_link(self, token: span_token.AutoLink) -> str:
        template = '<a href="{target}">{inner}</a>'
        if token.mailto:
            target = 'mailto:{}'.format(token.target)
        else:
            target = self.escape_url(token.target)
        inner = self.render_inner(token)
        return template.format(target=target, inner=inner)

    def render_escape_sequence(self, token: span_token.EscapeSequence) -> str:
        return self.render_inner(token)

    def render_raw_text(self, token: span_token.RawText) -> str:
        return html.escape(token.content)

    @staticmethod
    def render_html_span(token: span_token.HTMLSpan) -> str:
        return token.content

    def render_heading(self, token: block_token.Heading) -> str:
        template = '<h{level}>{inner}</h{level}>'
        inner = self.render_inner(token)
        return template.format(level=token.level, inner=inner)

    def render_quote(self, token: block_token.Quote) -> str:
        elements = ['<blockquote>']
        self._suppress_ptag_stack.append(False)
        elements.extend([self.render(child) for child in token.children])
        self._suppress_ptag_stack.pop()
        elements.append('</blockquote>')
        return '\n'.join(elements)

    def render_paragraph(self, token: block_token.Paragraph) -> str:
        if self._suppress_ptag_stack[-1]:
            return '{}'.format(self.render_inner(token))
        return '<p>{}</p>'.format(self.render_inner(token))

    def render_block_code(self, token: block_token.BlockCode) -> str:
        template = '<pre><code{attr}>{inner}</code></pre>'
        if token.language:
            attr = ' class="{}"'.format('language-{}'.format(html.escape(token.language)))
        else:
            attr = ''
        inner = html.escape(token.children[0].content)
        return template.format(attr=attr, inner=inner)

    def render_list(self, token: block_token.List) -> str:
        template = '<{tag}{attr}>\n{inner}\n</{tag}>'
        if token.start is not None:
            tag = 'ol'
            attr = ' start="{}"'.format(token.start) if token.start != 1 else ''
        else:
            tag = 'ul'
            attr = ''
        self._suppress_ptag_stack.append(not token.loose)
        inner = '\n'.join([self.render(child) for child in token.children])
        self._suppress_ptag_stack.pop()
        return template.format(tag=tag, attr=attr, inner=inner)

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

    def render_table(self, token: block_token.Table) -> str:
        # This is actually gross and I wonder if there's a better way to do it.
        #
        # The primary difficulty seems to be passing down alignment options to
        # reach individual cells.
        template = '<table>\n{inner}</table>'
        if hasattr(token, 'header'):
            head_template = '<thead>\n{inner}</thead>\n'
            head_inner = self.render_table_row(token.header, is_header=True)
            head_rendered = head_template.format(inner=head_inner)
        else: head_rendered = ''
        body_template = '<tbody>\n{inner}</tbody>\n'
        body_inner = self.render_inner(token)
        body_rendered = body_template.format(inner=body_inner)
        return template.format(inner=head_rendered+body_rendered)

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
    def escape_url(raw: str) -> str:
        """
        Escape urls to prevent code injection craziness. (Hopefully.)
        """
        return html.escape(quote(raw, safe='/#:()*?=%@+,&;'))
