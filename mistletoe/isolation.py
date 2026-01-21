import contextlib
from mistletoe import block_token
from mistletoe import span_token
from mistletoe import core_tokens


@contextlib.contextmanager
def IsolatedContext():
    """
    Context manager for isolated document parsing with clean token state.

    Use this context before parsing a document when you need to:
    - Parse with a clean slate of token types (no previously registered custom tokens)
    - Ensure parsing doesn't interfere with other parsing operations
    - Reset all token registrations to default state

    Usage:
        with IsolatedContext():
            # Register only the tokens you need for this specific parsing
            block_token.add_token(MyCustomBlockToken)
            span_token.add_token(MyCustomSpanToken)

            # Now parse your document with isolated token context
            doc = mistletoe.Document(markdown_content)

    Can also be used together with a (custom) renderer to ensure isolated token types
    in asynchronous or multithreaded environments:

    Usage:
        with IsolatedContext():
            with MarkdownRenderer() as renderer:
                # Parse the document with the custom renderer
                doc = mistletoe.Document(markdown_content)
                renderer.render(doc)

    The context automatically cleans up token registrations on exit,
    returning to the default token types state calling the reset functions and
    ensuring no side effects on subsequent parsing operations.
    """
    block_token._token_types.set([])
    block_token.reset_tokens()
    span_token._token_types.set([])
    span_token.reset_tokens()
    core_tokens._code_matches.set([])
    try:
        yield
    finally:
        block_token._token_types.set([])
        block_token.reset_tokens()
        span_token._token_types.set([])
        span_token.reset_tokens()
        core_tokens._code_matches.set([])