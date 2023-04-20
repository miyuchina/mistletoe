from mistletoe import HTMLRenderer
from pygments import highlight
from pygments.styles import get_style_by_name as get_style
from pygments.lexers import get_lexer_by_name as get_lexer, guess_lexer
from pygments.formatters.html import HtmlFormatter

class PygmentsRenderer(HTMLRenderer):
    formatter = HtmlFormatter()
    formatter.noclasses = True

    def __init__(self, *extras, style='default'):
        super().__init__(*extras)
        self.formatter.style = get_style(style)


    def render_block_code(self, token):
        code = token.children[0].content
        lexer = get_lexer(token.language) if token.language else guess_lexer(code)
        return highlight(code, lexer, self.formatter)

