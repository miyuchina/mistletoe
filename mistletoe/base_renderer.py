class BaseRenderer(object):
    """
    Naming conventions:
        The keys of self.render_map should exactly match the class name of
        tokens (see HTMLRenderer.render).

    Attributes:
        render_map (dict): maps tokens to their corresponding render functions.
        preamble (str): see self.render_document.
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
            'FootnoteLink':   self.render_footnote_link,
            'AutoLink':       self.render_auto_link,
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
        return ''.join([self.render(child, footnotes) for child in token.children])

    def __call__(self, token):
        return self.render(token, {})

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass
