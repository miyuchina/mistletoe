"""
Table of contents support for mistletoe.

See `if __name__ == '__main__'` section for sample usage.
"""

import re
from mistletoe.html_renderer import HtmlRenderer
from mistletoe import block_token


class TocRenderer(HtmlRenderer):
    """
    Extends HtmlRenderer class for table of contents support.
    """
    def __init__(self, *extras, depth=5, omit_title=True, filter_conds=[], **kwargs):
        """
        Args:
            extras (list): allows subclasses to add even more custom tokens.
            depth (int): the maximum level of heading to be included in TOC.
            omit_title (bool): whether to ignore tokens where token.level == 1.
            filter_conds (list): when any of these functions evaluate to true,
                                current heading will not be included.
            **kwargs: additional parameters to be passed to the ancestor's
                      constructor.
        """
        super().__init__(*extras, **kwargs)
        self._headings = []
        self.depth = depth
        self.omit_title = omit_title
        self.filter_conds = filter_conds

    @property
    def toc(self):
        """
        Returns table of contents as a block_token.List instance.
        """
        def get_indent(level):
            if self.omit_title:
                level -= 1
            return ' ' * 4 * (level - 1)

        def build_list_item(heading):
            level, content = heading
            template = '{indent}- {content}\n'
            return template.format(indent=get_indent(level), content=content)

        lines = [build_list_item(heading) for heading in self._headings]
        items = block_token.tokenize(lines)
        return items[0]

    def render_heading(self, token):
        """
        Overrides super().render_heading; stores rendered heading first,
        then returns it.
        """
        rendered = super().render_heading(token)
        content = self.parse_rendered_heading(rendered)
        if not (self.omit_title and token.level == 1
                or token.level > self.depth
                or any(cond(content) for cond in self.filter_conds)):
            self._headings.append((token.level, content))
        return rendered

    @staticmethod
    def parse_rendered_heading(rendered):
        """
        Helper method; converts rendered heading to plain text.
        """
        return re.sub(r'<.+?>', '', rendered)


TOCRenderer = TocRenderer
"""
Deprecated name of the `TocRenderer` class.
"""
