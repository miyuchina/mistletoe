import re

def normalize(lines):
    heading = re.compile(r'#+ |=+$|-+$')
    code_fence = False
    for line in lines:
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

def tokenize(iterable, token_types, fallback_token):
    line_buffer = []
    for line in normalize(iterable):
        if line != '\n':
            line_buffer.append(line)
        elif line_buffer:
            matched = 0
            for token_type in token_types:
                if token_type.match(line_buffer):
                    yield token_type(line_buffer)
                    matched = 1
                    break
            if not matched:
                yield fallback_token(line_buffer)
            line_buffer.clear()
