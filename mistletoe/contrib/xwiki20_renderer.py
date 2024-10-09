from itertools import chain
from mistletoe import block_token, span_token
from mistletoe.base_renderer import BaseRenderer


class XWiki20Renderer(BaseRenderer):
    """
    XWiki syntax 2.0 renderer class.

    See mistletoe.base_renderer module for more info.
    """
    def __init__(self, *extras):
        """
        Args:
            extras (list): allows subclasses to add even more custom tokens.
        """
        self.listTokens = []
        self.lastChildOfQuotes = []
        self.firstChildOfListItems = []

        localExtras = [block_token.HtmlBlock, span_token.HtmlSpan, span_token.XWikiBlockMacroStart, span_token.XWikiBlockMacroEnd]
        super().__init__(*chain(localExtras, extras))

    def render_strong(self, token):
        template = '**{}**'
        return template.format(self.render_inner(token))

    def render_emphasis(self, token):
        template = '//{}//'
        return template.format(self.render_inner(token))

    def render_inline_code(self, token):
        # Note: XWiki also offers preformatted text syntax ('##{}##') as a shorter alternative.
        #       We would have to escape the raw text when using it.
        template = '{{{{code}}}}{}{{{{/code}}}}'
        return template.format(self.render_raw_text(token.children[0], False))

    def render_strikethrough(self, token):
        template = '--{}--'
        return template.format(self.render_inner(token))

    def render_image(self, token):
        template = '[[image:{src}]]'
        self.render_inner(token)
        return template.format(src=token.src)

    def render_link(self, token):
        template = '[[{inner}>>{target}]]'
        target = escape_url(token.target)
        inner = self.render_inner(token)
        return template.format(target=target, inner=inner)

    def render_auto_link(self, token):
        template = '[[{target}]]'
        target = escape_url(token.target)
        return template.format(target=target)

    def render_escape_sequence(self, token):
        return '~' + self.render_inner(token)

    def render_raw_text(self, token, escape=True):
        return (token.content.replace('~', '~~')
                # Note: It's probably better to leave potential XWiki macros as-is, i. e. don't escape their markers:
                # .replace('{{', '~{{').replace('}}', '~}}')
                .replace('[[', '~[[').replace(']]', '~]]')
                .replace('**', '~**').replace('//', '~//')
                .replace('##', '~##').replace('--', '~--')
                ) if escape else token.content

    def render_x_wiki_block_macro_start(self, token):
        return token.content + '\n'

    def render_x_wiki_block_macro_end(self, token):
        return '\n' + token.content

    def render_html_span(self, token):
        # XXX: HtmlSpan parses (contains) only individual opening and closing tags
        # => no easy way to wrap the whole HTML code into {{html}} like this:
        #
        # template = '{{{{html wiki="true"}}}}{}{{{{/html}}}}'
        # return template.format(token.content)
        #
        # => Users must do this themselves after the conversion.

        return token.content

    def render_html_block(self, token):
        template = '{{{{html wiki="true"}}}}\n{}\n{{{{/html}}}}' + self._block_eol(token)
        return template.format(token.content)

    def render_heading(self, token):
        template = '{level} {inner} {level}'
        inner = self.render_inner(token)
        return template.format(level='=' * token.level, inner=inner) + self._block_eol(token)

    def render_quote(self, token):
        self.lastChildOfQuotes.append(token.children[-1])
        inner = self.render_inner(token)
        del (self.lastChildOfQuotes[-1])

        return (
            "".join(
                map(
                    lambda line: ">{}{}".format(
                        "" if line.startswith(">") else " ", line
                    ),
                    inner.splitlines(keepends=True),
                )
            )
            + self._block_eol(token)[0:-1]
        )

    def render_paragraph(self, token):
        return '{}'.format(self.render_inner(token)) + self._block_eol(token)

    def render_block_code(self, token):
        template = '{{{{code{attr}}}}}\n{inner}{{{{/code}}}}' + self._block_eol(token)
        if token.language:
            attr = ' language="{}"'.format(token.language)
        else:
            attr = ''

        inner = self.render_raw_text(token.children[0], False)
        return template.format(attr=attr, inner=inner)

    def render_list(self, token):
        inner = self.render_inner(token)
        return inner + self._block_eol(token)[0:-1]

    def render_list_item(self, token):
        template = '{prefix} {inner}\n'
        prefix = ''.join(self.listTokens)
        if '1' in self.listTokens:
            prefix += '.'

        self.firstChildOfListItems.append(token.children[0])
        inner = self.render_inner(token)
        del (self.firstChildOfListItems[-1])

        result = template.format(prefix=prefix, inner=inner.rstrip())

        return result

    def render_inner(self, token):
        if isinstance(token, block_token.List):
            if token.start:
                self.listTokens.append('1')
            else:
                self.listTokens.append('*')

        rendered = [self.render(child) for child in token.children]

        wrap = False
        if isinstance(token, block_token.BlockToken) and len(token.children) > 1:
            # test what follows after the 1st child of this block token - wrap it to a XWiki block right after the 1st child if necessary
            for child in token.children[1:]:
                if isinstance(token, block_token.ListItem) and not isinstance(child, block_token.List):
                    # Note: Nested list within a list item is OK, because it does its own wrapping if necessary.
                    wrap = True
                    break
                if isinstance(token, (block_token.TableCell)) and isinstance(child, block_token.BlockToken):
                    # Note: By-design, Markdown doesn't support multiple lines in one cell, but they can be enforced by using HTML.
                    # See e. g. https://stackoverflow.com/questions/19950648/how-to-write-lists-inside-a-markdown-table.
                    wrap = True
                    break

        if isinstance(token, block_token.List):
            del (self.listTokens[-1])

        return (''.join(rendered) if not wrap
                else '{head}(((\n{tail}\n)))\n'.format(head=rendered[0].rstrip(), tail=''.join(rendered[1:]).rstrip()))

    def render_table(self, token):
        # Copied from JiraRenderer...
        #
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
            template = '{inner}\n'
        else:
            template = '{inner}\n'

        inner = ''.join([self.render_table_cell(child, is_header)
                         for child in token.children])

        return template.format(inner=inner)

    def render_table_cell(self, token, in_header=False):
        if in_header:
            template = '|={inner}'
        else:
            template = '|{inner}'

        inner = self.render_inner(token)
        return template.format(inner=inner)

    @staticmethod
    def render_thematic_break(token):
        return '----\n'

    @staticmethod
    def render_line_break(token):
        return ' ' if token.soft else '\n'

    def render_document(self, token):
        self.footnotes.update(token.footnotes)
        return self.render_inner(token)

    def _block_eol(self, token):
        return ('\n' if ((len(self.firstChildOfListItems) > 0 and token is self.firstChildOfListItems[-1])
                or (len(self.lastChildOfQuotes) > 0 and token is self.lastChildOfQuotes[-1])) else '\n\n')


def escape_url(raw):
    """
    Escape urls to prevent code injection craziness. (Hopefully.)
    """
    from urllib.parse import quote
    return quote(raw, safe='/#:()*?=%@+,&;')
