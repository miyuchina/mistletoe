import re


angle_pattern = re.compile(r'\s*<([^\s<>]*?)>')
title_pattern = re.compile(r'\s*(\".*?(?<!\\)\"|\'.*?(?<!\\)\'|\(.*?(?<!\\)\))?\s*')


class Pattern:
    @classmethod
    def finditer(cls, string):
        match = cls.search(string)
        while match is not None:
            yield match
            match = cls.search(string, match.end())


class _MatchObj:
    def __init__(self, fields, start, end):
        self.fields = fields
        self._start = start
        self._end = end

    def start(self, n=0):
        if n == 0:
            return self._start
        return self.fields[n-1][0]

    def end(self, n=0):
        if n == 0:
            return self._end
        return self.fields[n-1][1]

    def group(self, n=0):
        return self.fields[n-1][2]

    def __repr__(self):
        return '<MatchObj fields={} start={} end={}>'.format(self.fields, self._start, self._end)


class LinkPattern(Pattern):
    @classmethod
    def search(cls, string, start=0):
        # read link text
        text_pair = read_link_text(string, offset=start)
        if text_pair is None:
            return None
        start, text_end, text = text_pair

        # read dest
        dest_pair = read_dest_text(string, offset=text_end)
        if dest_pair is None:
            return None
        dest_start, dest_end, dest = dest_pair

        # read title
        title_pair = read_link_title(string, offset=dest_end)
        if title_pair is None:
            return None
        title_start, title_end, title = title_pair

        # assert closing paren
        if string[title_end] != ')':
            return None
        end = title_end + 1
        return _MatchObj(((start+1, text_end, text),
                          (dest_start, dest_end, dest),
                          (title_start, title_end, title)),
                         start, end)


class ImagePattern(Pattern):
    @classmethod
    def search(cls, string, start=0):
        # read image text
        text_pair = read_image_text(string, offset=start)
        if text_pair is None:
            return None
        start, text_end, text = text_pair

        # read dest
        dest_pair = read_dest_text(string, offset=text_end)
        if dest_pair is None:
            return None
        dest_start, dest_end, dest = dest_pair

        # read title
        title_pair = read_link_title(string, offset=dest_end)
        if title_pair is None:
            return None
        title_start, title_end, title = title_pair

        # assert closing paren
        if string[title_end] != ')':
            return None
        end = title_end + 1
        return _MatchObj(((start+2, text_end, text),
                          (dest_start, dest_end, dest),
                          (title_start, title_end, title)),
                         start, end)


def read_link_text(string, offset=0):
    start = string.find('[', offset)
    if start == -1:
        return None
    brackets = 1
    escaped = False
    for i, c in enumerate(string[start+1:], start=start+1):
        if c == '\\':
            escaped = True
        elif not escaped:
            if c == '[':
                brackets += 1
            if c == ']':
                brackets -= 1
        else:
            escaped = False
        if brackets == 0:
            break
    else:
        return None
    return start, i, string[start+1:i]


def read_dest_text(string, offset=0):
    if offset+2 >= len(string) or string[offset+1] != '(':
        return None
    start = offset + 2
    match_obj = angle_pattern.match(string, pos=start)
    if match_obj is not None:
        end = match_obj.end()
        dest = match_obj.group(1)
    else:
        start = skip_spaces(string, start)
        parens = 1
        escaped = False
        for i, c in enumerate(string[start:], start=start):
            if c == '\\':
                escaped = True
            elif not escaped:
                if c == '(':
                    parens += 1
                if c == ')':
                    parens -= 1
            else:
                escaped = False
            if c == ' ' or parens == 0:
                break
        else:
            return None
        end = i
        dest = string[start:end]
    return start, end, dest


def read_link_title(string, offset=0):
    match_obj = title_pattern.match(string, pos=offset)
    if match_obj is None:
        return None
    title = match_obj.group(1)
    end = match_obj.end()
    if title is not None:
        return offset, end, title[1:-1]
    return offset, end, ''


def read_image_text(string, offset=0):
    start = string.find('![', offset)
    if start == -1:
        return None
    link_pair = read_link_text(string, start)
    if link_pair is None:
        return None
    return start, link_pair[1], link_pair[2]


def skip_spaces(string, start=0):
    for i, c in enumerate(string[start:], start=start):
        if c != ' ' or c != '\n':
            break
    return i
