import unittest
from unittest.mock import patch
from mistletoe import span_token
from functools import wraps


class TestBranchToken(unittest.TestCase):
    def setUp(self):
        self.addCleanup(lambda: span_token._token_types.__setitem__(-1, span_token.RawText))
        patcher = patch('mistletoe.span_token.RawText')
        self.mock = patcher.start()
        span_token._token_types[-1] = self.mock
        self.addCleanup(patcher.stop)

    def _test_parse(self, token_cls, raw, arg, **kwargs):
        token = next(iter(span_token.tokenize_inner(raw)))
        self.assertIsInstance(token, token_cls)
        self._test_token(token, arg, **kwargs)

    def _test_token(self, token, arg, children=True, **kwargs):
        for attr, value in kwargs.items():
            self.assertEqual(getattr(token, attr), value)
        if children:
            self.mock.assert_any_call(arg)


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

    def test_parse_multiple(self):
        tokens = iter(span_token.tokenize_inner('~~one~~ ~~two~~'))
        self._test_token(next(tokens), 'one')
        self._test_token(next(tokens), 'two')


class TestLink(TestBranchToken):
    def test_parse(self):
        self._test_parse(span_token.Link, '[name 1](target1)', 'name 1',
                         target='target1', title='')

    def test_parse_multi_links(self):
        tokens = iter(span_token.tokenize_inner('[n1](t1) & [n2](t2)'))
        self._test_token(next(tokens), 'n1', target='t1')
        self._test_token(next(tokens), ' & ', children=False)
        self._test_token(next(tokens), 'n2', target='t2')

    def test_parse_children(self):
        token = next(iter(span_token.tokenize_inner('[![alt](src)](target)')))
        child = next(iter(token.children))
        self._test_token(child, 'alt', src='src')


class TestAutoLink(TestBranchToken):
    def test_parse(self):
        self._test_parse(span_token.AutoLink, '<ftp://foo.com>', 'ftp://foo.com', target='ftp://foo.com')


class TestImage(TestBranchToken):
    def test_parse(self):
        self._test_parse(span_token.Image, '![alt](link)', 'alt', src='link')
        self._test_parse(span_token.Image, '![alt](link "title")', 'alt',
                         src='link', title='title')

    def test_no_alternative_text(self):
        self._test_parse(span_token.Image, '![](link)', '', children=False, src='link')


class TestEscapeSequence(TestBranchToken):
    def test_parse(self):
        self._test_parse(span_token.EscapeSequence, '\*', '*')

    def test_parse_in_text(self):
        tokens = iter(span_token.tokenize_inner('some \*text*'))
        self._test_token(next(tokens), 'some ', children=False)
        self._test_token(next(tokens), '*')
        self._test_token(next(tokens), 'text*', children=False)


class TestRawText(unittest.TestCase):
    def test_attribute(self):
        token = span_token.RawText('some text')
        self.assertEqual(token.content, 'some text')

    def test_no_children(self):
        token = span_token.RawText('some text')
        with self.assertRaises(AttributeError):
            token.children


class TestLineBreak(unittest.TestCase):
    def test_parse(self):
        token, = span_token.tokenize_inner('  \n')
        self.assertIsInstance(token, span_token.LineBreak)


class TestContains(unittest.TestCase):
    def test_contains(self):
        token = next(iter(span_token.tokenize_inner('**with some *emphasis* text**')))
        self.assertTrue('text' in token)
        self.assertTrue('emphasis' in token)
        self.assertFalse('foo' in token)

