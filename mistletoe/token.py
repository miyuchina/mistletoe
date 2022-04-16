"""
token contains the base token class Token.
"""


def _short_repr(value):
    """
    Return a shortened repr output of value for use in __repr__ method.
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

    Token has two subclasses:

    * block_token.BlockToken, for all block level tokens. A block level token
      is text which occupies the entire horizontal width of the "page" and is
      offset for the surrounding sibling block with line breaks.

    * span_token.SpanToken. for all span-level (or inline-level) tokens.
      A span-level token appears inside the flow of the text lines without any
      surrounding line break.
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
