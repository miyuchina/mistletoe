"""
HTML renderer for mistletoe.
"""

import html
import urllib.parse

def render(token):
    """
    Wrapper function for HTMLRenderer. Creates a HTMLRenderer instance
    and renders the token passed in.

    Unless you want to mess with the actual HTMLRenderer class, to render
    a token to HTML you would only need to do:

        >>> from HTMLRenderer import render
        >>> token = block_token.Document(lines)
        >>> render(token)

    ... without importing the class itself.
    """
    return HTMLRenderer().render(token, {})

class HTMLRenderer(object):
    """
    HTML renderer class.

    Naming conventions:
        The keys of self.render_map should exactly match the class name of
        tokens (see HTMLRenderer.render).

    Attributes:
        render_map (dict): maps tokens to their corresponding render functions.
        preamble (str): to be injected between <html> and <body> tags.
    """
    def __init__(self, preamble=''):
        self.render_map = {
            'Strong':         self.render_strong,
            'Emphasis':       self.render_emphasis,
            'InlineCode':     self.render_inline_code,
            'RawText':        self.render_raw_text,
            'Strikethrough':  self.render_strikethrough,
            'Image':          self.render_image,
            'FootnoteImage':  self.render_footnote_image,
            'Link':           self.render_link,
            'AutoLink':       self.render_auto_link,
            'EscapeSequence': self.render_raw_text,
            'HTMLSpan':       self.render_html_span,
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
            'HTMLBlock':      self.render_html_block,
            'Document':       self.render_document,
            }
        self.preamble = preamble

    def render(self, token, footnotes):
        """
        Grabs the class name from input token and finds its corresponding
        render function.

        Basically a janky way to do polymorphism.
        """
        return self.render_map[token.__class__.__name__](token, footnotes)

    def render_inner(self, token, footnotes):
        """
        Recursively renders child tokens.
        """
        return ''.join([self.render(child, footnotes)
                        for child in token.children])

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

    @staticmethod
    def render_image(token, footnotes):
        template = '<img src="{}" title="{}" alt="{}">'
        return template.format(token.src, token.title, token.alt)

    @staticmethod
    def render_footnote_image(token, footnotes):
        template = '<img src="{}" alt="{}">'
        src = footnotes.get(token.children[0].key, '')
        return template.format(src, token.alt)

    def render_link(self, token, footnotes):
        template = '<a href="{target}">{inner}</a>'
        target = urllib.parse.quote_plus(token.target)
        inner = self.render_inner(token, footnotes)
        return template.format(target=target, inner=inner)

    @staticmethod
    def render_auto_link(token, footnotes):
        template = '<a href="{target}">{name}</a>'
        target = urllib.parse.quote_plus(token.target)
        name = html.escape(token.name)
        return template.format(target=target, name=name)

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
        attr = ' class="lang-{}"'.format(token.language) if token.language else ''
        inner = self.render_inner(token, footnotes)
        return template.format(attr=attr, inner=inner)

    def render_list(self, token, footnotes):
        template = '<{tag}{attr}>\n{inner}</{tag}>\n'
        if hasattr(token, 'start'):
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
        template = '<table>\n{inner}</table>\n'
        if token.has_header:
            head_template = '<thead>\n{inner}</thead>\n'
            header = token.children.send(None)
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
        template = '<html>\n{preamble}<body>\n{inner}</body>\n</html>\n'
        token.children = list(token.children)  # kick off generator
        inner = self.render_inner(token, token.footnotes)
        return template.format(preamble=self.preamble, inner=inner)
