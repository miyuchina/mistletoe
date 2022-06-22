"""
Base class for renderers.
"""

import re
from mistletoe import block_token, span_token

class BaseRenderer(object):
    """
    Base class for renderers.

    All renderers should ...
    *   ... define all render functions specified in self.render_map;
    *   ... be a context manager (by inheriting __enter__ and __exit__);

    Custom renderers could ...
    *   ... add additional tokens into the parsing process by passing custom
        tokens to super().__init__();
    *   ... add additional render functions by appending to self.render_map;

    Usage:
        Suppose SomeRenderer inherits BaseRenderer, and fin is the input file.
        The syntax looks something like this:

            >>> from mistletoe import Document
            >>> from some_renderer import SomeRenderer
            >>> with SomeRenderer() as renderer:
            ...     rendered = renderer.render(Document(fin))

        See mistletoe.html_renderer for an implementation example.

    Naming conventions:
        *   The keys of self.render_map should exactly match the class
            name of tokens;
        *   Render function names should be of form: "render_" + the
            "snake-case" form of token's class name.

    Attributes:
        render_map (dict): maps tokens to their corresponding render functions.
        _extras (list): a list of custom tokens to be added to the
                        parsing process.
    """
    _parse_name = re.compile(r"([A-Z][a-z]+|[A-Z]+(?![a-z]))")

    def __init__(self, *extras):
        self.render_map = {
            'Strong':         self.render_strong,
            'Emphasis':       self.render_emphasis,
            'InlineCode':     self.render_inline_code,
            'RawText':        self.render_raw_text,
            'Strikethrough':  self.render_strikethrough,
            'Image':          self.render_image,
            'Link':           self.render_link,
            'AutoLink':       self.render_auto_link,
            'EscapeSequence': self.render_escape_sequence,
            'Heading':        self.render_heading,
            'SetextHeading':  self.render_heading,
            'Quote':          self.render_quote,
            'Paragraph':      self.render_paragraph,
            'CodeFence':      self.render_block_code,
            'BlockCode':      self.render_block_code,
            'List':           self.render_list,
            'ListItem':       self.render_list_item,
            'Table':          self.render_table,
            'TableRow':       self.render_table_row,
            'TableCell':      self.render_table_cell,
            'ThematicBreak':  self.render_thematic_break,
            'LineBreak':      self.render_line_break,
            'Document':       self.render_document,
            }
        self._extras = extras

        for token in extras:
            if issubclass(token, span_token.SpanToken):
                token_module = span_token
            else:
                token_module = block_token
            token_module.add_token(token)
            render_func = getattr(self, self._cls_to_func(token.__name__))
            self.render_map[token.__name__] = render_func

        self.footnotes = {}

    def render(self, token):
        """
        Grabs the class name from input token and finds its corresponding
        render function.

        Basically a janky way to do polymorphism.

        Arguments:
            token: whose __class__.__name__ is in self.render_map.
        """
        return self.render_map[token.__class__.__name__](token)

    def render_inner(self, token) -> str:
        """
        Recursively renders child tokens. Joins the rendered
        strings with no space in between.

        If newlines / spaces are needed between tokens, add them
        in their respective templates, or override this function
        in the renderer subclass, so that whitespace won't seem to
        appear magically for anyone reading your program.

        Arguments:
            token: a branch node who has children attribute.
        """
        return ''.join(map(self.render, token.children))

    def __enter__(self):
        """
        Make renderer classes into context managers.
        """
        return self

    def __exit__(self, exception_type, exception_val, traceback):
        """
        Make renderer classes into context managers.

        Reset block_token._token_types and span_token._token_types.
        """
        block_token.reset_tokens()
        span_token.reset_tokens()

    @classmethod
    def _cls_to_func(cls, cls_name):
        snake = '_'.join(map(str.lower, cls._parse_name.findall(cls_name)))
        return 'render_{}'.format(snake)

    @staticmethod
    def _tokens_from_module(module):
        """
        Helper method; takes a module and returns a list of all token classes
        specified in module.__all__. Useful when custom tokens are defined in a
        separate module.
        """
        return [getattr(module, name) for name in module.__all__]

    def render_raw_text(self, token) -> str:
        """
        Default render method for RawText. Simply return token.content.
        """
        return token.content

    def render_strong(self, token: span_token.Strong) -> str:
        return self.render_inner(token)

    def render_emphasis(self, token: span_token.Emphasis) -> str:
        return self.render_inner(token)

    def render_inline_code(self, token: span_token.InlineCode) -> str:
        return self.render_inner(token)

    def render_strikethrough(self, token: span_token.Strikethrough) -> str:
        return self.render_inner(token)

    def render_image(self, token: span_token.Image) -> str:
        return self.render_inner(token)

    def render_link(self, token: span_token.Link) -> str:
        return self.render_inner(token)

    def render_auto_link(self, token: span_token.AutoLink) -> str:
        return self.render_inner(token)

    def render_escape_sequence(self, token: span_token.EscapeSequence) -> str:
        return self.render_inner(token)

    def render_line_break(self, token: span_token.LineBreak) -> str:
        return self.render_inner(token)

    def render_heading(self, token: block_token.Heading) -> str:
        return self.render_inner(token)

    def render_quote(self, token: block_token.Quote) -> str:
        return self.render_inner(token)

    def render_paragraph(self, token: block_token.Paragraph) -> str:
        return self.render_inner(token)

    def render_block_code(self, token: block_token.BlockCode) -> str:
        return self.render_inner(token)

    def render_list(self, token: block_token.List) -> str:
        return self.render_inner(token)

    def render_list_item(self, token: block_token.ListItem) -> str:
        return self.render_inner(token)

    def render_table(self, token: block_token.Table) -> str:
        return self.render_inner(token)

    def render_table_cell(self, token: block_token.TableCell) -> str:
        return self.render_inner(token)

    def render_table_row(self, token: block_token.TableRow) -> str:
        return self.render_inner(token)

    def render_thematic_break(self, token: block_token.ThematicBreak) -> str:
        return self.render_inner(token)

    def render_document(self, token: block_token.Document) -> str:
        return self.render_inner(token)
