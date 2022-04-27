"""
Base token class.
"""


def _short_repr(value):
    """
    Return a shortened ``repr`` output of value for use in ``__repr__`` methods.
    """

    if isinstance(value, str):
        chars = len(value)
        threshold = 30
        if chars > threshold:
            return "{0!r}...+{1}".format(value[:threshold], chars-threshold)
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

        if hasattr(self, "children"):
            count = len(self.children)
            if count == 1:
                output += " with 1 child"
            else:
                output += " with {} children".format(count)

        if hasattr(self, "content"):
           output += " content=" + _short_repr(self.content)

        for attrname in self.repr_attributes:
            attrvalue = getattr(self, attrname)
            output += " {}={}".format(attrname, _short_repr(attrvalue))
        output += " at {:#x}>".format(id(self))
        return output
