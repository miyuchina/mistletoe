import re


whitespace = ' \n\t\r'
label_pattern = re.compile(r'\[(.+?)(?<!\])\]', re.DOTALL)
punctuation = {'!', '"', '#', '$', '%', '&', '\'', '(', ')', '*', '+', ',',
               '-', '.', '/', ':', ';', '<', '=', '>', '?', '@', '[', '\\',
               ']', '^', '_', '`', '{', '|', '}', '~'}


def find_core_tokens(string):
    delimiters = []
    matches = []
    escaped = False
    in_delimiter_run = False
    in_image = False
    start = 0
    i = 0
    while i < len(string):
        c = string[i]
        if c == '\\':
            escaped = True
        elif (c == '*' or c == '_') and not escaped:
            if not in_delimiter_run:
                in_delimiter_run = True
                start = i
        elif in_delimiter_run:
            delimiters.append(Delimiter(start, i, string))
            in_delimiter_run = False
        elif not escaped:
            if c == '[':
                if not in_image:
                    delimiters.append(Delimiter(i, i+1, string))
                else:
                    delimiters.append(Delimiter(i-1, i+1, string))
                    in_image = False
            elif c == '!':
                in_image = True
            elif c == ']':
                i = find_link_image(string, i, delimiters, matches)
            elif in_image:
                in_image = False
        else:
            escaped = False
        i += 1
    if in_delimiter_run:
        delimiters.append(Delimiter(start, i, string))
    process_emphasis(string, 0, delimiters, matches)
    return matches


def find_link_image(string, offset, delimiters, matches):
    i = len(delimiters) - 1
    for delimiter in delimiters[::-1]:
        # found a link/image delimiter
        if delimiter.type in ('[', '!['):
            # not active, remove delimiter
            if not delimiter.active:
                delimiters.remove(delimiter)
                return offset
            match = match_link_image(string, offset, delimiter)
            # found match
            if match:
                # parse for emphasis
                process_emphasis(string, i, delimiters, matches)
                # append current match
                matches.append(match)
                # if match is a link, set all previous links to be inactive
                if delimiter.type == '[':
                    deactivate_delimiters(delimiters, i, '[')
                # shift index till end of match
                return match.end() - 1
            # no match, remove delimiter
            delimiters.remove(delimiter)
            return offset
        i -= 1
    # no link/image delimiter
    return offset


def process_emphasis(string, stack_bottom, delimiters, matches):
    star_bottom = stack_bottom
    underscore_bottom = stack_bottom
    curr_pos = next_closer(stack_bottom, delimiters)
    while curr_pos is not None:
        closer = delimiters[curr_pos]
        bottom = star_bottom if closer.type[0] == '*' else underscore_bottom
        open_pos = matching_opener(curr_pos, delimiters, bottom)
        if open_pos is not None:
            opener = delimiters[open_pos]
            n = 2 if closer.number >= 2 and opener.number >= 2 else 1
            start = opener.end - n
            end = closer.start + n
            match = MatchObj(((start+n, end-n, string[start+n:end-n]),),
                              start, end)
            match.type = 'Strong' if n == 2 else 'Emphasis'
            matches.append(match)
            if not opener.remove(n, left=False):
                delimiters.remove(opener)
                curr_pos -= 2
                if curr_pos < 0: curr_pos = 0
            if not closer.remove(n, left=True):
                delimiters.remove(closer)
                curr_pos -= 2
                if curr_pos < 0: curr_pos = 0
        else:
            if closer.type[0] == '*':
                star_bottom = curr_pos - 1
            else:
                underscore_bottom = curr_pos - 1
            if not closer.open:
                delimiters.remove(closer)
                curr_pos -= 2
                if curr_pos < 0: curr_pos = 0
        curr_pos = next_closer(curr_pos, delimiters)
    del delimiters[stack_bottom:]


def match_link_image(string, offset, delimiter):
    image = delimiter.type == '!['
    start = delimiter.start
    text_start = start + delimiter.number
    text_end = offset
    text = string[text_start:text_end]
    # inline link
    if follows(string, offset, '('):
        # link destination
        match_info = match_link_dest(string, offset+1)
        if match_info is None:
            return None
        dest_start, dest_end, dest = match_info
        # link title
        match_info = match_link_title(string, dest_end)
        if match_info is None:
            return None
        title_start, title_end, title = match_info
        # assert closing paren
        paren_index = shift_whitespace(string, title_end)
        if paren_index >= len(string) or string[paren_index] != ')':
            return None
        end = paren_index + 1
        match = MatchObj(((text_start, text_end, text),
                          (dest_start, dest_end, dest),
                          (title_start, title_end, title)),
                         start, end)
        match.type = 'Link' if not image else 'Image'
        return match
    # footnote link
    elif follows(string, offset, '['):
        # full footnote link
        match_info = match_link_label(string, offset+1)
        if match_info:
            label_start, label_end, label = match_info
            match = MatchObj(((text_start, text_end, text),
                              (label_start, label_end, label)),
                             start, label_end)
            match.type = 'FootnoteLink' if not image else 'FootnoteImage'
            return match
        elif is_link_label(text):
            # compact footnote link
            if follows(string, offset+1, ']'):
                label_start = offset + 1
                label_end = offset + 2
                label = ''
                end = offset + 3
                match = MatchObj(((text_start, text_end, text),
                                  (label_start, label_end, label)),
                                 start, end)
                match.type = 'FootnoteLink' if not image else 'FootnoteImage'
                return match
    # shortcut footnote link
    if is_link_label(text):
        label_start = offset + 1
        label_end = offset + 1
        label = ''
        end = offset + 1
        match = MatchObj(((text_start, text_end, text),
                          (label_start, label_end, label)),
                         start, end)
        match.type = 'FootnoteLink' if not image else 'FootnoteImage'
        return match
    return None


