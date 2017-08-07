"""
Base class for renderers.
"""

class BaseRenderer(object):
    """
    Base class for renderers.

    All renderers should ...
    *   ... define all render functions specified in self.render_map;
    *   ... be a context manager (by inheriting __enter__ and __exit__);

    Custom renderers could ...
    *   ... add additional render functions by appending to self.render_map;
    *   ... inject custom tokens into the parsing process (by overriding
        __enter__ and __exit__)

    Example:
        Suppose SomeRenderer inherits BaseRenderer, and fin is the input file.
        The syntax looks something like this:

            >>> from mistletoe import Document
            >>> from some_renderer import SomeRenderer
            >>> with SomeRenderer as r:
            ...     rendered = r(Document(fin))

        See mistletoe.html_renderer for an implementation example.

    Naming conventions:
        The keys of self.render_map should exactly match the class
        name of tokens.

    Attributes:
        render_map (dict): maps tokens to their corresponding render functions.
    """
    def __init__(self):
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

    def render(self, token, footnotes={}):
        """
        Grabs the class name from input token and finds its corresponding
        render function.

        Basically a janky way to do polymorphism.

        Arguments:
            token: whose __class__.__name__ is in self.render_map.
            footnotes (dict): pass down footnote information during recursion.
        """
        return self.render_map[token.__class__.__name__](token, footnotes)

    def render_inner(self, token, footnotes):
        """
        Recursively renders child tokens. Joins the rendered
        strings with no space in between.

        If newlines / spaces are needed between tokens, add them
        in their respective templates, or override this function
        in the renderer subclass, so that whitespace won't seem to
        appear magically for anyone reading your program.

        Arguments:
            token: a branch node who has children attribute.
            footnotes (dict): pass down footnote information during recursion.
        """
        rendered = [self.render(child, footnotes) for child in token.children]
        return ''.join(rendered)

    def __enter__(self):
        """
        Make renderer classes into context managers.

        This should be overridden in subclasses when custom tokens
        are needed. Specifically, custom token classes should be
        injected to mistletoe.span_token / mistletoe.block_token
        namespace.
        """
        return self

    def __exit__(self, exception_type, exception_val, traceback):
        """
        Make renderer classes into context managers.

        Provides teardown logic for __enter__. Subclasses with custom
        tokens injected should clean up namespace here.
        """
        pass
