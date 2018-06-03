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
        self._suppress_ptag_stack = [False]
        super().__init__(*chain(tokens, extras))

    def render_to_plain(self, token):
        if hasattr(token, 'children'):
            return self.render_inner(token)
        return html.escape(token.content)

    def render_strong(self, token):
        template = '<strong>{}</strong>'
        return template.format(self.render_inner(token))

    def render_emphasis(self, token):
        template = '<em>{}</em>'
        return template.format(self.render_inner(token))

    def render_inline_code(self, token):
        template = '<code>{}</code>'
        return template.format(self.render_inner(token))

    def render_strikethrough(self, token):
        template = '<del>{}</del>'
        return template.format(self.render_inner(token))

    def render_image(self, token):
        template = '<img src="{}" alt="{}"{} />'
        render_func = self.render
        self.render = self.render_to_plain
        inner = self.render_inner(token)
        self.render = render_func
        if token.title:
            title = ' title="{}"'.format(html.escape(token.title))
        else:
            title = ''
        return template.format(token.src, inner, title)

    def render_footnote_image(self, token):
        template = '<img src="{src}" alt="{inner}"{title} />'
        src = self.footnotes.get(token.src.key, '')
        if isinstance(src, tuple):
            src, title = src
            title = ' title="{}"'.format(html.escape(title))
        else:
            title = ''
        render_func = self.render
        self.render = self.render_to_plain
        inner = self.render_inner(token)
        self.render = render_func
        return template.format(src=src, title=title, inner=inner)

    def render_link(self, token):
        template = '<a href="{target}"{title}>{inner}</a>'
        target = token.target
        if token.title:
            title = ' title="{}"'.format(html.escape(token.title))
        else:
            title = ''
        inner = self.render_inner(token)
        return template.format(target=target, title=title, inner=inner)

    def render_footnote_link(self, token):
        inner = self.render_inner(token)
        key = token.target.key
        if key in self.footnotes:
            template = '<a href="{target}"{title}>{inner}</a>'
            target = self.footnotes[key]
            if isinstance(target, tuple):
                target, title = target
                title = ' title="{}"'.format(html.escape(title))
            else:
                title = ''
            return template.format(target=target, inner=inner, title=title)
        return '[{}]'.format(inner)

    def render_auto_link(self, token):
        template = '<a href="{target}">{inner}</a>'
        if token.mailto:
            target = 'mailto:{}'.format(token.target)
        else:
            target = html.escape(token.target)
        inner = self.render_inner(token)
        return template.format(target=target, inner=inner)

    def render_escape_sequence(self, token):
        return self.render_inner(token)

    @staticmethod
    def render_raw_text(token):
        return html.escape(token.content)

    @staticmethod
    def render_html_span(token):
        return token.content

    def render_heading(self, token):
        template = '<h{level}>{inner}</h{level}>'
        inner = self.render_inner(token)
        return template.format(level=token.level, inner=inner)

    def render_quote(self, token):
        elements = ['<blockquote>']
        elements.extend([self.render(child) for child in token.children])
        elements.append('</blockquote>')
        return '\n'.join(elements)

    def render_paragraph(self, token):
        if self._suppress_ptag_stack[-1]:
            return '{}'.format(self.render_inner(token))
        return '<p>{}</p>'.format(self.render_inner(token))

    def render_block_code(self, token):
        template = '<pre><code{attr}>{inner}</code></pre>'
        if token.language:
            attr = ' class="{}"'.format('language-{}'.format(token.language))
        else:
            attr = ''
        inner = self.render_inner(token)
        return template.format(attr=attr, inner=inner)

    def render_list(self, token):
        template = '<{tag}{attr}>\n{inner}\n</{tag}>'
        if token.start:
            tag = 'ol'
            attr = ' start="{}"'.format(token.start) if token.start != 1 else ''
        else:
            tag = 'ul'
            attr = ''
        self._suppress_ptag_stack.append(not token.loose)
        inner = '\n'.join([self.render(child) for child in token.children])
        self._suppress_ptag_stack.pop()
        return template.format(tag=tag, attr=attr, inner=inner)

    def render_list_item(self, token):
        inner = '\n'.join([self.render(child) for child in token.children])
        inner_template = '\n{}\n'
        if self._suppress_ptag_stack[-1]:
            if token.children[0].__class__.__name__ == 'Paragraph':
                inner_template = inner_template[1:]
            if token.children[-1].__class__.__name__ == 'Paragraph':
                inner_template = inner_template[:-1]
        return '<li>{}</li>'.format(inner_template.format(inner))

    def render_table(self, token):
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

    def render_table_row(self, token, is_header=False):
        template = '<tr>\n{inner}</tr>\n'
        inner = ''.join([self.render_table_cell(child, is_header)
                         for child in token.children])
        return template.format(inner=inner)

    def render_table_cell(self, token, in_header=False):
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
    def render_thematic_break(token):
        return '<hr />'

    @staticmethod
    def render_line_break(token):
        return '<br />\n'

    @staticmethod
    def render_html_block(token):
        return token.content

    def render_document(self, token):
        self.footnotes.update(token.footnotes)
        inner = '\n'.join([self.render(child) for child in token.children])
        return '{}\n'.format(inner) if inner else ''

def escape_url(raw):
    """
    Escape urls to prevent code injection craziness. (Hopefully.)
    """
    from urllib.parse import quote
    return quote(raw, safe='/#:')
