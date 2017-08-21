"""
Inline tokenizer for mistletoe.
"""

def tokenize(content, token_types, fallback_token):
    """
    Searches for token_types in content, and applies fallback_token
    to texts in between.

    Args:
        content (str): user input string to be parsed.
        token_types (list): a list of span-level token constructors.
        fallback_token (span_token.SpanToken): token for unmatched texts.

    Yields:
        span-level token instances.
    """
    if content:
        index, match_obj, token_type = _find_nearest_token(content, token_types)
        if index != 0:
            yield fallback_token(content[:index])
        if match_obj is not None:
            yield token_type(match_obj)
            yield from tokenize(content[match_obj.end():], token_types, fallback_token)


def _find_nearest_token(content, token_types):
    # accumulator pattern
    min_index = len(content)
    min_match_obj = None
    min_token_type = None
    for token_type in token_types:
        match_obj = token_type.pattern.search(content)
        if match_obj and match_obj.start() < min_index:
            min_index = match_obj.start()
            min_match_obj = match_obj
            min_token_type = token_type
    return min_index, min_match_obj, min_token_type
