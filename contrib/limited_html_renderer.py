import sys
if sys.version_info < (3, 4):
    from mistletoe import _html as html
else:
    import html
from mistletoe.html_renderer import HTMLRenderer

class LimitedHTMLRenderer(HTMLRenderer):
    @staticmethod
    def render_html_block(token):
        return html.escape(token.content)

    @staticmethod
    def render_html_span(token):
        return html.escape(token.content)