def match_link_dest(string, offset):
    offset = shift_whitespace(string, offset+1)
    if string[offset] == '<':
        escaped = False
        for i, c in enumerate(string[offset+1:], start=offset+1):
            if c == '\\':
                escaped = True
            elif c == ' ' or c == '\n' or (c == '<' and not escaped):
                return None
            elif c == '>' and not escaped:
                return offset, i+1, string[offset+1:i]
            elif escaped:
                escaped = False
        return None
    else:
        escaped = False
        count = 1
        for i, c in enumerate(string[offset+1:], start=offset+1):
            if c == '\\':
                escaped = True
            elif c in whitespace:
                return offset, i, string[offset:i]
            elif not escaped:
                if c == '(':
                    count += 1
                elif c == ')':
                    count -= 1
            elif is_control_char(c):
                return None
            elif escaped:
                escaped = False
            if count == 0:
                return offset, i, string[offset:i]
        return None


def match_link_title(string, offset):
    offset = shift_whitespace(string, offset)
    if string[offset] == ')':
        return offset, offset, ''
    if string[offset] == '"':
        closing = '"'
    elif string[offset] == "'":
        closing = "'"
    elif string[offset] == '(':
        closing = ')'
    else:
        return None
    escaped = False
    for i, c in enumerate(string[offset+1:], start=offset+1):
        if c == '\\':
            escaped = True
        elif c == closing and not escaped:
            return offset, i+1, string[offset+1:i]
        elif escaped:
            escaped = False
    return None


def match_link_label(string, offset):
    match_obj = label_pattern.search(string, offset)
    if match_obj and is_link_label(match_obj.group(1)):
        return match_obj.start(), match_obj.end(), match_obj.group(1)
    return None


def is_link_label(text):
    return text.strip() != ''


def next_closer(curr_pos, delimiters):
    for i, delimiter in enumerate(delimiters[curr_pos+1:], start=curr_pos+1):
        if hasattr(delimiter, 'close') and delimiter.close:
            return i
    return None


def matching_opener(curr_pos, delimiters, bottom):
    curr_type = delimiters[curr_pos].type[0]
    index = curr_pos - 1
    for delimiter in delimiters[curr_pos-1::-1]:
        if (hasattr(delimiter, 'open')
                and delimiter.open
                and delimiter.type[0] == curr_type):
            return index
        index -= 1
    return None


def is_opener(start, end, string):
    if string[start] == '*':
        return is_left_delimiter(start, end, string)
    is_right = is_right_delimiter(start, end, string)
    return (is_left_delimiter(start, end, string)
            and (not is_right
                 or (is_right and preceded_by(end, string, punctuation))))


def is_closer(start, end, string):
    if string[start] == '*':
        return is_right_delimiter(start, end, string)
    is_left = is_left_delimiter(start, end, string)
    return (is_right_delimiter(start, end, string)
            and (not is_left
                 or (is_left and succeeded_by(end, string, punctuation))))


def is_left_delimiter(start, end, string):
    return (not succeeded_by(end, string, whitespace)
            and (not succeeded_by(end, string, punctuation)
                 or preceded_by(start, string, punctuation)
                 or preceded_by(start, string, whitespace)))

def is_right_delimiter(start, end, string):
    return (not preceded_by(start, string, whitespace)
            and (not preceded_by(start, string, punctuation)
                 or succeeded_by(end, string, whitespace)
                 or succeeded_by(end, string, punctuation)))

def preceded_by(start, string, charset):
    preceding_char = string[start-1] if start > 0 else ' '
    return preceding_char in charset


def succeeded_by(end, string, charset):
    succeeding_char = string[end] if end < len(string) else ' '
    return succeeding_char in charset


def is_control_char(char):
    return ord(char) > 31 and ord(char) != 127


def follows(string, index, char):
    return index + 1 < len(string) and string[index+1] == char


def shift_whitespace(string, index):
    for i, c in enumerate(string[index:], start=index):
        if c not in whitespace:
            return i
    return i


def deactivate_delimiters(delimiters, index, delimiter_type):
    for delimiter in delimiters[:index]:
        if delimiter.type == delimiter_type:
            delimiter.active = False


class Delimiter:
    def __init__(self, start, end, string):
        self.type = string[start:end]
        self.number = end - start
        self.active = True
        self.start = start
        self.end = end
        self._string = string
        if self.type.startswith(('*', '_')):
            self.open = is_opener(start, end, string)
            self.close = is_closer(start, end, string)

    def remove(self, n, left=True):
        if self.number - n == 0:
            return False
        if left:
            self.start = self.start + n
            self.number = self.end - self.start
            return True
        self.end = self.end - n
        self.number = self.end - self.start
        return True

    def __repr__(self):
        if not self.type.startswith(('*', '_')):
            return '<Delimiter type={} active={}>'.format(repr(self.type), self.active)
        return '<Delimiter type={} active={} open={} close={}>'.format(repr(self.type), self.active, self.open, self.close)


class MatchObj:
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