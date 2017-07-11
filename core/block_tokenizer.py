import re

__all__ = ['read_quote', 'read_block_code', 'read_paragraph', 'read_list']

def read_quote(index, lines):
    while index < len(lines):
        if not lines[index].startswith('> '):
            return index
        index += 1
    return index

def read_block_code(index, lines):
    index += 1    # skip first line
    while index < len(lines):
        if lines[index] == '```\n':
            return index + 1
        index += 1
    return index

def read_paragraph(index, lines):
    index += 1
    while index < len(lines):
        if lines[index] == '\n':
            return index
        index += 1
    return index

def read_list(index, lines, level=0):
    while index < len(lines):
        expected_content = lines[index][level*4:].strip()
        if not re.match(r'([\+\-\*])|([0-9]\.)', expected_content):
            return index
        index += 1
    return index

