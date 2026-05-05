from mistletoe.isolation import IsolatedContext
from mistletoe.block_token import _token_types as block_token_types
from mistletoe.span_token import _token_types as span_token_types
from mistletoe.core_tokens import _code_matches

def test_isolation_of_contexts():

    assert len(block_token_types.get()) == 9
    assert len(span_token_types.get()) == 7
    assert len(_code_matches.get()) == 0

    block_token_types.get().append(1)
    span_token_types.get().append(1)
    _code_matches.get().append(1)

    assert len(block_token_types.get()) == 10
    assert block_token_types.get()[-1] == 1
    assert len(span_token_types.get()) == 8
    assert span_token_types.get()[-1] == 1
    assert len(_code_matches.get()) == 1
    assert _code_matches.get()[-1] == 1

    with IsolatedContext() as c:
        assert len(block_token_types.get()) == 9
        assert len(span_token_types.get()) == 7
        assert len(_code_matches.get()) == 0

        block_token_types.get().append(2)
        span_token_types.get().append(2)
        _code_matches.get().append(2)

        assert len(block_token_types.get()) == 10
        assert block_token_types.get()[-1] == 2
        assert len(span_token_types.get()) == 8
        assert span_token_types.get()[-1] == 2
        assert len(_code_matches.get()) == 1
        assert _code_matches.get()[-1] == 2

    assert len(block_token_types.get()) == 9
    assert len(span_token_types.get()) == 7
    assert len(_code_matches.get()) == 0
