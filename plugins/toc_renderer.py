"""
Table of contents support for mistletoe.

See `if __name__ == '__main__'` section for sample usage.
"""

import re
from mistletoe.block_token import List
from mistletoe.html_renderer import HTMLRenderer

class TOCRenderer(HTMLRenderer):
    """
    Extends HTMLRenderer class for table of contents support.
    """
    def __init__(self, omit_title=True, filter_conds=[]):
        super().__init__()
        self._headings = []
        self.omit_title = omit_title
        self.filter_conds = filter_conds

    @property
    def toc(self):
        """
        Returns table of contents as a block_token.List instance.
        """
        def get_indent(level):
            return ' ' * 4 * (level - 1)

        def build_list_item(heading):
            level, content = heading
            template = '{indent}- {content}\n'
            return template.format(indent=get_indent(level), content=content)

        return List([build_list_item(heading) for heading in self._headings])

    def render_heading(self, token, footnotes):
        """
        Overrides super().render_heading; stores rendered heading first,
        then returns it.
        """
        rendered = super().render_heading(token, footnotes)
        if not (self.omit_title and token.level == 1
                or any(cond(rendered) for cond in self.filter_conds)):
            self.store_rendered_heading(rendered)
        return rendered

    def store_rendered_heading(self, rendered):
        """
        Helper method; converts rendered heading to a tuple pair
        (level, content), where content is stripped of HTML tags.
        """
        level = int(rendered[2])
        content = re.sub(r'<.+?>', '', rendered[4:-6])
        self._headings.append((level, content))

if __name__ == '__main__':
    from mistletoe import Document
    with open('test/samples/jquery.md', 'r') as fin:
        with TOCRenderer() as renderer:
            renderer.render(Document(fin))
            print(renderer.render(renderer.toc))
