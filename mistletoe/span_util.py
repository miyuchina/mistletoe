import re


class _MatchObj:
    def __init__(self, fields, start, end):
        self.fields = fields
        self._start = start
        self._end = end

    def start(self):
        return self._start

    def end(self):
        return self._end

    def __repr__(self):
        return '<MatchObj fields={} start={} end={}>'.format(self.fields, self._start, self._end)


class LinkPattern:
    angle_dest_pattern = re.compile(r'\s*<([^\s<>]*?)>')
    title_pattern = re.compile(r'\s*(\".*?(?<!\\)\"|\'.*?(?<!\\)\'|\(.*?(?<!\\)\))?\s*\)')

    @classmethod
    def search(cls, string, start=0):
        # read link text
        if start != 0:
            string = string[start:]

        text_start = string.find('[')
        if text_start == -1:
            return None
        brackets = 1
        escaped = False
        for i, c in enumerate(string[text_start+1:], start=text_start+1):
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
        text_end = i
        text = string[text_start+1:text_end]

        # read dest
        if text_end+2 >= len(string) or string[text_end+1] != '(':
            return None
        dest_start = text_end + 2
        match_obj = cls.angle_dest_pattern.match(string, pos=dest_start)
        if match_obj is not None:
            dest_end = match_obj.end()
            dest = match_obj.group(1)
        else:
            dest_start = cls.skip_spaces(string, dest_start)
            parens = 1
            escaped = False
            for i, c in enumerate(string[dest_start:], start=dest_start):
                if c == '\\':
                    escaped = True
                elif not escaped:
                    if c == '(':
                        parens += 1
                    if c == ')':
                        parens -= 1
                else:
                    escaped = False
                if c == ' ':
                    break
                if parens == 0:
                    return _MatchObj((text, string[dest_start:i], ''), start+text_start, start+i+1)
            else:
                return None
            dest_end = i
            dest = string[dest_start:dest_end]

        # read title
        match_obj = cls.title_pattern.match(string, pos=dest_end)
        if match_obj is None:
            return None
        title = match_obj.group(1)
        title_end = match_obj.end()
        if title is not None:
            title = title[1:-1]
        else:
            title = ''

        return _MatchObj((text, dest, title), start+text_start, start+title_end+1)

    @staticmethod
    def skip_spaces(string, start=0):
        for i, c in enumerate(string[start:], start=start):
            if c != ' ' or c != '\n':
                break
        return i
