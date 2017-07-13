import itertools

class BlockTokenizer(object):
    def __init__(self, iterable, token_types, fallback_token):
        self.lines = itertools.chain(iterable, [ '\n' ])
        self.token_types = token_types
        self.fallback_token = fallback_token

    def get_tokens(self):
        line_buffer = []
        for line in self.lines:
            if line != '\n': line_buffer.append(line)
            elif line_buffer:
                matched = False
                for token_type in self.token_types:
                    if token_type.match(line_buffer):
                        yield token_type(line_buffer)
                        matched = True
                        break
                if not matched:
                    yield self.fallback_token(line_buffer)
                line_buffer.clear()
