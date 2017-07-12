class LeafTokenizer(object):
    def __init__(self, content, token_types, fallback_token):
        self.content = content
        self.token_types = token_types
        self.fallback_token = fallback_token

    def get_tokens(self):
        index = 0
        while index < len(self.content):
            matched = False
            for token_type in self.token_types:
                match_obj = token_type.pattern.match(self.content[index:])
                if match_obj:
                    yield token_type(match_obj.group(1))
                    matched = True
                    index += match_obj.end()
                    break
            if not matched:
                min_index = len(self.content)
                for token_type in self.token_types:
                    match_obj = token_type.pattern.search(self.content[index:])
                    if match_obj and match_obj.start() < min_index:
                        min_index = match_obj.start()
                yield self.fallback_token(self.content[index:min_index])
                index = min_index
        return
