from typing import Iterable, Optional

"""
Base token class.
"""


"""
Stores a reference to the current document (root) token during parsing.

Footnotes are stored in the document token by accessing this reference.
"""
_root_node = None


def _short_repr(value):
    """
    Return a shortened ``repr`` output of value for use in ``__repr__`` methods.
    """

    if isinstance(value, str):
        chars = len(value)
        threshold = 30
        if chars > threshold:
            return "{0!r}...+{1}".format(value[:threshold], chars - threshold)
    return repr(value)


class Token:
    """
    Base token class.

    `Token` has two subclasses:

    * `block_token.BlockToken`, for all block level tokens. A block level token
      is text which occupies the entire horizontal width of the "page" and is
      offset for the surrounding sibling block with line breaks.

    * `span_token.SpanToken`, for all span-level (or inline-level) tokens.
      A span-level token appears inside the flow of the text lines without any
      surrounding line break.

    Custom ``__repr__`` methods in subclasses: The default ``__repr__``
    implementation outputs the number of child tokens (from the attribute
    ``children``) if applicable, and the ``content`` attribute if applicable.
    If any additional attributes should be included in the ``__repr__`` output,
    this can be specified by setting the class attribute ``repr_attributes``
    to a tuple containing the attribute names to be output.
    """

    repr_attributes = ()

    def __repr__(self):
        output = "<{}.{}".format(
            self.__class__.__module__,
            self.__class__.__name__
        )

        if self.children is not None:
            count = len(self.children)
            if count == 1:
                output += " with 1 child"
            else:
                output += " with {} children".format(count)

        if "content" in vars(self):
            output += " content=" + _short_repr(self.content)

        for attrname in self.repr_attributes:
            attrvalue = getattr(self, attrname)
            output += " {}={}".format(attrname, _short_repr(attrvalue))
        output += " at {:#x}>".format(id(self))
        return output

    @property
    def parent(self) -> Optional['Token']:
        """Returns the parent token, if there is any."""
        return getattr(self, '_parent', None)

    @property
    def children(self) -> Optional[Iterable['Token']]:
        """
        Returns the child (nested) tokens.
        Returns `None` if the token is a leaf token.
        """
        return getattr(self, '_children', None)

    @children.setter
    def children(self, value: Iterable['Token']):
        """"
        Sets new child (nested) tokens.
        Passed tokens are iterated and their ``parent`` property is set to
        this token.
        """
        self._children = value
        if value:
            for child in value:
                child._parent = self
