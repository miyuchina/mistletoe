class LeafTokenizer(object):
    def __init__(self, content, token_types, fallback_token):
        self.content = content
        self.token_types = token_types
        self.fallback_token = fallback_token

    def get_tokens(self):
        index = 0
        while index < len(self.content):
            matched = 0
            for token_type in self.token_types:
                match_obj = token_type.pattern.match(self.content[index:])
                if match_obj:
                    yield token_type(match_obj.group(1))
                    matched = 1
                    index += match_obj.end()
                    break
            if not matched:
                min_index = len(self.content)
                min_match_obj = None
                min_token_type = None
                for token_type in self.token_types:
                    match_obj = token_type.pattern.search(self.content[index:])
                    if match_obj and match_obj.start() < min_index:
                        min_index = index + match_obj.start()
                        min_match_obj = match_obj
                        min_token_type = token_type
                yield self.fallback_token(self.content[index:min_index])
                if min_match_obj:
                    yield min_token_type(min_match_obj.group(1))
                    index += min_match_obj.end()
                else:
                    return
        return
