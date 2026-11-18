"""
Make mistletoe easier to import.
"""

__version__ = "1.7.0.dev"
__all__ = ['html_renderer', 'ast_renderer', 'block_token', 'block_tokenizer',
           'span_token', 'span_tokenizer']

from typing import TYPE_CHECKING, Callable, Iterable, Union

if TYPE_CHECKING:
    from mistletoe import (
        ast_renderer as ast_renderer,
        block_token as block_token,
        block_tokenizer as block_tokenizer,
        html_renderer as html_renderer,
        span_token as span_token,
        span_tokenizer as span_tokenizer,
    )

from mistletoe.base_renderer import BaseRenderer
from mistletoe.block_token import Document  # noqa: F401
from mistletoe.html_renderer import HtmlRenderer
# import the old name for backwards compatibility:
from mistletoe.html_renderer import HTMLRenderer  # noqa: F401


def markdown(iterable: Union[str, Iterable[str]], renderer: Callable[..., BaseRenderer] = HtmlRenderer):
    """
    Converts markdown input to the output supported by the given renderer.
    If no renderer is supplied, ``HtmlRenderer`` is used.

    Note that extra token types supported by the given renderer
    are automatically (and temporarily) added to the parsing process.
    """
    with renderer() as r:
        return r.render(r.parse(iterable))
