from unittest import TestCase, mock
from mistletoe.span_token import tokenize_inner, _token_types
from mistletoe.block_token import tokenize
from mistletoe import html_token
from mistletoe.html_renderer import HTMLRenderer

class TestHTMLToken(TestCase):
    def setUp(self):
        self.renderer = HTMLRenderer()
        self.renderer.__enter__()
        self.addCleanup(self.renderer.__exit__, None, None, None)

    def _test_html_token(self, token, token_cls, content):
        self.assertIsInstance(token, token_cls)
        self.assertEqual(token.content, content)

    def test_span(self):
        raw = 'some <span>more</span> text'
        tokens = tokenize_inner(raw)
        next(tokens)
        content = '<span>more</span>'
        self._test_html_token(next(tokens), html_token.HTMLSpan, content)
        next(tokens)

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

    def test_comment(self):
        from mistletoe.block_token import Heading
        lines = ['<!-- hello -->\n', '\n', '# heading 1\n']
        token1, token2 = tokenize(lines)
        content = '<!-- hello -->\n'
        self._test_html_token(token1, html_token.HTMLBlock, content)
        self.assertIsInstance(token2, Heading)

    def test_empty_span(self):
        raw = '<span></span>'
        token = next(tokenize_inner(raw))
        content = '<span></span>'
        self._test_html_token(token, html_token.HTMLSpan, content)

    def test_self_closing_span(self):
        raw = '<span />'
        token = next(tokenize_inner(raw))
        content = '<span />'
        self._test_html_token(token, html_token.HTMLSpan, content)

    def test_autolink(self):
        from mistletoe.span_token import AutoLink
        self.assertIsInstance(next(tokenize_inner('<autolink>')), AutoLink)

