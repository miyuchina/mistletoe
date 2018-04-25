from mistletoe import HTMLRenderer, Document
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters.html import HtmlFormatter

class PygmentsRenderer(HTMLRenderer):
    formatter = HtmlFormatter()
    formatter.noclasses = True

    def render_block_code(self, token):
        code = token.children[0].content
        lexer = get_lexer_by_name(token.language) if token.language else guess_lexer(code)
        return highlight(code, lexer, self.formatter)
