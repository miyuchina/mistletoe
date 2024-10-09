# Copyright 2018 Tile, Inc.  All Rights Reserved.
#
# The MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from itertools import chain
from mistletoe import block_token, span_token
from mistletoe.base_renderer import BaseRenderer
import re


class JiraRenderer(BaseRenderer):
    """
    JIRA renderer class.

    See mistletoe.base_renderer module for more info.
    """
    def __init__(self, *extras):
        """
        Args:
            extras (list): allows subclasses to add even more custom tokens.
        """
        self.listTokens = []
        self.lastChildOfQuotes = []
        super().__init__(*chain([block_token.HtmlBlock, span_token.HtmlSpan], extras))

    def render_strong(self, token):
        template = '*{}*'
        return template.format(self.render_inner(token))

    def render_emphasis(self, token):
        template = '_{}_'
        return template.format(self.render_inner(token))

    def render_inline_code(self, token):
        template = '{{{{{}}}}}'
        return template.format(self.render_inner(token))

    def render_strikethrough(self, token):
        template = '-{}-'
        return template.format(self.render_inner(token))

    def render_image(self, token):
        template = '!{src}!'
        self.render_inner(token)
        return template.format(src=token.src)

    def render_link(self, token):
        template = '[{inner}|{target}{title}]'
        inner = self.render_inner(token)
        target = escape_url(token.target)
        if token.title:
            title = '|{}'.format(token.title)
        else:
            title = ''

        return template.format(inner=inner, target=target, title=title)

    def render_auto_link(self, token):
        template = '[{target}]'
        target = escape_url(token.target)
        return template.format(target=target)

    def render_escape_sequence(self, token):
        return self.render_inner(token)

    def render_raw_text(self, token, escape=True):
        if escape:
            def repl(match):
                return '\\' + match.group(0)
            # The following regex tries to find special chars that are one of the following:
            # 1. the whole string (typically in an EscapeSequence)
            # 2. just after a non-whitespace
            # 3. just before a non-whitespace
            re_esc_chars = r'[{}\[\]\-*_+^~]'
            re_find = r'(^{esc_chars}$)|((?<=\S)({esc_chars}))|(({esc_chars})(?=\S))'.format(esc_chars=re_esc_chars)
            return re.sub(re_find, repl, token.content)
        else:
            return token.content

    @staticmethod
    def render_html_span(token):
        return token.content

    def render_heading(self, token):
        template = 'h{level}. {inner}'
        inner = self.render_inner(token)
        return template.format(level=token.level, inner=inner) + self._block_eol(token)

    def render_quote(self, token):
        self.lastChildOfQuotes.append(token.children[-1])
        inner = self.render_inner(token)
        del (self.lastChildOfQuotes[-1])

        if len(token.children) == 1 and isinstance(token.children[0], block_token.Paragraph):
            template = 'bq. {inner}' + self._block_eol(token)[0:-1]
        else:
            template = '{{quote}}\n{inner}{{quote}}' + self._block_eol(token)

        return template.format(inner=inner)

    def render_paragraph(self, token):
        return '{}'.format(self.render_inner(token)) + self._block_eol(token)

    def render_block_code(self, token):
        template = '{{code{attr}}}\n{inner}{{code}}' + self._block_eol(token)
        if token.language:
            attr = ':{}'.format(token.language)
        else:
            attr = ''

        inner = self.render_raw_text(token.children[0], False)
        return template.format(attr=attr, inner=inner)

    def render_list(self, token):
        inner = self.render_inner(token)
        return inner + self._block_eol(token)[0:-1]

    def render_list_item(self, token):
        template = '{prefix} {inner}'
        prefix = ''.join(self.listTokens)
        result = template.format(prefix=prefix, inner=self.render_inner(token))
        return result

    def render_inner(self, token):
        if isinstance(token, block_token.List):
            if token.start:
                self.listTokens.append('#')
            else:
                self.listTokens.append('*')

        rendered = [self.render(child) for child in token.children]

        if isinstance(token, block_token.List):
            del (self.listTokens[-1])

        return ''.join(rendered)

    def render_table(self, token):
        # This is actually gross and I wonder if there's a better way to do it.
        #
        # The primary difficulty seems to be passing down alignment options to
        # reach individual cells.
        template = '{inner}\n'
        if hasattr(token, 'header'):
            head_template = '{inner}'
            header = token.header
            head_inner = self.render_table_row(header, True)
            head_rendered = head_template.format(inner=head_inner)

        else:
            head_rendered = ''

        body_template = '{inner}'
        body_inner = self.render_inner(token)
        body_rendered = body_template.format(inner=body_inner)
        return template.format(inner=head_rendered + body_rendered)

    def render_table_row(self, token, is_header=False):
        if is_header:
            template = '{inner}||\n'
        else:
            template = '{inner}|\n'

        inner = ''.join([self.render_table_cell(child, is_header)
                         for child in token.children])

        return template.format(inner=inner)

    def render_table_cell(self, token, in_header=False):
        if in_header:
            template = '||{inner}'
        else:
            template = '|{inner}'

        inner = self.render_inner(token)
        if inner == '':
            inner = ' '
        return template.format(inner=inner)

    @staticmethod
    def render_thematic_break(token):
        return '----\n'

    @staticmethod
    def render_line_break(token):
        # Note: In Jira, outputting just '\n' instead of '\\\n' should be usually sufficient as well.
        # It is not clear when it wouldn't be sufficient though, so we use the longer variant for sure.
        return ' ' if token.soft else '\\\\\n'

    @staticmethod
    def render_html_block(token):
        return token.content

    def render_document(self, token):
        self.footnotes.update(token.footnotes)
        return self.render_inner(token)

    def _block_eol(self, token):
        """
        Jira syntax is very limited when it comes to lists: whenever
        we put an empty line anywhere in a list, it gets terminated
        and there seems to be no workaround for this. Also to have blocks
        like paragraphs really vertically separated, we need to put
        an empty line between them. This function handles these two cases.
        """
        return (
            "\n"
            if len(self.listTokens) > 0 or (len(self.lastChildOfQuotes) > 0 and token is self.lastChildOfQuotes[-1])
            else "\n\n"
        )


def escape_url(raw):
    """
    Escape urls to prevent code injection craziness. (Hopefully.)
    """
    from urllib.parse import quote
    return quote(raw, safe='/#:()*?=%@+,&;')


JIRARenderer = JiraRenderer
"""
Deprecated name of the `JiraRenderer` class.
"""
