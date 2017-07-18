import unittest
import core.block_token  as block_token
import core.span_token   as span_token
import lib.html_renderer as renderer

class TestHTMLRenderer(unittest.TestCase):
    def setUp(self):
        self.renderer = renderer.HTMLRenderer()

    def _test_token(self, token_type, raw, target):
        output = self.renderer.render(token_type(raw))
        self.assertEqual(output, target)

    def test_strong(self):
        raw, target = 'some text', '<strong>some text</strong>'
        self._test_token(span_token.Strong, raw, target)

    def test_emphasis(self):
        raw, target = 'some text', '<em>some text</em>'
        self._test_token(span_token.Emphasis, raw, target)

    def test_inline_code(self):
        raw, target = 'some code', '<code>some code</code>'
        self._test_token(span_token.InlineCode, raw, target)

    def test_strikethrough(self):
        raw, target = 'some text', '<del>some text</del>'
        self._test_token(span_token.Strikethrough, raw, target)

    def test_image(self):
        raw = '![alt](src "title")'
        target = '<img src="src" title="title" alt="alt">'
        self._test_token(span_token.Image, raw, target)

    def test_link(self):
        raw, target = '[name](target)', '<a href="target">name</a>'
        self._test_token(span_token.Link, raw, target)

    def test_escape_sequence(self):
        raw, target = '\*', '\*'
        self._test_token(span_token.EscapeSequence, raw, target)

    def test_raw_text(self):
        raw, target = 'john & jane', 'john &amp; jane'
        self._test_token(span_token.RawText, raw, target)
