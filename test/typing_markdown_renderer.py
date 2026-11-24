"""Static examples for Markdown renderer extensions.

Run with: uv run mypy; uv run pyright; uv run ty check
These commands also check the library subset configured in pyproject.toml.
Imported modules retain their types; see CONTRIBUTING.md for full-library
audit commands. This file is not collected as a runtime test.

Overrides of the line conversion helpers must return iterators: callers use
next() directly. Render hooks keep their more general iterable return types.
Fragment metadata is present only when supplied in extras. Placeholder fields
belong to downstream subclasses; None text is not supported by the standard
fragment consumers and needs a separate sentinel/consumer contract downstream.
"""

from typing import Iterable, Iterator, Match, Optional, Sequence, Union, assert_type

from mistletoe import block_token, span_token, token
from mistletoe.core_tokens import MatchObj
from mistletoe.markdown_renderer import Fragment, MarkdownRenderer


class PlaceholderFragment(Fragment):
    """Application metadata belongs on an application-specific fragment."""

    placeholder_content: str
    important: bool

    def __init__(self, text: str, placeholder_content: str, important: bool):
        super().__init__(text, placeholder_content=placeholder_content,
                         important=important)


class CustomRenderer(MarkdownRenderer):
    def span_to_lines(
        self, tokens: Iterable[span_token.SpanToken],
        max_line_length: Optional[float],
    ) -> Iterator[str]:
        return super().span_to_lines(tokens, max_line_length)

    @classmethod
    def fragments_to_lines(
        cls, fragments: Iterable[Fragment],
        max_line_length: Optional[float] = None,
    ) -> Iterator[str]:
        return super().fragments_to_lines(fragments, max_line_length)

    def render_link_or_image(
        self, token: Union[span_token.Link, span_token.Image], target: str,
    ) -> Iterable[Fragment]:
        return self.embed_span(Fragment("["), token.children, Fragment("]"))


def renderer_examples(
    renderer: MarkdownRenderer,
    link: span_token.Link,
    image: span_token.Image,
    block: block_token.BlockToken,
    leaf: span_token.RawText,
) -> None:
    assert_type(next(renderer.span_to_lines(link.children, None), ""), str)
    assert_type(renderer.embed_span(Fragment("["), image.children),
                Iterable[Fragment])
    assert_type(renderer.render_link_or_image(link, "target"), Iterable[Fragment])
    assert_type(renderer.render_link_or_image(image, "source"), Iterable[Fragment])
    assert_type(block.line_number, Optional[int])
    assert_type(token._root_node.get(), Optional[block_token.Document])
    assert_type(leaf.children, Optional[Iterable[span_token.SpanToken]])
    assert_type(renderer.fragments_to_lines(
        [Fragment("text", wordwrap=True)], float("inf")), Iterator[str])
    renderer.span_to_lines(image.children, 80)
    renderer.blocks_to_lines([block], float("inf"))
    renderer.render_quote(block_token.Quote([]), float("inf"))
    MarkdownRenderer(max_line_length=float("inf"))
    fragment = Fragment("text", wordwrap=True, hard_line_break=False)
    assert_type(fragment.wordwrap, bool)
    assert_type(fragment.hard_line_break, bool)
    placeholder = PlaceholderFragment("", "original text", True)
    assert_type(placeholder.placeholder_content, str)
    assert_type(placeholder.important, bool)


def parser_examples(
    match: MatchObj,
    span_class: type[span_token.SpanToken],
    document: block_token.Document,
    quote: block_token.Quote,
) -> None:
    assert_type(match.type, str)
    assert_type(match.dest_type, str)
    assert_type(match.title_delimiter, Optional[str])
    assert_type(span_class.find("text"), Iterable[Union[Match[str], MatchObj]])
    assert_type(span_class.repr_attributes, tuple[str, ...])
    assert_type(document.footnotes, dict[str, tuple[str, str]])
    assert_type(quote.children, Sequence[block_token.BlockToken])
