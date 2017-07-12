class BlockTokenizer(object):
    def __init__(self, lines, token_types, fallback_token):
        self.lines = lines
        self.token_types = token_types
        self.fallback_token = fallback_token

    def get_tokens(self):
        index = 0
        while index < len(self.lines):
            matched = False
            for token_type in self.token_types:
                if token_type.check_start(self.lines[index]):
                    curr_index = token_type.read(index, self.lines)
                    yield token_type(self.lines[index:curr_index])
                    matched = True
                    index = curr_index
                    break
            if not matched:
                if self.lines[index] == '\n':
                    index += 1
                else:
                    curr_index = self.fallback_token.read(index, self.lines)
                    yield self.fallback_token(self.lines[index:curr_index])
                    index = curr_index
        return
