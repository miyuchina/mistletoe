"""Static checks for Markdown renderer extensions and token types.

See CONTRIBUTING.md for the type-checking commands.
"""

from typing import Iterable, Iterator, Sequence, assert_type

from mistletoe import block_token, span_token
from mistletoe.markdown_renderer import Fragment, MarkdownRenderer


class CustomRenderer(MarkdownRenderer):
    def render_link_or_image(
        self, token: span_token.Link | span_token.Image, target: str,
    ) -> Iterable[Fragment]:
        return self.embed_span(Fragment("["), token.children, Fragment("]"))


def renderer_examples(link: span_token.Link) -> None:
    renderer = MarkdownRenderer(max_line_length=float("inf"))
    assert_type(
        renderer.span_to_lines(link.children, renderer.max_line_length),
        Iterator[str],
    )
    assert_type(
        renderer.fragments_to_lines([Fragment("text")], renderer.max_line_length),
        Iterator[str],
    )


def parser_examples(quote: block_token.Quote) -> None:
    assert_type(quote.children, Sequence[block_token.BlockToken])
