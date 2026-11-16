"""Static contracts for token children and extension classes."""
from typing import Any, Iterable, Optional, Sequence, assert_type

from mistletoe.block_token import BlockToken, Document, Quote
from mistletoe.span_token import InlineCode, RawText, SpanToken
from mistletoe.token import Token


class CustomToken(Token[list[RawText]]):
    def __init__(self, children: list[RawText]) -> None:
        self.children = children


class CustomBlock(BlockToken):
    pass


class CustomSpan(SpanToken):
    pass


def examples(
    base: Token, document: Document, quote: Quote, code: InlineCode,
    leaf: RawText, custom: CustomToken, block: CustomBlock, span: CustomSpan,
) -> None:
    assert_type(base.children, Optional[Iterable[Token[Any]]])
    assert_type(document.children, Iterable[BlockToken[Any]])
    assert_type(quote.children, Sequence[BlockToken[Any]])
    assert_type(code.children[0], RawText)
    assert_type(leaf.children, Optional[Iterable[SpanToken[Any]]])
    assert_type(custom.children, list[RawText])
    assert_type(custom.children[0].parent, Optional[Token[Any]])
    assert_type(block.children, Optional[Iterable[Token[Any]]])
    assert_type(span.children, Optional[Iterable[SpanToken[Any]]])
    custom.children = [leaf]
    base.children = (child for child in [leaf])
