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
    index = 0
    # The following loop is critical to mistletoe.
    # Don't mess with it unless you really know what you are doing!
    while index < len(content):
        new_content = content[index:]
        min_index = len(content)
        min_match_obj = None
        min_token_type = None
        for token_type in token_types:   # search for nearest valid token_type
            match_obj = token_type.pattern.search(new_content)
            if match_obj and index + match_obj.start() < min_index:
                min_index = index + match_obj.start()
                min_match_obj = match_obj
                min_token_type = token_type
        if min_index != index:
            # there's text between our current position and the next token
            yield fallback_token(content[index:min_index])
        if min_match_obj:                # min_match_obj is not None
            yield min_token_type(min_match_obj.group(1))
            index += min_match_obj.end() # update pointer
        else: return                     # min_match_obj is None; no more tokens
