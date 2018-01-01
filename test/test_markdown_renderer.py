from unittest import TestCase
from mistletoe.markdown_renderer import MarkdownRenderer
from mistletoe import block_token, span_token


class TestMarkdownRenderer(TestCase):
    def setUp(self):
        self.renderer = MarkdownRenderer()
        self.renderer.__enter__()
        self.addCleanup(self.renderer.__exit__, None, None, None)

    def test_render_raw_text(self):
        token = next(span_token.tokenize_inner('some *emphasis*'))
        self.assertIsInstance(token, span_token.RawText)
        self.assertEqual('some *emphasis*', self.renderer.render(token))

    def test_render_paragraph(self):
        lines = ['# this is a heading\n', '\n', 'a paragraph\n']
        token = next(block_token.tokenize(lines))
        self.assertIsInstance(token, block_token.Paragraph)
        self.assertEqual('# this is a heading\n\n', self.renderer.render(token))

    def test_document(self):
        lines = ['# this is a heading\n', '\n', 'a paragraph\n']
        token = block_token.Document(lines)
        self.assertEqual(''.join(lines) + '\n', self.renderer.render(token))

    def test_render_list(self):
        lines = ['- item 1\n',
                 '- item 2\n',
                 '    - nested item 1\n',
                 '    - nested item 2\n',
                 '- item 3\n']
        output = self.renderer.render(block_token.Document(lines))
        self.assertEqual(''.join(lines) + '\n', output)
