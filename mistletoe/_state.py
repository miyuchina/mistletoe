"""Context-local parser configuration and state (not part of the public API)."""

from contextvars import ContextVar
from typing import TYPE_CHECKING, Callable, Generic, Iterable, Optional, TypeVar

if TYPE_CHECKING:
    from mistletoe.base_renderer import BaseRenderer
    from mistletoe.token import Token


TokenType = TypeVar('TokenType', bound='Token')


class TokenRegistry(Generic[TokenType]):
    """Keep ambient defaults separate from an active renderer's token types.

    Tuples and replacement updates keep copied asyncio contexts independent.
    Built-in defaults are captured when the token module finishes loading.
    Explicit resets resolve the current token constructors, as before.
    """

    def __init__(self, name: str, defaults: Callable[[], tuple[type[TokenType], ...]]):
        self._defaults = defaults
        self._builtin_types = defaults()
        self._ambient: ContextVar[Optional[tuple[type[TokenType], ...]]] = ContextVar(name + '_ambient', default=None)
        self.active: ContextVar[Optional[tuple[type[TokenType], ...]]] = ContextVar(name, default=None)

    def defaults(self) -> tuple[type[TokenType], ...]:
        types = self._ambient.get()
        return self._builtin_types if types is None else types

    def get(self) -> tuple[type[TokenType], ...]:
        types = self.active.get()
        return self.defaults() if types is None else types

    def set(self, types: Iterable[type[TokenType]]) -> None:
        variable = self._ambient if self.active.get() is None else self.active
        variable.set(tuple(types))

    def add(self, token_cls: type[TokenType], position: int) -> None:
        types = list(self.get())
        types.insert(position, token_cls)
        self.set(types)

    def remove(self, token_cls: type[TokenType]) -> None:
        types = list(self.get())
        if token_cls in types:
            types.remove(token_cls)
            self.set(types)

    def reset(self) -> None:
        self.set(self._defaults())


active_renderer: ContextVar[Optional['BaseRenderer']] = ContextVar('mistletoe_renderer', default=None)
parse_setext = ContextVar('mistletoe_parse_setext', default=True)
