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

    def test_heading(self):
        raw, target = [ '### heading 3\n' ], '<h3>heading 3</h3>'
        self._test_token(block_token.Heading, raw, target)

    def test_quote(self):
        raw = ['> ## heading 2\n', '> a paragraph\n', '> continued\n']
        target = ('<blockquote><h2>heading 2</h2>'
                  '<p>a paragraph continued</p></blockquote>')
        self._test_token(block_token.Quote, raw, target)

    def test_block_code(self):
        raw = ['```sh\n', 'mkdir temp\n', 'rmdir temp\n', '```\n']
        target = ('<pre><code class="lang-sh">mkdir temp\n'
                  'rmdir temp\n</code></pre>')
        self._test_token(block_token.BlockCode, raw, target)

    def test_list(self):
        raw = ['- item 1\n',
               '- item 2\n',
               '    2. nested item 1\n',
               '    3. nested item 2\n',
               '        * further nested\n',
               '- item 3\n']
        target = ('<ul>'
                    '<li>item 1</li>'
                    '<li>item 2</li>'
                    '<ol start="2">'
                      '<li>nested item 1</li>'
                      '<li>nested item 2</li>'
                      '<ul><li>further nested</li></ul>'
                    '</ol>'
                    '<li>item 3</li>'
                  '</ul>')
        self._test_token(block_token.List, raw, target)

    def test_list_item(self):
        raw = '    - some **bold** text\n'
        target = '<li>some <strong>bold</strong> text</li>'
        self._test_token(block_token.ListItem, raw, target)

    def test_separator(self):
        raw, target = '***\n', '<hr>'
        self._test_token(block_token.Separator, raw, target)

    def test_document(self):
        raw = ['a paragraph\n']
        target = '<html><body><p>a paragraph</p></body></html>'
        self._test_token(block_token.Document, raw, target)
