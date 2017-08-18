from unittest import TestCase, mock
from mistletoe.span_token import tokenize_inner
from mistletoe.block_token import tokenize
import mistletoe.html_token as html_token
from mistletoe.html_renderer import HTMLRenderer

class TestHTMLToken(TestCase):
    def setUp(self):
        self.renderer = HTMLRenderer()
        self.renderer.__enter__()
        self.addCleanup(self.renderer.__exit__, None, None, None)

    def _test_html_token(self, token, token_cls, content):
        self.assertIsInstance(token, token_cls)
        self.assertEqual(token.content, content)

    @mock.patch('mistletoe.span_token.RawText')
    def test_span(self, MockRawText):
        raw = 'some <span>more</span> text'
        tokens = tokenize_inner(raw)
        next(tokens)
        MockRawText.assert_called_with('some ')
        content = '<span>more</span>'
        self._test_html_token(next(tokens), html_token.HTMLSpan, content)
        next(tokens)
        MockRawText.assert_called_with(' text')

    def test_block(self):
        lines = ['<p>a paragraph\n',
                 'within an html block\n',
                 '</p>\n']
        token = next(tokenize(lines))
        content = '<p>a paragraph\nwithin an html block\n</p>\n'
        self._test_html_token(token, html_token.HTMLBlock, content)

    def test_span_attrs(self):
        raw = '<span class="foo">more</span>'
        token = next(tokenize_inner(raw))
        content = '<span class="foo">more</span>'
        self._test_html_token(token, html_token.HTMLSpan, content)

    def test_block_attrs(self):
        lines = ['<p class="bar">a paragraph\n',
                 'within an html block\n',
                 '</p>\n']
        token = next(tokenize(lines))
        content = '<p class="bar">a paragraph\nwithin an html block\n</p>\n'
        self._test_html_token(token, html_token.HTMLBlock, content)
