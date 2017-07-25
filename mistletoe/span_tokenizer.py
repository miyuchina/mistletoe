def tokenize(content, token_types, fallback_token):
    index = 0
    while index < len(content):
        new_content = content[index:]
        min_index = len(content)
        min_match_obj = None
        min_token_type = None
        for token_type in token_types:
            match_obj = token_type.pattern.search(new_content)
            if match_obj and index + match_obj.start() < min_index:
                min_index = index + match_obj.start()
                min_match_obj = match_obj
                min_token_type = token_type
        if min_index != index:
            yield fallback_token(content[index:min_index])
        if min_match_obj:
            yield min_token_type(min_match_obj.group(1))
            index += min_match_obj.end()
        else: return
