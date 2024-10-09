from mistletoe import HtmlRenderer
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name as get_lexer, guess_lexer
from pygments.styles import get_style_by_name as get_style
from pygments.util import ClassNotFound


class PygmentsRenderer(HtmlRenderer):
    formatter = HtmlFormatter()
    formatter.noclasses = True

    def __init__(self, *extras, style='default', fail_on_unsupported_language=False, **kwargs):
        """
        Args:
            extras (list): allows subclasses to add even more custom tokens.
            style (str): short name of the style to be used by Pygments' `HtmlFormatter`,
                      see `pygments.styles.get_style_by_name()`.
            fail_on_unsupported_language (bool): whether to let Pygments' `ClassNotFound`
                      be thrown when there is an unsupported language found on
                      a code block.
                      If `False`, then language is guessed instead of throwing the error.
            **kwargs: additional parameters to be passed to the ancestor's
                      constructor.
        """
        super().__init__(*extras, **kwargs)
        self.formatter.style = get_style(style)
        self.fail_on_unsupported_language = fail_on_unsupported_language

    def render_block_code(self, token):
        code = token.content
        lexer = None

        if token.language:
            try:
                lexer = get_lexer(token.language)
            except ClassNotFound as err:
                if self.fail_on_unsupported_language:
                    raise err

        if lexer is None:
            lexer = guess_lexer(code)

        return highlight(code, lexer, self.formatter)
