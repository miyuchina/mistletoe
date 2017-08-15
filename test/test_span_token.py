import unittest
import mistletoe.span_token as span_token


class TestStrong(unittest.TestCase):
    def test_parse_asterisk(self):
        token = next(span_token.tokenize_inner('**some text**'))
        self.assertIsInstance(token, span_token.Strong)
        self.assertEqual(token._raw, '**some text**')

    def test_parse_underscore(self):
        token = next(span_token.tokenize_inner('__some text__'))
        self.assertIsInstance(token, span_token.Strong)
        self.assertEqual(token._raw, '__some text__')


class TestEmphasis(unittest.TestCase):
    def test_parse_asterisk(self):
        token = next(span_token.tokenize_inner('*some text*'))
        self.assertIsInstance(token, span_token.Emphasis)
        self.assertEqual(token._raw, '*some text*')

    def test_parse_underscore(self):
        token = next(span_token.tokenize_inner('_some text_'))
        self.assertIsInstance(token, span_token.Emphasis)
        self.assertEqual(token._raw, '_some text_')


class TestInlineCode(unittest.TestCase):
    def test_parse(self):
        token = next(span_token.tokenize_inner('`some code`'))
        self.assertIsInstance(token, span_token.InlineCode)
        self.assertEqual(token._raw, '`some code`')

    def test_children(self):
        token = next(span_token.tokenize_inner('`some code`'))
        child = next(token.children)
        self.assertIsInstance(child, span_token.RawText)
        self.assertEqual(child.content, 'some code')


class TestStrikethrough(unittest.TestCase):
    def test_parse(self):
        token = next(span_token.tokenize_inner('~~some code~~'))
        self.assertIsInstance(token, span_token.Strikethrough)
        self.assertEqual(token._raw, '~~some code~~')


class TestLink(unittest.TestCase):
    def test_parse(self):
        token = next(span_token.tokenize_inner('[name 1] (target 1)'))
        self.assertIsInstance(token, span_token.Link)
        self.assertEqual(token._raw, '[name 1] (target 1)')
        self.assertEqual(token.target, 'target 1')

    def test_parse_multi_links(self):
        tokens = span_token.tokenize_inner('[n1](t1) & [n2](t2)')

        token1 = next(tokens)
        self.assertIsInstance(token1, span_token.Link)
        self.assertEqual(token1._raw, '[n1](t1)')

        token2 = next(tokens)
        self.assertIsInstance(token2, span_token.RawText)
        self.assertEqual(token2.content, ' & ')

        token3 = next(tokens)
        self.assertIsInstance(token3, span_token.Link)
        self.assertEqual(token3._raw, '[n2](t2)')

    def test_children(self):
        token = next(span_token.tokenize_inner('[![alt](src)](target)'))
        child = next(token.children)
        self.assertIsInstance(child, span_token.Image)
        self.assertEqual(child._raw, '![alt](src)')


class TestFootnoteLink(unittest.TestCase):
    def test_parse(self):
        token = next(span_token.tokenize_inner('[alt] [key]'))
        self.assertIsInstance(token, span_token.FootnoteLink)
        self.assertEqual(token._raw, '[alt] [key]')

    def test_footnote_anchor(self):
        token = next(span_token.tokenize_inner('[alt] [key]')).target
        self.assertIsInstance(token, span_token.FootnoteAnchor)
        self.assertEqual(token.key, 'key')


class TestAutoLink(unittest.TestCase):
    def test_parse(self):
        token = next(span_token.tokenize_inner('<link>'))
        self.assertIsInstance(token, span_token.AutoLink)
        self.assertEqual(token._raw, '<link>')
        self.assertEqual(token.name, 'link')
        self.assertEqual(token.target, 'link')


class TestImage(unittest.TestCase):
    def test_parse_without_title(self):
        token = next(span_token.tokenize_inner('![alt] (link)'))
        self.assertIsInstance(token, span_token.Image)
        self.assertEqual(token._raw, '![alt] (link)')
        self.assertEqual(token.alt, 'alt')
        self.assertEqual(token.src, 'link')
        self.assertIsNone(token.title)

    def test_parse_with_title(self):
        token = next(span_token.tokenize_inner('![alt] (link "title")'))
        self.assertEqual(token.title, 'title')


class TestFootnoteImage(unittest.TestCase):
    def test_parse(self):
        token = next(span_token.tokenize_inner('![alt] [key]'))
        self.assertIsInstance(token, span_token.FootnoteImage)
        self.assertEqual(token._raw, '![alt] [key]')
        self.assertEqual(token.alt, 'alt')

    def test_footnote_anchor(self):
        token = next(span_token.tokenize_inner('![alt] [key]')).src
        self.assertIsInstance(token, span_token.FootnoteAnchor)
        self.assertEqual(token.key, 'key')


class TestEscapeSequence(unittest.TestCase):
    def test_parse(self):
        token = next(span_token.tokenize_inner('\*'))
        self.assertIsInstance(token, span_token.EscapeSequence)
        self.assertEqual(token.content, '*')

    def test_parse_in_text(self):
        tokens = span_token.tokenize_inner('some \*text*')

        token1 = next(tokens)
        self.assertIsInstance(token1, span_token.RawText)
        self.assertEqual(token1.content, 'some ')

        token2 = next(tokens)
        self.assertIsInstance(token2, span_token.EscapeSequence)
        self.assertEqual(token2.content, '*')

        token3 = next(tokens)
        self.assertIsInstance(token3, span_token.RawText)
        self.assertEqual(token3.content, 'text*')


class TestRawText(unittest.TestCase):
    def test_attribute(self):
        token = span_token.RawText('some text')
        self.assertEqual(token.content, 'some text')
