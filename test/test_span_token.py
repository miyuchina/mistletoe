import unittest
from unittest.mock import patch
from mistletoe import span_token


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
        return token

    def _test_token(self, token, arg, children=True, **kwargs):
        for attr, value in kwargs.items():
            self.assertEqual(getattr(token, attr), value)
        if children:
            self.mock.assert_any_call(arg)


class TestStrong(TestBranchToken):
    def test_parse(self):
        self._test_parse(span_token.Strong, '**some text**', 'some text')
        self._test_parse(span_token.Strong, '__some text__', 'some text')

    def test_strong_when_both_delimiter_run_lengths_are_multiples_of_3(self):
        tokens = iter(span_token.tokenize_inner('foo******bar*********baz'))
        self._test_token(next(tokens), 'foo', children=False)
        self._test_token(next(tokens), 'bar', children=True)
        self._test_token(next(tokens), '***baz', children=False)


class TestEmphasis(TestBranchToken):
    def test_parse(self):
        self._test_parse(span_token.Emphasis, '*some text*', 'some text')
        self._test_parse(span_token.Emphasis, '_some text_', 'some text')

    def test_emphasis_with_straight_quote(self):
        tokens = iter(span_token.tokenize_inner('_Book Title_\'s author'))
        self._test_token(next(tokens), 'Book Title', children=True)
        self._test_token(next(tokens), '\'s author', children=False)

    def test_emphasis_with_smart_quote(self):
        tokens = iter(span_token.tokenize_inner('_Book Title_’s author'))
        self._test_token(next(tokens), 'Book Title', children=True)
        self._test_token(next(tokens), '’s author', children=False)

    def test_no_emphasis_for_underscore_without_punctuation(self):
        tokens = iter(span_token.tokenize_inner('_an example without_punctuation'))
        self._test_token(next(tokens), '_an example without_punctuation', children=True)

    def test_emphasis_for_asterisk_without_punctuation(self):
        tokens = iter(span_token.tokenize_inner('*an example without*punctuation'))
        self._test_token(next(tokens), 'an example without', children=True)
        self._test_token(next(tokens), 'punctuation', children=False)


class TestInlineCode(TestBranchToken):
    def _test_parse_enclosed(self, encl_type, encl_delimiter):
        token = self._test_parse(encl_type, '{delim}`some text`{delim}'.format(delim=encl_delimiter), 'some text')
        self.assertEqual(len(token.children), 1)
        self.assertIsInstance(token.children[0], span_token.InlineCode)

    def test_parse(self):
        self._test_parse(span_token.InlineCode, '`some text`', 'some text')

    def test_parse_in_bold(self):
        self._test_parse_enclosed(span_token.Strong, '**')
        self._test_parse_enclosed(span_token.Strong, '__')

    def test_parse_in_emphasis(self):
        self._test_parse_enclosed(span_token.Emphasis, '*')
        self._test_parse_enclosed(span_token.Emphasis, '_')

    def test_parse_in_strikethrough(self):
        self._test_parse_enclosed(span_token.Strikethrough, '~~')

    def test_remove_space_if_present_on_both_sides(self):
        self._test_parse(span_token.InlineCode, '``` ```', ' ')
        self._test_parse(span_token.InlineCode, '`  ``  `', ' `` ')

    def test_preserve_escapes(self):
        self._test_parse(span_token.InlineCode, '`\\xa0b\\xa0`', '\\xa0b\\xa0')
        self._test_parse(span_token.InlineCode, '``\\`\\[``', '\\`\\[')


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

    def test_parse_angle_bracketed_inline_link_with_space(self):
        self._test_parse(span_token.Link, '[link](</my uri> \'a title\')',
            'link', target='/my uri', title='a title')


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
        self._test_parse(span_token.EscapeSequence, r'\*', '*')

    def test_parse_in_text(self):
        tokens = iter(span_token.tokenize_inner(r'some \*text*'))
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

    def test_valid_html_entities(self):
        tokens = span_token.tokenize_inner('&nbsp; &#21512;')
        self.assertEqual(tokens[0].content, '\xa0 \u5408')

    def test_invalid_html_entities(self):
        text = '&nbsp &x; &#; &#x; &#87654321; &#abcdef0; &ThisIsNotDefined; &hi?;'
        tokens = span_token.tokenize_inner(text)
        self.assertEqual(tokens[0].content, text)


class TestLineBreak(unittest.TestCase):
    def test_parse_soft_break(self):
        token, = span_token.tokenize_inner('\n')
        self.assertIsInstance(token, span_token.LineBreak)
        self.assertTrue(token.soft)

    def test_parse_hard_break_with_double_blanks(self):
        token, = span_token.tokenize_inner('  \n')
        self.assertIsInstance(token, span_token.LineBreak)
        self.assertFalse(token.soft)

    def test_parse_hard_break_with_backslash(self):
        _, token, = span_token.tokenize_inner(' \\\n')
        self.assertIsInstance(token, span_token.LineBreak)
        self.assertFalse(token.soft)


class TestContains(unittest.TestCase):
    def test_contains(self):
        token = next(iter(span_token.tokenize_inner('**with some *emphasis* text**')))
        self.assertTrue('text' in token)
        self.assertTrue('emphasis' in token)
        self.assertFalse('foo' in token)


class TestHtmlSpan(unittest.TestCase):
    def setUp(self):
        span_token.add_token(span_token.HtmlSpan)
        self.addCleanup(span_token.reset_tokens)

    def test_parse(self):
        tokens = span_token.tokenize_inner('<a>')
        self.assertIsInstance(tokens[0], span_token.HtmlSpan)
        self.assertEqual('<a>', tokens[0].content)

    def test_parse_with_illegal_whitespace(self):
        tokens = span_token.tokenize_inner('< a><\nfoo><bar/ >\n<foo bar=baz\nbim!bop />')
        for t in tokens:
            self.assertNotIsInstance(t, span_token.HtmlSpan)
