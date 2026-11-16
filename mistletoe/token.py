import sys
from typing import TYPE_CHECKING, Any, Generic, Iterable, Optional, Sized, cast

if sys.version_info >= (3, 13):
    from typing import TypeVar
else:
    from typing_extensions import TypeVar

if TYPE_CHECKING:
    from mistletoe.block_token import Document

"""
Base token class.
"""


"""
Stores a reference to the current document (root) token during parsing.

Footnotes are stored in the document token by accessing this reference.
"""
_root_node: Optional["Document"] = None


Children = TypeVar(
    "Children",
    bound=Optional[Iterable["Token[Any]"]],
    default=Optional[Iterable["Token[Any]"]],
)


def _short_repr(value: object) -> str:
    """
    Return a shortened ``repr`` output of value for use in ``__repr__`` methods.
    """

    if isinstance(value, str):
        chars = len(value)
        threshold = 30
        if chars > threshold:
            return "{0!r}...+{1}".format(value[:threshold], chars - threshold)
    return repr(value)


class Token(Generic[Children]):
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

    repr_attributes: tuple[str, ...] = ()

    _children: Children
    _parent: Optional["Token[Any]"]

    def __repr__(self) -> str:
        output = "<{}.{}".format(
            self.__class__.__module__,
            self.__class__.__name__
        )

        if self.children is not None:
            count = len(cast(Sized, self.children))
            if count == 1:
                output += " with 1 child"
            else:
                output += " with {} children".format(count)

        if "content" in vars(self):
            output += " content=" + _short_repr(getattr(self, 'content'))

        for attrname in self.repr_attributes:
            attrvalue = getattr(self, attrname)
            output += " {}={}".format(attrname, _short_repr(attrvalue))
        output += " at {:#x}>".format(id(self))
        return output

    @property
    def parent(self) -> Optional['Token[Any]']:
        """Returns the parent token, if there is any."""
        return getattr(self, '_parent', None)

    @property
    def children(self) -> Children:
        """Return children, or None before assignment (including leaf tokens).

        Nonoptional specializations describe initialized instances. Keep the
        supplied collection itself: assigning children also sets parent links,
        but later mutations of that collection do not update those links.
        """
        return cast(Children, getattr(self, '_children', None))

    @children.setter
    def children(self, value: Children) -> None:
        self._children = value
        if value:
            for child in cast(Iterable[Token[Any]], value):
                child._parent = self
