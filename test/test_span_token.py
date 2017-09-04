import unittest
from unittest.mock import patch
import mistletoe.span_token as span_token


class TestBranchToken(unittest.TestCase):
    def setUp(self):
        patcher = patch('mistletoe.span_token.RawText')
        self.mock = patcher.start()
        self.addCleanup(patcher.stop)

    def _test_parse(self, token_cls, raw, arg, **kwargs):
        token = next(span_token.tokenize_inner(raw))
        self.assertIsInstance(token, token_cls)
        self._test_token(token, arg, **kwargs)

    def _test_token(self, token, arg, children=True, **kwargs):
        for attr, value in kwargs.items():
            self.assertEqual(getattr(token, attr), value)
        if children:
            next(iter(token.children))
        self.mock.assert_called_with(arg)


class TestStrong(TestBranchToken):
    def test_parse(self):
        self._test_parse(span_token.Strong, '**some text**', 'some text')
        self._test_parse(span_token.Strong, '__some text__', 'some text')


class TestEmphasis(TestBranchToken):
    def test_parse(self):
        self._test_parse(span_token.Emphasis, '*some text*', 'some text')
        self._test_parse(span_token.Emphasis, '_some text_', 'some text')


class TestInlineCode(TestBranchToken):
    def test_parse(self):
        self._test_parse(span_token.InlineCode, '`some text`', 'some text')


class TestStrikethrough(TestBranchToken):
    def test_parse(self):
        self._test_parse(span_token.Strikethrough, '~~some text~~', 'some text')


class TestLink(TestBranchToken):
    def test_parse(self):
        self._test_parse(span_token.Link, '[name 1] (target 1)', 'name 1',
                         target='target 1')

    def test_parse_multi_links(self):
        tokens = span_token.tokenize_inner('[n1](t1) & [n2](t2)')
        self._test_token(next(tokens), 'n1', target='t1')
        self._test_token(next(tokens), ' & ', children=False)
        self._test_token(next(tokens), 'n2', target='t2')

    def test_parse_children(self):
        token = next(span_token.tokenize_inner('[![alt](src)](target)'))
        child = next(token.children)
        self._test_token(child, 'alt', src='src')


class TestFootnoteLink(TestBranchToken):
    def test_parse_with_key(self):
        with patch('mistletoe.span_token.FootnoteAnchor') as mock:
            self._test_parse(span_token.FootnoteLink, '[alt] [key]', 'alt')
            mock.assert_called_with('key')

    def test_parse_without_key(self):
        with patch('mistletoe.span_token.FootnoteAnchor') as mock:
            self._test_parse(span_token.FootnoteLink, '[alt]', 'alt')
            mock.assert_called_with('alt')


class TestAutoLink(TestBranchToken):
    def test_parse(self):
        self._test_parse(span_token.AutoLink, '<link>', 'link', target='link')


class TestImage(TestBranchToken):
    def test_parse(self):
        self._test_parse(span_token.Image, '![alt] (link)', 'alt', src='link')
        self._test_parse(span_token.Image, '![alt] (link "title")', 'alt',
                         src='link', title='title')


class TestFootnoteImage(TestBranchToken):
    def test_parse(self):
        with patch('mistletoe.span_token.FootnoteAnchor') as mock:
            self._test_parse(span_token.FootnoteImage, '![alt] [key]', 'alt')
            mock.assert_called_with('key')


class TestEscapeSequence(TestBranchToken):
    def test_parse(self):
        self._test_parse(span_token.EscapeSequence, '\*', '*')

    def test_parse_in_text(self):
        tokens = span_token.tokenize_inner('some \*text*')
        self._test_token(next(tokens), 'some ', children=False)
        self._test_token(next(tokens), '*')
        self._test_token(next(tokens), 'text*', children=False)


class TestRawText(unittest.TestCase):
    def test_attribute(self):
        token = span_token.RawText('some text')
        self.assertEqual(token.content, 'some text')
