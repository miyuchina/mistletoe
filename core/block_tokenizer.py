import re

class BlockTokenizer(object):
    def __init__(self, iterable, token_types, fallback_token):
        self.lines = iterable
        self.token_types = token_types
        self.fallback_token = fallback_token


    def normalize(self):
        heading = re.compile(r'#+ |=+$|-+$')
        code_fence = False
        for line in self.lines:
            line = line.replace('\t', '    ')
            if heading.match(line):
                yield line
                yield '\n'
            elif not code_fence and line.startswith('```'):
                code_fence = True
                yield '\n'
                yield line
            elif code_fence:
                if line == '```\n':
                    code_fence = False
                    yield line
                    yield '\n'
                elif line == '\n':
                    yield ' ' + line
                else:
                    yield line
            else: yield line
        yield '\n'

    def get_tokens(self):
        line_buffer = []
        for line in self.normalize():
            if line != '\n': line_buffer.append(line)
            elif line_buffer:
                matched = 0
                for token_type in self.token_types:
                    if token_type.match(line_buffer):
                        yield token_type(line_buffer)
                        matched = 1
                        break
                if not matched:
                    yield self.fallback_token(line_buffer)
                line_buffer.clear()
